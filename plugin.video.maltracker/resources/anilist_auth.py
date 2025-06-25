import webbrowser
import requests
import json
import xbmcgui
from .config import ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET, ANILIST_AUTH_URL, ANILIST_TOKEN_URL, ANILIST_TOKEN_FILE, USER_AGENT

def get_authorization_code():
    if not ANILIST_CLIENT_ID:
        xbmcgui.Dialog().notification('AniList', 'Client ID no configurado')
        return None
    url = f"{ANILIST_AUTH_URL}?client_id={ANILIST_CLIENT_ID}&response_type=code&redirect_uri=http://localhost:8080/callback"
    try:
        webbrowser.open(url)
    except:
        pass
    dialog = xbmcgui.Dialog()
    dialog.ok('Autorización AniList', f'Visita: {url}\n\nCopia el código de la URL de callback.')
    return dialog.input('Código de autorización:')

def get_access_token(auth_code):
    if not auth_code or not ANILIST_CLIENT_ID:
        return None
    data = {
        'grant_type': 'authorization_code',
        'client_id': ANILIST_CLIENT_ID,
        'client_secret': ANILIST_CLIENT_SECRET,
        'redirect_uri': 'http://localhost:8080/callback',
        'code': auth_code
    }
    headers = {'User-Agent': USER_AGENT, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        response = requests.post(ANILIST_TOKEN_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        with open(ANILIST_TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        return token_data.get('access_token')
    except Exception as e:
        xbmcgui.Dialog().notification('AniList', f'Error: {str(e)}')
        return None

def load_access_token():
    try:
        with open(ANILIST_TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('access_token')
    except:
        return None