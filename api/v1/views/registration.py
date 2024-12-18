#!/usr/bin/python3
"""routes for users"""
from flask import jsonify, request
from models import storage
from models.registration import Registration
from models.logout import TokenBlacklist
from api.v1.views import app_views
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jti
from ..services.jwt_service import create_jwt_token
from os import getenv
from api.v1.extensions import jwt, mail
from api.v1.utils import send_verification_email


Session = storage._DBStorage__session


@app_views.route('/registered_users', methods=['GET'],
                 strict_slashes=False, endpoint='registered_users')
def registered_users():
    """get all registered users from strage"""
    registered_users = []
    s = storage.all(Registration)
    for obj in s.values():
        registered_users.append(obj.to_dict())
    return jsonify(registered_users)


@app_views.route('/reg_users/<user_id>', methods=['GET'],
                 strict_slashes=False, endpoint='single_user')
def single_user(user_id):
    #return user based on id
    #print(user_id)
    s = storage.all(Registration)
    for key, value in s.items():
        if value.id == user_id:
            #print(value.id, user_id)
            return jsonify(value.to_dict())
    abort(404, description="User not found")


# Register endpoint
@app_views.route("/register", methods=["POST"],
                 strict_slashes=False, endpoint='register')
def register():
    """register new user"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400, 'Not a JSON')
    
    email = data.get('email')
    password = data.get('password')
    if not email:
        return jsonify({'error': 'Missing data'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    db = Session()
    if db.query(Registration).filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already exists'}), 401

    # Save new user to database
    new_user = Registration(
                    email=email,
                    )
    new_user.set_password(password)
    storage.new(new_user)
    storage.save()
    send_verification_email(mail, new_user)
    db.close()

    return jsonify({'message': 'Verification email has been sent to {email}'}), 201


# Protected endpoint
@app_views.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    db = Session()
    user = db.query(Registration).get(current_user_id)
    db.close()

    return jsonify({'message': f'Hello, {user.email}!'}), 200


# Function to get current user info
@app_views.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_identity = get_jwt_identity()
    db = Session()
    user = db.query(Registration).filter_by(id=current_user_identity['id']).first()
    if user:
        user_info = {
            'id': user.id,
            'email': user.email
            # Add other fields as needed
        }
        db.close()
        return jsonify(user_info), 200
    else:
        db.close()
        return jsonify({"msg": "User not found"}), 404
