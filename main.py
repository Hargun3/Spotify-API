import requests
import urllib.parse

from flask import Flask , request


app = Flask(__name__)
app.secret_key = 'test1wsazxasmansiabddvasfv423b213b2132323'


CLIENT_ID = 'fb9ba38989444a259af61ce8f69878ac'
CLIENT_SECRET = 'd5a4b236ab6e4d40877817db357e873d'
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL =  'https://accounts.spotify.com/token'
API_BASE_URL = 'https://api.spotify.com/v1/'



@app.route('/')
def index():
    return "Welcome to my Spotify App <a> href = '/login'>Login with SPotify</a>"


app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id' : CLIENT_ID,
        'response_type' : 'code',
        'scope' : scope,
        'redirect_uri' : REDIRECT_URI,
        'show_dialog' : False  #omit later while testing

    }

    auth_url  = f"{AUTH_URL} ? {urllib.parse.urlencode(params)}"

    return redirect(auth_url)



