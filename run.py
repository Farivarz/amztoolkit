from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from the .env file in the project root
# This makes variables like FLASK_APP and SECRET_KEY available to the app
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Create an instance of the Flask application using the factory function
app = create_app()

if __name__ == '__main__':
    # This block runs the application server.
    # It now gets the port from the application's configuration.
    # We've also added host='0.0.0.0' which can help bypass permission issues.
    port = app.config.get('FLASK_RUN_PORT')
    app.run(debug=True, host='0.0.0.0', port=port)
