#!/bin/bash

echo "Starting deployment process..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python database/init_db.py

# Train model
echo "Training ML model..."
python model_training.py

echo "Deployment setup completed!"
echo "To run the application: python app.py"
echo "Access at: http://localhost:5000"