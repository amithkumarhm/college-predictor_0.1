# College Predictor

An AI-powered web application that predicts suitable colleges for MCA, MBA, and MTech programs in Karnataka based on PGCET ranks.

## Features

- **AI-Powered Predictions**: Machine learning model trained on historical cutoff data
- **Multiple College Types**: Support for MCA, MBA, and MTech programs
- **Smart Filtering**: Filter by location, category, and exam type
- **Interactive Chatbot**: Guided prediction process through chatbot
- **User Authentication**: Secure login and registration system
- **Prediction History**: Track your previous predictions
- **Responsive Design**: Modern UI that works on all devices

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **ML Model**: Scikit-learn Random Forest
- **Deployment**: Docker, Render

## Installation
create python env python-3.9.16

python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python database/init_db.py
python model_training.py

Render Build Command:
pip install --upgrade pip && pip install -r requirements.txt && python database/init_db.py && python model_training.py