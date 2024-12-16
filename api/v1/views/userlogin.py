#!/usr/bin/python3

from flask import jsonify, request, session
from models import storage
from models.registration import Registration
from models.logout import TokenBlacklist
from api.v1.views import app_views
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jti
from ..services.jwt_service import create_jwt_token
from os import getenv
from api.v1.extensions import jwt

Session = storage._DBStorage__session


@app_views.route("/login", methods=["POST"],
                 strict_slashes=False, endpoint='login_user')
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Missing data'}), 400

    session = Session()
    user = session.query(Registration).filter_by(email=email).first()
    session.close()

    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_jwt_token(user.id, user.email)
    return jsonify({'token': access_token}), 200

# Logout endpoint
@app_views.route("/logout", methods=["POST"],
                 strict_slashes=False, endpoint='logout')
@jwt_required()
def logout():
    jti = get_jti(request.headers['Authorization'].split(' ')[1])
    #print(jti)
    session = Session()
    blacklist_token = TokenBlacklist(jti=jti)
    storage.new(blacklist_token)
    storage.save()
    session.close()
    return jsonify({'message': 'Successfully logged out'}), 200


# Check if a token is blacklisted 
# part of logout functionality
@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    session = Session()
    token = session.query(TokenBlacklist).filter_by(jti=jti).first()
    session.close()
    return token is not None


