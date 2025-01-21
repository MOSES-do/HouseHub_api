#!/usr/bin/python3
"""routes for users"""
from flask import jsonify, request, session
from models import storage
from models.registration import Registration
from api.v1.views import app_views
from requests_oauthlib import OAuth2Session
from ..services.jwt_service import create_jwt_token
from google.oauth2 import id_token
from google.auth.transport import requests
from os import getenv

Session = storage._DBStorage__session

CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
#redirect_uri = 'http://localhost:5500'  # Client-side app callback URL
redirect_uri = 'https://househubng.netlify.app'

authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'


# Route to handle the ID Token (from frontend-based login)
@app_views.route('/google-signin', methods=['POST'])
def handle_id_token():
    try:
        # Get the token from the request
        token = request.json.get('code')
        
        # Verify the token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        
        # Extract user information
        user_info = {
            'user_id': id_info['sub'],
            'email': id_info['email'],
            'name': id_info.get('name', ''),
            'picture': id_info.get('picture', '')
        }
        return checkUserExistenceInDb(user_info['email'], True)
        #return jsonify({'status': 'success', 'user_info': user_info}), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': 'Invalid ID token', 'details': str(e)}), 400


@app_views.route('/login/google')
def login_google():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['openid', 'email', 'profile'])
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline')
    session['oauth_state'] = state
    return jsonify({'authorization_url': authorization_url, 'response': "ok"})


@app_views.route('/oauth2/callback', methods=["POST"])
def oauth2_callback():
    oauth_code = request.json.get('code')
    
    if oauth_code:
        google = OAuth2Session(client_id, redirect_uri=redirect_uri)
        try:
            token = google.fetch_token(token_url, client_secret=client_secret, code=oauth_code)
        except Exception as e:
            return jsonify({'error': f'Failed to fetch token: {str(e)}'}), 400

        user_info = google.get(user_info_url).json()
        user_email = user_info.get('email')

        return checkUserExistenceInDb(user_email, True)
        
    else:
        return jsonify({'error': 'Authorization code missing'}), 400


def checkUserExistenceInDb(user_email, verify_email=False):
    """Confirm user exists in databses or create user"""
    if user_email:
        # Check if user exists, if not, add to the database
        session = Session()
        user = session.query(Registration).filter_by(email=user_email).first()
        if not user:
            user = Registration(email=user_email)
            if verify_email:
                user.is_verified = True
            storage.new(user)
            storage.save()

        # Generate JWT token
        access_token = create_jwt_token(user.id, user.email)
        session.close()

        return jsonify({
            'token': access_token,
        }), 200
    else:
        return jsonify({'error': 'Failed to fetch user email'}), 400
