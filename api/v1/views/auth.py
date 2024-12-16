
#!/usr/bin/python3
"""routes for users"""
from flask import jsonify, request, session
from models import storage
from models.registration import Registration
from api.v1.views import app_views
from requests_oauthlib import OAuth2Session
from ..services.jwt_service import create_jwt_token
from os import getenv

Session = storage._DBStorage__session

CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
#redirect_uri = 'http://localhost:5500/oauth2/callback'  # Client-side app callback URL
redirect_uri = 'https://househubng.netlify.app'

authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'


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
        
        if user_email:
            # Check if user exists, if not, add to the database
            session = Session()
            user = session.query(Registration).filter_by(email=user_email).first()
            if not user:
                user = Registration(email=user_email)
                storage.new(user)
                storage.save()

            # Generate JWT token
            access_token = create_jwt_token(user.id, user.email)
            session.close()
            redirect_url = 'https://househubng.netlify.app/listings.html'

            return jsonify({
                'token': access_token,
                'redirect_url': redirect_url
            }), 200
        else:
            return jsonify({'error': 'Failed to fetch user email'}), 400
    else:
        return jsonify({'error': 'Authorization code missing'}), 400
