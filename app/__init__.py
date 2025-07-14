from flask import Flask
from config.settings import Config

def create_app(config_class=Config):
    """
    Creates and configures an instance of the Flask application.
    This is the application factory pattern.
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Load the configuration from the 'config/settings.py' file
    app.config.from_object(config_class)

    # Import and register the routes from the app.routes module
    # We import it here to avoid circular dependencies.
    with app.app_context():
        from . import routes

    return app
