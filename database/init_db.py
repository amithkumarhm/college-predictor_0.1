# database/init_db.py - Updated with better error handling
import sqlite3
import pandas as pd
import os
from pathlib import Path
import sys


def init_database():
    print("🔧 Initializing College Predictor Database...")

    # Get the current directory
    current_dir = Path(__file__).parent.parent
    print(f"Current directory: {current_dir}")

    # Ensure database directory exists
    database_dir = current_dir / 'database'
    database_dir.mkdir(exist_ok=True)
    print(f"Database directory: {database_dir}")

    # Database path
    db_path = database_dir / 'college_data.db'
    print(f"Database path: {db_path}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    print("📝 Creating users table...")
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       email
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Create predictions history table
    print("📝 Creating predictions table...")
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS predictions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       exam_type
                       TEXT,
                       college_type
                       TEXT,
                       category
                       TEXT,
                       place
                       TEXT,
                       rank
                       INTEGER,
                       prediction_result
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   )
                       )
                   ''')

    # Load and insert college data
    datasets_dir = current_dir / 'datasets'
    print(f"Datasets directory: {datasets_dir}")

    datasets = {
        'mtech': 'mtech_colleges_data.csv',
        'mca': 'mca_colleges_data.csv',
        'mba': 'mba_colleges_data.csv'
    }

    total_records = 0

    for college_type, file_name in datasets.items():
        file_path = datasets_dir / file_name
        print(f"\n📂 Processing {file_name}...")

        if file_path.exists():
            try:
                # Read CSV file
                print(f"Reading CSV file: {file_path}")
                df = pd.read_csv(file_path)

                # Clean column names (remove any extra spaces)
                df.columns = df.columns.str.strip()
                print(f"Columns found: {list(df.columns)}")

                # Create table for each college type
                table_name = f"{college_type}_colleges"
                print(f"Creating/checking table: {table_name}")

                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        serial_no INTEGER,
                        college_id TEXT,
                        college_name TEXT,
                        college_type TEXT,
                        state TEXT,
                        place TEXT,
                        exam_type TEXT,
                        category TEXT,
                        opening_cutoff_rank INTEGER,
                        closing_cutoff_rank INTEGER,
                        seats INTEGER,
                        year INTEGER,
                        website TEXT,
                        background_images TEXT,
                        PRIMARY KEY (college_id, category, year)
                    )
                ''')

                # Insert data
                try:
                    # Drop table if exists to replace data
                    cursor.execute(f'DROP TABLE IF EXISTS {table_name}_temp')

                    # Create temp table with proper schema
                    cursor.execute(f'''
                        CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name} WHERE 1=0
                    ''')

                    # Insert data into temp table
                    df.to_sql(f'{table_name}_temp', conn, if_exists='replace', index=False)

                    # Copy data from temp to main table
                    cursor.execute(f'INSERT OR REPLACE INTO {table_name} SELECT * FROM {table_name}_temp')

                    # Drop temp table
                    cursor.execute(f'DROP TABLE {table_name}_temp')

                    count = len(df)
                    total_records += count
                    print(f"✅ Successfully loaded {count} records into {table_name}")

                    # Show sample data
                    print(f"Sample data from {table_name}:")
                    sample = df.head(3)
                    for _, row in sample.iterrows():
                        print(f"  - {row.get('college_name', 'Unknown')} ({row.get('place', 'Unknown')})")

                except Exception as e:
                    print(f"❌ Error inserting data into {table_name}: {e}")
                    # Try alternative method
                    try:
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        count = len(df)
                        total_records += count
                        print(f"✅ Alternative method loaded {count} records into {table_name}")
                    except Exception as e2:
                        print(f"❌ Alternative method also failed: {e2}")

            except Exception as e:
                print(f"❌ Error loading {file_name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  Warning: File {file_path} not found")
            print(f"   Creating empty table for {college_type}...")

            table_name = f"{college_type}_colleges"
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    serial_no INTEGER,
                    college_id TEXT,
                    college_name TEXT,
                    college_type TEXT,
                    state TEXT,
                    place TEXT,
                    exam_type TEXT,
                    category TEXT,
                    opening_cutoff_rank INTEGER,
                    closing_cutoff_rank INTEGER,
                    seats INTEGER,
                    year INTEGER,
                    website TEXT,
                    background_images TEXT,
                    PRIMARY KEY (college_id, category, year)
                )
            ''')

    # Verify tables were created
    print("\n📊 Verifying database structure...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")

    # Show record counts
    print("\n📈 Record counts:")
    for college_type in datasets.keys():
        table_name = f"{college_type}_colleges"
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")
        except:
            print(f"  - {table_name}: 0 records (table may not exist)")

    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully!")
    print(f"   Total records loaded: {total_records}")
    print(f"   Database file: {db_path}")

    # Print next steps
    print("\n📋 Next steps:")
    print("   1. Run 'python model_training.py' to train the ML model")
    print("   2. Run 'python app.py' to start the web application")
    print("   3. Access the app at http://localhost:5000")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)