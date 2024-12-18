#!/usr/bin/python3

from flask import Flask, jsonify, make_response
from flask_mail import Mail
from api.v1.extensions import oauth, jwt, cors, mail
from models import storage
from api.v1.views import app_views
import os

def create_app(config_class='api.config.DevelopmentConfig'):
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)

    # Load app configuration
    app.config.from_object(config_class)

    # Initialize extensions with app
    oauth.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(app_views)

    # App teardown and error handling
    @app.teardown_appcontext
    def teardown_db(exception):
        """Close database connection after session."""
        storage.close()

    @app.errorhandler(404)
    def not_found(error):
        """Return 404 error on page not found."""
        return make_response(jsonify({'error': 'Not found'}), 404)

    return app
