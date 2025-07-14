import os

# Get the absolute path of the project's root directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """
    Base configuration class. Contains default settings and loads
    any environment variables from the .env file.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_fallback_secret_key'
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    
    # Configurable port, defaulting to 8080 if not set in .env
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT') or 8080

    # --- File Path Configurations ---
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

    # Specific file paths
    AMAZON_PROCESSED_FILE = os.path.join(PROCESSED_DATA_DIR, 'Amazonnew_processed.csv')
    ASDATA_PROCESSED_FILE = os.path.join(PROCESSED_DATA_DIR, 'asdata_processed.csv')
    
    # New Xentral file path
    XENTRAL_PROCESSED_FILE = os.path.join(PROCESSED_DATA_DIR, 'xentral.csv')

