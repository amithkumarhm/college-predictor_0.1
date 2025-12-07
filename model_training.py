import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
import joblib
import sqlite3
import os


def train_model():
    print("Starting model training...")

    # Check if database exists
    if not os.path.exists('database/college_data.db'):
        print("Database not found. Please run init_db.py first.")
        return

    # Load data from database
    conn = sqlite3.connect('database/college_data.db')

    # Check if tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    print("Available tables:", tables)

    dfs = []
    college_types = ['mtech', 'mba', 'mca']

    for college_type in college_types:
        table_name = f"{college_type}_colleges"
        if table_name in tables:
            print(f"Loading data from {table_name}...")
            try:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                # Add college type if not present
                if 'college_type' not in df.columns:
                    df['college_type'] = college_type.upper()
                dfs.append(df)
                print(f"Loaded {len(df)} records from {table_name}")
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
        else:
            print(f"Table {table_name} not found")

    if not dfs:
        print("No data found in database. Please check your CSV files.")
        conn.close()
        return

    # Combine all data
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total records loaded: {len(df)}")

    # Check if we have enough data
    if len(df) == 0:
        print("No data available for training.")
        conn.close()
        return

    # Create synthetic training data
    print("Creating synthetic training data...")
    rows = []
    rng = np.random.default_rng(42)

    for _, c in df.iterrows():
        try:
            open_r = int(c['opening_cutoff_rank'])
            close_r = int(c['closing_cutoff_rank'])

            # Skip if cutoffs are invalid
            if open_r <= 0 or close_r <= 0 or open_r > close_r:
                continue

            # Sample positive examples from within cutoff range
            if open_r <= close_r:
                sample_size = min(10, max(1, close_r - open_r + 1))
                pos_samples = rng.integers(open_r, close_r + 1, size=sample_size)
            else:
                pos_samples = rng.integers(close_r, open_r + 1, size=5)

            # Sample negative examples
            neg_before = rng.integers(max(1, open_r - 200), max(1, open_r), size=5)
            neg_after = rng.integers(close_r + 1, close_r + 200, size=5)

            for r in pos_samples:
                rows.append({
                    'user_rank': int(r),
                    'exam_type': c.get('exam_type', 'PGCET'),
                    'category': c.get('category', 'GM'),
                    'place': c.get('place', 'Bangalore'),
                    'opening': open_r,
                    'closing': close_r,
                    'seats': c.get('seats', 0),
                    'label': 1,  # Positive example
                    'college_id': c.get('college_id', '')
                })

            for r in np.concatenate([neg_before, neg_after]):
                rows.append({
                    'user_rank': int(r),
                    'exam_type': c.get('exam_type', 'PGCET'),
                    'category': c.get('category', 'GM'),
                    'place': c.get('place', 'Bangalore'),
                    'opening': open_r,
                    'closing': close_r,
                    'seats': c.get('seats', 0),
                    'label': 0,  # Negative example
                    'college_id': c.get('college_id', '')
                })
        except (ValueError, TypeError) as e:
            print(f"Skipping row due to error: {e}")
            continue

    if not rows:
        print("No valid training data generated.")
        conn.close()
        return

    train_df = pd.DataFrame(rows)
    print(f"Generated {len(train_df)} training samples")

    # Feature engineering
    print("Performing feature engineering...")
    train_df['range_width'] = train_df['closing'] - train_df['opening']
    train_df['rank_vs_open'] = train_df['user_rank'] - train_df['opening']
    train_df['rank_vs_close'] = train_df['user_rank'] - train_df['closing']

    # Prepare features and target
    feature_columns = ['user_rank', 'opening', 'closing', 'range_width',
                       'rank_vs_open', 'rank_vs_close', 'seats', 'exam_type', 'category', 'place']

    # Check if all required columns exist
    missing_cols = [col for col in feature_columns if col not in train_df.columns]
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        # Create missing columns with default values
        for col in missing_cols:
            if col in ['exam_type', 'category', 'place']:
                train_df[col] = 'Unknown'
            else:
                train_df[col] = 0

    X = train_df[feature_columns]
    y = train_df['label']

    print(f"Training data shape: {X.shape}")
    print(f"Positive samples: {sum(y)}")
    print(f"Negative samples: {len(y) - sum(y)}")

    # Preprocessing
    cat_cols = ['exam_type', 'category', 'place']
    num_cols = [c for c in X.columns if c not in cat_cols]

    preprocessor = ColumnTransformer([
        ('num', 'passthrough', num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])

    # Train model with smaller dataset if needed
    print("Training Random Forest model...")
    n_estimators = 100 if len(X) > 10000 else 50

    clf = make_pipeline(preprocessor,
                        RandomForestClassifier(n_estimators=n_estimators,
                                               random_state=42,
                                               max_depth=10))
    clf.fit(X, y)

    # Save model
    joblib.dump(clf, 'model.pkl')
    print("Model trained and saved as model.pkl")

    # Test prediction with sample data
    try:
        sample_input = pd.DataFrame([{
            'user_rank': 1000,
            'opening': 800,
            'closing': 1200,
            'range_width': 400,
            'rank_vs_open': 200,
            'rank_vs_close': -200,
            'seats': 30,
            'exam_type': 'PGCET',
            'category': 'GM',
            'place': 'Bangalore'
        }])

        prediction = clf.predict_proba(sample_input)[0][1]
        print(f"Sample prediction probability: {prediction:.3f}")
    except Exception as e:
        print(f"Sample prediction test failed: {e}")

    conn.close()


if __name__ == '__main__':
    train_model()