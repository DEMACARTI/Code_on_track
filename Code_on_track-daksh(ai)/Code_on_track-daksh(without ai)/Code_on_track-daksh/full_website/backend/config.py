import os

# Define base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security
SECRET_KEY = 'dev-secret-key'
