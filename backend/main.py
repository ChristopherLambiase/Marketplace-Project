"""Module: main.py - Entry point for the Flask web application"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from requesting import requests_bp
from listings import listings_bp
from user import user_bp
from init_db import init_database

# Initialize database on first run
def initialize_app():
    """Initialize the application and database."""
    db_path = os.path.join(os.path.dirname(__file__), 'marketplace.db')
    if not os.path.exists(db_path):
        print("First run detected - initializing database...")
        init_database()
    else:
        print("Database already exists - skipping initialization")

# Create a new Flask web application instance
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for the app

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, config=swagger_config)

# Register blueprints
app.register_blueprint(requests_bp, url_prefix='/')
app.register_blueprint(listings_bp, url_prefix='/')
app.register_blueprint(user_bp, url_prefix='/')

# Define a URL path; this one responds to the homepage.
@app.route('/')
def home():
    """Handle requests to the root URL ('/').

    Returns:
        jsonify: A JSON response indicating the API is running.
    """
    return jsonify({"message": "Group Project - Market Place API running!"})

# Start the Flask development server when the script is run
if __name__ == "__main__":
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
