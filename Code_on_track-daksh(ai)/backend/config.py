import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Use environment variable or default to the user-provided Postgres URI
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:0001@127.0.0.1:5432/qrtrack')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'super-secret-key-for-dev'
