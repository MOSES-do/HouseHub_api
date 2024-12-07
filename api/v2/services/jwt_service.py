#!/usr/bin/python3

import datetime
from flask_jwt_extended import create_access_token

def create_jwt_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    access_token = create_access_token(identity={'id': user.id, 'role': user.role, 'exp': expiration})
    
    return access_token

