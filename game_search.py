import os
import requests
from flask import Flask, redirect, request, render_template_string, session, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

oauth = OAuth(app)

STEAM_API_KEY_FILE = "steam_api_key.txt"

def read_steam_api_key():
    """Read the Steam API key from the file."""
    try:
        with open(STEAM_API_KEY_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"[Error] File '{STEAM_API_KEY_FILE}' not found. Please create it and add your Steam API key.")
        return None

STEAM_API_KEY = read_steam_api_key()
if not STEAM_API_KEY:
    exit(1)

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

def is_valid_game_folder(folder_path):
    """Check if a folder contains a game executable or other common game-related files."""
    possible_executables = ["game.exe", "launcher.exe", "play.exe", "start.exe"]
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower() in possible_executables or file.endswith(".exe"):
                return True
    return False

def search_local_games():
    game_directories = [
        os.getenv("PROGRAMFILES", "C:/Program Files") + "/Epic Games",
        os.getenv("PROGRAMFILES(X86)", "C:/Program Files (x86)") + "/Steam/steamapps/common",
        "C:/Games"
    ]
    found_games = set()
    for game_directory in game_directories:
        if os.path.exists(game_directory):
            for folder in os.listdir(game_directory):
                folder_path = os.path.join(game_directory, folder)
                if os.path.isdir(folder_path) and is_valid_game_folder(folder_path):
                    found_games.add(folder)
        else:
            print(f"[Warning] The directory {game_directory} does not exist.")
    return sorted(found_games)

def get_steam_games(steamid):
    """Fetch the user's Steam game library using their SteamID."""
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': STEAM_API_KEY,
        'steamid': steamid,
        'format': 'json',
        'include_appinfo': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'games' in data['response']:
            return data['response']['games']
    return []

@app.route('/')
def home():
    """Render the main page with a login/logout button."""
    return render_template_string('''
        <h1>Clockwork - Game Library</h1>
        {% if 'steam_id' in session %}
            <p>Logged in as: {{ session['steam_id'] }}</p>
            <button onclick="window.location.href='/logout'">Logout</button>
        {% else %}
            <button onclick="window.location.href='/login'">Login with Steam</button>
        {% endif %}
        <button onclick="window.location.href='/games'">View Games</button>
    ''')

@app.route('/login')
def login():
    """Redirect to Steam OpenID login."""
    return redirect(f"{STEAM_OPENID_URL}?openid.ns=http://specs.openid.net/auth/2.0"
                    "&openid.mode=checkid_setup"
                    f"&openid.return_to={url_for('auth', _external=True)}"
                    "&openid.realm=http://localhost:8080"
                    "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
                    "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select")

@app.route('/auth')
def auth():
    """Handle Steam OpenID response and validate it."""
    if 'openid.claimed_id' in request.args:
        steam_id = request.args['openid.claimed_id'].split('/')[-1]  # Extract SteamID
        session['steam_id'] = steam_id
        return redirect(url_for('show_games'))
    return "Steam login failed."

@app.route('/logout')
def logout():
    """Clear session and log out user."""
    session.clear()
    return redirect(url_for('home'))

@app.route('/games')
def show_games():
    """Display locally found games and Steam games."""
    local_games = search_local_games()
    steam_games = get_steam_games(session.get('steam_id')) if 'steam_id' in session else []
    return render_template_string('''
        <h1>Your Games</h1>
        {% if 'steam_id' in session %}
            <p>Logged in as Steam User: {{ session['steam_id'] }}</p>
            <button onclick="window.location.href='/logout'">Logout</button>
        {% else %}
            <p>You are not logged in.</p>
            <button onclick="window.location.href='/login'">Login with Steam</button>
        {% endif %}
        
        <h2>Local Games:</h2>
        <ul>
            {% for game in local_games %}
                <li>{{ game }}</li>
            {% endfor %}
        </ul>
        
        <h2>Steam Games:</h2>
        <ul>
            {% for game in steam_games %}
                <li>{{ game.name }} (Playtime: {{ game.playtime_forever }} minutes)</li>
            {% endfor %}
        </ul>
    ''', local_games=local_games, steam_games=steam_games)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
