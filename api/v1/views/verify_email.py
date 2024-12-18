#!/usr/bin/python3
import jwt
from api.v1.config import Config
from api.v1.extensions import mail
from api.v1.utils import send_password_reset_email
from api.v1.views import app_views
from flask import jsonify, request, redirect
from models.registration import Registration
from models import storage


Session = storage._DBStorage__session
redirect_url = 'https://househubng.netlify.app'


@app_views.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    return verify_token_and_perform_action(token, handle_email_verification, redirect_url=redirect_url)


@app_views.route('/forgot-password', methods=['POST'])
def forgot_password():
    db = Session()
    try:
        email = request.json.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = db.query(Registration).filter_by(email=email).first()

        if user:
            # Send the password reset email
            try:
                send_password_reset_email(mail, user)
                #print(f"Password reset email sent to: {email}")
                return jsonify({'message': 'Password reset email sent.'}), 200
            except Exception as e:
                #print(f"Error sending email: {e}")
                return jsonify({'error': 'Failed to send email.'}), 500
        else:
            return jsonify({'message': 'User not found.'}), 404
    except Exception as e:
        #print(f"Unexpected error: {e}")
        return jsonify({'error': 'Something went wrong.'}), 500
    finally:
        db.close()

@app_views.route('/reset_password/<token>', methods=['GET'])
def reset_password(token):
    return verify_token_and_perform_action(token, handle_password_reset, redirect_url=redirect_url)


def verify_token_and_perform_action(token, callb_fn, redirect_url=None):
    db = Session()
    try:
        # Decode the token using the provided secret key from the config
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])

        return callb_fn(data, db, redirect_url, token)

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

def handle_email_verification(data, db, redirect_url=None, token=None):
    user = db.query(Registration).get(data['user_id'])
    if user and not user.is_verified:
        user.is_verified = True
        db.commit()
        frontend_url = f"{redirect_url}/verify-success?status=success"
        return redirect(frontend_url, code=302) if frontend_url else jsonify({'message': 'Email verified successfully.'}), 200
    return jsonify({'message': 'Invalid or expired token.'}), 400


def handle_password_reset(data, db, redirect_url=None, token=None):
    user = db.query(Registration).get(data['user_id'])
    if user:
        frontend_form_url = f"{redirect_url}/reset-password?token={token}"
        return redirect(frontend_form_url)
    return jsonify({'message': 'Invalid token.'}), 400


@app_views.route('/update-password', methods=['POST'])
def update_password():

    db = Session()
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
        frontend_form_url = f"{redirect_url}/passwordUpdate-success?status=success"
        return redirect(frontend_form_url)
        #return jsonify({'message': 'Password updated successfully.'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired.'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token.'}), 400
    finally:
        db.close()
