#!/usr/bin/python3

from . import create_app
from .extensions import db
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
import os
from .models import *

app = create_app()
oauth = OAuth(app)
CORS(app, resources={r"/*": {"origins": "*"}})

host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('HBNB_API_PORT', 5000)

with app.app_context():
    db.create_all()  # This creates all the tables defined in your models.

@app.teardown_appcontext
def teardown_db(exception):
    """close database connection after session"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """return 404 error on page not found"""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(host, port)
