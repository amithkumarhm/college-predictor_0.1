#!/usr/bin/env python3
"""
Setup script for College Predictor Application
Run this script to initialize the database and train the model
"""

import subprocess
import sys
import os
import importlib.util
import shlex
from pathlib import Path


def check_module_installed(module_name):
    """Check if a Python module is installed."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except ImportError:
        return False


def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    print("=" * 50)

    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("⚠️  Warning: Not running in a virtual environment.")
        print("   Consider creating a virtual environment first:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Unix/Mac")
        print("   venv\\Scripts\\activate  # On Windows")

    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                       check=True, capture_output=True)

        # Install requirements
        requirements_file = Path('requirements.txt')
        if not requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False

        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package],
                           check=False, capture_output=True)

        print("✅ All packages installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False


def run_command(command, description, cwd=None, shell=False):
    """Run a command and handle errors."""
    print(f"\n{'=' * 50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('=' * 50)

    try:
        # Use shell=True on Windows for better path handling
        if sys.platform == "win32":
            shell = True

        result = subprocess.run(command, shell=shell, check=True,
                                capture_output=True, text=True,
                                cwd=cwd or os.getcwd())
        print("SUCCESS:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("FAILED:")
        print(f"Error code: {e.returncode}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def run_python_script(script_path, description):
    """Run a Python script directly."""
    print(f"\n{'=' * 50}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print('=' * 50)

    script_path = Path(script_path)
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False

    try:
        # Import the script as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("script_module", script_path)
        module = importlib.util.module_from_spec(spec)

        # Change to script directory temporarily
        original_dir = os.getcwd()
        script_dir = script_path.parent
        os.chdir(script_dir)

        try:
            # Execute the script
            spec.loader.exec_module(module)
            print("✅ Script executed successfully!")
            return True
        finally:
            os.chdir(original_dir)

    except Exception as e:
        print(f"❌ Error running script: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function."""
    print("🚀 College Predictor Setup Script")
    print("=" * 60)
    print("This script will:")
    print("1. Install required packages")
    print("2. Initialize the database")
    print("3. Train the ML model")
    print("=" * 60)

    # Get current directory
    current_dir = Path(__file__).parent
    print(f"\n📁 Current directory: {current_dir}")

    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        return

    # Step 0: Check if datasets directory exists
    datasets_dir = current_dir / 'datasets'
    if not datasets_dir.exists():
        print(f"\n❌ Directory '{datasets_dir}' not found!")
        print("   Please create a 'datasets' directory with your CSV files.")
        print("   Creating datasets directory...")
        datasets_dir.mkdir(exist_ok=True)

        # Create sample CSV files with basic structure
        sample_data = """serial_no,college_id,college_name,college_type,state,place,exam_type,category,opening_cutoff_rank,closing_cutoff_rank,seats,year,website,background_images
1,T001,Sample College 1,MCA,Karnataka,Bengaluru,PGCET,GM,100,500,60,2024,https://example.com,
2,T002,Sample College 2,MCA,Karnataka,Bengaluru,PGCET,GM,501,1000,60,2024,https://example.com,
3,T003,Sample College 3,MBA,Karnataka,Bengaluru,PGCET,GM,100,500,60,2024,https://example.com,
4,T004,Sample College 4,MTECH,Karnataka,Bengaluru,PGCET,GM,100,500,60,2024,https://example.com,"""

        for file_name in ['mca_colleges_data.csv', 'mba_colleges_data.csv', 'mtech_colleges_data.csv']:
            file_path = datasets_dir / file_name
            with open(file_path, 'w') as f:
                f.write(sample_data)
            print(f"   Created sample file: {file_name}")

    # Check if dataset files exist
    required_files = ['mtech_colleges_data.csv', 'mca_colleges_data.csv', 'mba_colleges_data.csv']
    missing_files = []
    for file in required_files:
        file_path = datasets_dir / file
        if not file_path.exists():
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️  Missing dataset files: {missing_files}")
        print("   Using sample data for setup.")
        print("   Please replace with your actual data after setup.")

    # Step 1: Install requirements
    print("\n" + "=" * 50)
    print("Step 1: Installing Requirements")
    print("=" * 50)

    if not install_requirements():
        print("\n❌ Failed to install requirements.")
        print("   You can manually install with: pip install -r requirements.txt")
        return

    # Step 2: Initialize database
    print("\n" + "=" * 50)
    print("Step 2: Initializing Database")
    print("=" * 50)

    # First, check if we can import pandas
    if not check_module_installed('pandas'):
        print("❌ pandas is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pandas"], check=True, capture_output=True)

    if not check_module_installed('pandas'):
        print("❌ Failed to install pandas. Please install manually.")
        return

    # Run init_db.py directly using import method
    init_db_path = current_dir / 'database' / 'init_db.py'
    if not run_python_script(init_db_path, "Initializing database"):
        print("\n⚠️  Database initialization may have issues.")
        print("   You can try running manually with:")
        print(f"   cd \"{current_dir}\"")
        print("   python database\\init_db.py")

        # Try alternative method
        print("\nTrying alternative method...")
        try:
            os.chdir(current_dir)
            exec(open(init_db_path).read())
            print("✅ Database initialized successfully via alternative method!")
        except Exception as e:
            print(f"❌ Alternative method failed: {e}")

    # Step 3: Train model
    print("\n" + "=" * 50)
    print("Step 3: Training ML Model")
    print("=" * 50)

    if not check_module_installed('sklearn'):
        print("❌ scikit-learn is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "scikit-learn"], check=True, capture_output=True)

    # Run model_training.py directly using import method
    model_training_path = current_dir / 'model_training.py'
    if not run_python_script(model_training_path, "Training ML model"):
        print("\n⚠️  Model training may have issues.")
        print("   You can try running manually:")
        print(f"   cd \"{current_dir}\"")
        print("   python model_training.py")
        print("   Or skip this step if you just want to test the database.")

    # Step 4: Create directories if they don't exist
    print("\n" + "=" * 50)
    print("Step 4: Setting Up Directories")
    print("=" * 50)

    directories = ['database', 'static/css', 'static/js', 'static/assets', 'templates']
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

    # Step 5: Test the application
    print("\n" + "=" * 50)
    print("Step 5: Verification")
    print("=" * 50)

    # Check if database was created
    db_path = current_dir / 'database' / 'college_data.db'
    if db_path.exists():
        print(f"✅ Database created: {db_path}")
        size = db_path.stat().st_size
        print(f"   Size: {size:,} bytes")
    else:
        print(f"❌ Database not found at: {db_path}")

    # Check if model was created
    model_path = current_dir / 'model.pkl'
    if model_path.exists():
        print(f"✅ ML model created: {model_path}")
    else:
        print(f"⚠️  ML model not found at: {model_path}")
        print("   The app will run without ML predictions.")

    # Final message
    print("\n" + "=" * 60)
    print("🎉 Setup Completed!")
    print("=" * 60)
    print("\n📊 You can now run the application with:")
    print(f"   cd \"{current_dir}\"")
    print("   python app.py")
    print("\n🌐 Access the application at:")
    print("   http://localhost:5000")
    print("\n🔧 Quick Test:")
    print("   To test if everything works, run:")
    print("   python debug_database.py")
    print("\n🆘 For help or issues:")
    print("   1. Check the README.md file")
    print("   2. Run debug_database.py to check database issues")
    print("   3. Ensure all CSV files have proper format")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        import traceback

        traceback.print_exc()