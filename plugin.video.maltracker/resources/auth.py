
import webbrowser
import requests
import json
import base64
import hashlib
import secrets
import xbmcgui
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, TOKEN_FILE, USER_AGENT, rate_limit

# Paso 1: Obtener el código de autorización

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

def get_authorization_code():
    if not CLIENT_ID:
        xbmcgui.Dialog().notification('MAL Tracker', 'Client ID no configurado')
        return None, None
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
    try:
        webbrowser.open(url)
    except:
        pass
    dialog = xbmcgui.Dialog()
    dialog.ok('Autorización requerida', f'Visita: {url}\n\nAutoriza el acceso y copia el código.')
    code = dialog.input('Código de autorización:')
    return code, code_verifier

# Paso 2: Intercambiar el código por un token de acceso

def get_access_token(auth_code, code_verifier):
    if not auth_code or not CLIENT_ID:
        return None
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET
    headers = {'User-Agent': USER_AGENT}
    try:
        rate_limit()
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        return token_data.get('access_token')
    except Exception as e:
        xbmcgui.Dialog().notification('MAL Tracker', f'Error token: {str(e)}')
        return None

# Paso 3: Cargar el token de acceso guardado

def load_access_token():
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        return token_data.get('access_token')
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

def refresh_access_token():
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            return None
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID
        }
        if CLIENT_SECRET:
            data['client_secret'] = CLIENT_SECRET
        headers = {'User-Agent': USER_AGENT}
        rate_limit()
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        new_token_data = response.json()
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_token_data, f, ensure_ascii=False, indent=2)
        return new_token_data.get('access_token')
    except Exception:
        return None
