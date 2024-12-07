#!/usr/bin/python3

from flask import Flask
from .config import Config
from .extensions import db, jwt, login_manager
#from v2.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)           # Bind SQLAlchemy to the app
    jwt.init_app(app)          # Configure JWT for token handling
    login_manager.init_app(app)  # Flask-Login session handling

    # Register routes (blueprints)
    #register_routes(app)

    return app
