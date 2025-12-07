#!/usr/bin/env python3
"""
Setup script for College Predictor Application
Run this script to initialize the database and train the model
"""

import subprocess
import sys
import os


def run_command(command, description):
    print(f"\n{'=' * 50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('=' * 50)

    try:
        result = subprocess.run(command, shell=True, check=True,
                                capture_output=True, text=True)
        print("SUCCESS:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("FAILED:")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    print("College Predictor Setup Script")
    print("This script will initialize the database and train the ML model.")

    # Check if datasets directory exists and has CSV files
    datasets_dir = 'datasets'
    required_files = ['mtech_colleges_data.csv', 'mca_colleges_data.csv', 'mba_colleges_data.csv']

    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(datasets_dir, file)):
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing required dataset files: {missing_files}")
        print("Please ensure all CSV files are in the 'datasets' directory.")
        return

    print("\n✅ All required dataset files found.")

    # Step 1: Initialize database
    if not run_command("python database/init_db.py", "Initializing database"):
        print("\n❌ Database initialization failed.")
        return

    # Step 2: Train model
    if not run_command("python model_training.py", "Training ML model"):
        print("\n❌ Model training failed.")
        return

    # Step 3: Test the application
    print(f"\n{'=' * 50}")
    print("Setup completed successfully!")
    print("You can now run the application with: python app.py")
    print("Access the application at: http://localhost:5000")
    print('=' * 50)


if __name__ == '__main__':
    main()