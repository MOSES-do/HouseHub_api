#!/usr/bin/python3

from flask_jwt_extended import create_access_token
from api.v1.config import Config
import jwt
from datetime import datetime, timedelta


def create_jwt_token(user_id, user_email):
    # Generate the token; expiration is automatically set by Flask-JWT-Extended
    access_token = create_access_token(identity={'id':user_id, 'email':user_email})
    return access_token

def create_jwt_token_verify_email(user_id, secret_key, expires_in=None):
    if expires_in is None:
        expires_in = Config.JWT_ACCESS_TOKEN_EXPIRES

    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_in
    }
    access_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return access_token
