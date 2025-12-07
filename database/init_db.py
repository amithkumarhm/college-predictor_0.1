import sqlite3
import pandas as pd
import os


def init_database():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    conn = sqlite3.connect('database/college_data.db')
    cursor = conn.cursor()

    # Create users table
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
    datasets = {
        'mtech': 'datasets/mtech_colleges_data.csv',
        'mca': 'datasets/mca_colleges_data.csv',
        'mba': 'datasets/mba_colleges_data.csv'
    }

    for college_type, file_path in datasets.items():
        if os.path.exists(file_path):
            print(f"Loading {file_path}...")
            df = pd.read_csv(file_path)

            # Clean column names (remove any extra spaces)
            df.columns = df.columns.str.strip()

            # Create table for each college type (without _colleges suffix)
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

            # Insert data
            try:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Successfully loaded {len(df)} records into {table_name}")
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
        else:
            print(f"Warning: File {file_path} not found")

    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:", [table[0] for table in tables])

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()