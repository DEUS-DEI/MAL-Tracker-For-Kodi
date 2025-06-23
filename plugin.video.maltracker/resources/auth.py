
import webbrowser
import requests
import json
import base64
import hashlib
import secrets
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL

TOKEN_FILE = 'resources/token.json'

# Paso 1: Obtener el código de autorización

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

def get_authorization_code():
    code_verifier, code_challenge = generate_pkce_pair()
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': 'kodi_mal'
    }
    url = AUTH_URL + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    webbrowser.open(url)
    import xbmcgui
    dialog = xbmcgui.Dialog()
    dialog.ok('Autorización requerida', 'Abre el enlace en tu navegador y autoriza el acceso a tu cuenta de MyAnimeList. Luego, copia el código de autorización.')
    code = dialog.input('Código de autorización:')
    return code, code_verifier

# Paso 2: Intercambiar el código por un token de acceso

def get_access_token(auth_code, code_verifier):
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    # Cumple con https://myanimelist.net/apiconfig/references/api/v2 y PKCE
    try:
        response = requests.post(TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        return token_data['access_token']
    except requests.RequestException as e:
        print('Error al obtener el token:', str(e))
        return None

# Paso 3: Cargar el token de acceso guardado

def load_access_token():
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        return token_data['access_token']
    except (FileNotFoundError, json.JSONDecodeError):
        return None
