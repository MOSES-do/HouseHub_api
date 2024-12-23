#!/usr/bin/python3


from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_mail import Mail

# Lazy initialization of extensions
oauth = OAuth()
jwt = JWTManager()
cors = CORS()
mail = Mail()
