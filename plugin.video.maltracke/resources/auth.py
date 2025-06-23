import webbrowser
import requests
import json
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL

TOKEN_FILE = 'resources/token.json'

# Paso 1: Obtener el código de autorización

def get_authorization_code():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge': 'challenge',  # Para PKCE, opcional
        'code_challenge_method': 'plain',
        'state': 'kodi_mal'
    }
    url = AUTH_URL + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    webbrowser.open(url)
    print('Abre el enlace en tu navegador y pega el código de autorización:')
    code = input('Código de autorización: ')
    return code

# Paso 2: Intercambiar el código por un token de acceso

def get_access_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
        return token_data['access_token']
    else:
        print('Error al obtener el token:', response.text)
        return None

# Paso 3: Cargar el token de acceso guardado

def load_access_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        return token_data['access_token']
    except Exception:
        return None
