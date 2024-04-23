from flask import Flask, redirect, request, jsonify, session
from dotenv import load_dotenv
import requests
import secrets
from datetime import datetime, timedelta
import json
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

REDIRECT_URI = "http://localhost:5000/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

@app.route("/")
def index():
    return "Welcome to my spotify app! <a href='/login'>Login with Spotify</a>"

@app.route("/login")
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    auth_url = f"{AUTH_URL}?{query_string}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # if 'access_token' not in session or 'refresh_token' not in session or 'expires_at' not in session:
    #     return redirect('/login')
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    # if we dont have errror, user logged in successfully
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        
        return redirect('/playlists')
    
@app.route("/playlists")
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    # access token must be in session
    # lets confirm it has not expired
    if datetime.now().timestamp() > session['expires_at']:
        # token has expired, lets refresh it
        return redirect('/refresh_token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)

    playlists = response.json()
    html = "<h1>Playlists</h1>"
    # add way to logout
    html += "<a href='/logout'>Logout</a><br><br>"
    
    j = json.dumps(playlists)
    
    # get tracks for each playlist
    for playlist in playlists['items']:
        playlist_id = playlist['id']
        response = requests.get(f"{API_BASE_URL}playlists/{playlist_id}/tracks", headers=headers)
        tracks = response.json()
        
        html += f"<h2>{playlist['name']}</h2>"
        html += "<h3>Tracks:</h3>"
        print(tracks['items'][0].keys())
        
        for t in tracks['items']:
            html += f"<p>{t['track']['name']}</p>"
            
        html += "<br><br>"

    return html
    
    
@app.route("/refresh_token")
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()
    
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    
    return redirect('/playlists')


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug=True)