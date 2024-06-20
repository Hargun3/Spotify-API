import requests
import urllib.parse

from datetime import datetime, timedelta
from flask import Flask, request, redirect, jsonify, session

app = Flask(__name__)
# Secret key for session management, should be a strong random string in a real application
app.secret_key = 'test1wsazxasmansiabddvasfv423b213b2132323'

# Spotify API credentials
CLIENT_ID = 'fb9ba38989444a259af61ce8f69878ac'
CLIENT_SECRET = 'hidegit'
REDIRECT_URI = 'http://localhost:5000/callback'

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    # Main entry point of the application, provides a link to login with Spotify
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    # Defines the permissions the app will ask for
    scope = 'user-read-private user-read-email'

    # Parameters for the authorization URL
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': False  # Set to True if you want to force the user to always approve the app
    }

    # Construct the full authorization URL and redirect the user to it
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Check if there's an error in the callback request
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    # Check if the authorization code is present in the callback request
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        # Exchange the authorization code for an access token
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        # Store the access and refresh tokens in the session
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        # Redirect to the playlists endpoint after successfully obtaining the token
        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    # Check if the access token is available in the session
    if 'access_token' not in session:
        return redirect('/login')

    # Check if the access token has expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')

    # Set up the headers with the access token to make an authenticated request
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Make a request to Spotify's API to get the user's playlists
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    # Return the playlists as JSON
    return jsonify(playlists)

@app.route('/refresh_token')
def refresh_token():
    # Check if the refresh token is available in the session
    if 'refresh_token' not in session:
        return redirect('/login')

    # Check if the access token has expired
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        # Request a new access token using the refresh token
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        # Update the session with the new access token and expiry time
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        # Redirect back to the playlists endpoint after refreshing the token
        return redirect('/playlists')

if __name__ == '__main__':
    # Run the Flask app, accessible from any IP address on port 5000, with debug mode enabled
    app.run(host='0.0.0.0', debug=True)
