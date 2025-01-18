import os
import secrets  # Add this import

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Generate a secure random key
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    FIREBASE_CREDENTIALS = os.path.join(basedir, "serviceAccountKey.json")
    DEBUG = True
