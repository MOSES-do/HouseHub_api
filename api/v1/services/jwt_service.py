#!/usr/bin/python3

from flask_jwt_extended import create_access_token

def create_jwt_token(user_id, user_email):
    # Generate the token; expiration is automatically set by Flask-JWT-Extended
    access_token = create_access_token(identity={'id':user_id, 'email':user_email})
    return access_token

