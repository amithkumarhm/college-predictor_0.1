from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import joblib
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'

# Fix database path - use absolute path
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database', 'college_data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load ML model
try:
    model = joblib.load('model.pkl')
    print("✅ ML model loaded successfully")
except Exception as e:
    print(f"❌ Error loading ML model: {e}")
    model = None


# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Prediction Logic - IMPROVED with better location matching
def predict_colleges(user_input):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'college_data.db')

    if not os.path.exists(db_path):
        return {'error': 'Database not found'}

    conn = sqlite3.connect(db_path)

    # Base query - use the correct table name
    table_name = f"{user_input['college_type'].lower()}_colleges"

    # Debug: Check what table we're querying
    print(f"Querying table: {table_name}")
    print(f"User input: {user_input}")

    # First check if table exists
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print(f"Table {table_name} does not exist!")
        conn.close()
        return {'exact_matches': [], 'near_matches': [], 'weak_matches': []}

    # Build query based on location preference - IMPROVED
    place = user_input['place'].strip()
    category = user_input['category']
    exam_type = user_input['exam_type']
    state = user_input['state']

    # Normalize place name for comparison
    place_lower = place.lower()

    # Map common variations to database values
    place_mapping = {
        'bangalore': 'Bengaluru',
        'bengaluru': 'Bengaluru',
        'mysore': 'Mysore',
        'mandya': 'Mandya',
        'belagavi': 'Belagavi',
        'dharwad': 'Dharwad',
        'hubballi': 'Hubballi',
        'davanagere': 'Davanagere',
        'mangaluru': 'Mangaluru',
        'hassan': 'Hassan',
        'all': 'All',
        '': 'All'
    }

    # Get normalized place name
    normalized_place = place_mapping.get(place_lower, place)

    if normalized_place == 'All' or normalized_place == '':
        query = f"""
        SELECT * FROM {table_name} 
        WHERE state = ? AND exam_type = ? AND category = ?
        """
        params = [state, exam_type, category]
    else:
        query = f"""
        SELECT * FROM {table_name} 
        WHERE state = ? AND exam_type = ? AND category = ? AND place = ?
        """
        params = [state, exam_type, category, normalized_place]

    print(f"Executing query: {query}")
    print(f"With params: {params}")

    try:
        college_data = pd.read_sql(query, conn, params=params)
        print(f"Found {len(college_data)} colleges for query")

        # Debug: Show first few rows
        if len(college_data) > 0:
            print("Sample colleges found:")
            print(college_data[['college_name', 'place', 'opening_cutoff_rank', 'closing_cutoff_rank']].head())
        else:
            # If no exact match, try case-insensitive search
            if normalized_place != 'All':
                print(f"No exact match for {normalized_place}, trying case-insensitive search...")
                query = f"""
                SELECT * FROM {table_name} 
                WHERE state = ? AND exam_type = ? AND category = ? AND LOWER(place) = ?
                """
                params = [state, exam_type, category, normalized_place.lower()]
                college_data = pd.read_sql(query, conn, params=params)
                print(f"Found {len(college_data)} colleges with case-insensitive search")

    except Exception as e:
        print(f"Database query error: {e}")
        college_data = pd.DataFrame()

    conn.close()

    if college_data.empty:
        print("No colleges found in database query")
        return {'exact_matches': [], 'near_matches': [], 'weak_matches': []}

    user_rank = user_input['rank']
    exact_matches = []

    for _, college in college_data.iterrows():
        try:
            opening = int(college['opening_cutoff_rank'])
            closing = int(college['closing_cutoff_rank'])

            # Debug each college
            print(f"Checking college: {college.get('college_name', 'Unknown')}")
            print(f"  Place: {college.get('place', 'Unknown')}")
            print(f"  Rank range: {opening} - {closing}")
            print(f"  User rank: {user_rank}")

            if opening <= user_rank <= closing:
                print(f"  ✓ Match found!")
                exact_matches.append(college.to_dict())
            else:
                print(f"  ✗ No match (rank {user_rank} outside range {opening}-{closing})")

        except (ValueError, TypeError) as e:
            print(f"Skipping college {college.get('college_name', 'Unknown')} due to error: {e}")
            continue

    print(f"Total exact matches found: {len(exact_matches)}")
    return {
        'exact_matches': exact_matches,
        'near_matches': [],
        'weak_matches': []
    }


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='Registration failed. Please try again.')

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/prediction')
@login_required
def prediction():
    return render_template('prediction.html')


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_input = {
            'exam_type': data.get('exam_type', 'PGCET'),
            'state': data.get('state', 'Karnataka'),
            'place': data.get('place', 'All'),
            'rank': int(data.get('rank', 0)),
            'category': data.get('category', 'GM'),
            'college_type': data.get('college_type', 'MCA')
        }

        # Validate required fields
        if user_input['rank'] <= 0:
            return jsonify({'error': 'Please enter a valid rank'}), 400

        results = predict_colleges(user_input)
        return jsonify(results)

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/results')
@login_required
def results():
    return render_template('results.html')


@app.route('/chatbot_predict', methods=['POST'])
@login_required
def chatbot_predict():
    try:
        data = request.get_json()
        user_input = {
            'exam_type': data.get('exam_type', 'PGCET'),
            'state': data.get('state', 'Karnataka'),
            'place': data.get('place', 'All'),
            'rank': int(data.get('rank', 0)),
            'category': data.get('category', 'GM'),
            'college_type': data.get('college_type', 'MCA')
        }

        results = predict_colleges(user_input)
        return jsonify(results)

    except Exception as e:
        print(f"Chatbot prediction error: {e}")
        return jsonify({'error': 'Prediction failed'}), 500


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Production settings
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")

    print("🚀 Starting College Predictor Application...")
    print(f"📊 Debug mode: {debug_mode}")

    if debug_mode:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # For production use gunicorn
        from werkzeug.serving import run_simple

        run_simple('0.0.0.0', 5000, app, use_reloader=False, use_debugger=False)