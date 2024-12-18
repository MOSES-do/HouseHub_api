#!/usr/bin/python3
"""routes for users"""
from flask import Flask, jsonify, request, session, redirect
from models import storage
from models.registration import Registration
from models.logout import TokenBlacklist
from api.v1.views import app_views
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jti
from ..services.jwt_service import create_jwt_token
from os import getenv
from api.v1.extensions import jwt, mail
from api.v1.utils import send_verification_email, send_password_reset_email
from api.v1.config import Config

Session = storage._DBStorage__session
redirect_url = 'https://househubng.netlify.app'

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


@app_views.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    return verify_token_and_perform_action(token, redirect_url=redirect_url)


@app_views.route('/forgot-password', methods=['POST'])
def forgot_password():
    db = Session()
    email = request.json.get('email')
    user = db.query(Registration).filter_by(email=email).first()
    if user:
        send_password_reset_email(mail, user)
        return jsonify({'message': 'Password reset email sent.'})
    return jsonify({'message': 'User not found.'}), 404


@app_views.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    return verify_token_and_perform_action(token, redirect_url=redirect_url)


def verify_token_and_perform_action(token, redirect_url=None):
    db = Session
    try:
        # Decode the token using the provided secret key from the config
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])

        # Determine the request method (GET or POST)
        if request.method == 'GET':
            # Handle email verification
            return handle_email_verification(data, db, redirect_url)
        elif request.method == 'POST':
            # Handle password reset
            return handle_password_reset(data, db, redirect_url, token)
        else:
            return jsonify({'message': 'Invalid request method.'}), 400

    except jwt.ExpiredSignatureError:
        frontend_url = f"{redirect_url}/verify-failure?status=expired"
        return redirect(frontend_url)
        #return jsonify({'message': 'Token expired.'}), 400
    except jwt.InvalidTokenError:
        frontend_url = f"{redirect_url}/verify-failure?status=invalied"
        return redirect(frontend_url)
        #return jsonify({'message': 'Invalid token.'}), 400
    finally:
        db.close()


def handle_email_verification(data, db, redirect_url=None):
    user = db.query(Registration).get(data['user_id'])
    if user and not user.is_verified:
        user.is_verified = True
        db.commit()
        frontend_url = f"{redirect_url}/verify-success?status=success"
        return redirect(frontend_url) if frontend_url else jsonify({'message': 'Email verified successfully.'}), 200
    return jsonify({'message': 'Invalid or expired token.'}), 400


def handle_password_reset(data, db, redirect_url=None, token=None):
    user = db.query(Registration).get(data['user_id'])
    if user:
        frontend_form_url = f"{redirect_url}/reset-password?token={token}"
        return redirect(frontend_form_url)
    return jsonify({'message': 'Invalid token.'}), 400


@app_views.route('/update-password', methods=['POST'])
def update_password():
    # Check if data is sent as JSON
    if request.is_json:
        data = request.get_json()
    else:
        # Fallback to form data
        data = request.form
    
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required.'}), 400

    # Verify the token
    try:
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = data['user_id']

        # Retrieve the user from the database
        user = db.query(Registration).get(user_id)
        if not user:
            return jsonify({'message': 'Invalid or expired token.'}), 400

        # Update the user's password (hash it for security)
        user.set_password(new_password)
        db.commit()
        return jsonify({'message': 'Password updated successfully.'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired.'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token.'}), 400
    finally:
        db.close()


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
    session = Session()
    user = session.query(Registration).filter_by(id=current_user_identity['id']).first()
    if user:
        user_info = {
            'id': user.id,
            'email': user.email
            # Add other fields as needed
        }
        session.close()
        return jsonify(user_info), 200
    else:
        session.close()
        return jsonify({"msg": "User not found"}), 404
