#!/usr/bin/python3

from api.v1 import create_app
from models import storage
from api.v1.config import DevelopmentConfig
import os 

host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('HBNB_API_PORT', 5000)

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(host, port)
