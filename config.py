import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
    FIREBASE_CREDENTIALS = "path/to/your/serviceAccountKey.json"
    DEBUG = True
