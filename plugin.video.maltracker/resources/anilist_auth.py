import webbrowser
import requests
import json
import threading
import xbmcgui
from .config import ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET, ANILIST_AUTH_URL, ANILIST_TOKEN_URL, ANILIST_TOKEN_FILE, USER_AGENT
from .local_server import start_callback_server

def get_authorization_code():
    if not ANILIST_CLIENT_ID:
        xbmcgui.Dialog().notification('AniList', 'Client ID no configurado')
        return None
    
    url = f"{ANILIST_AUTH_URL}?client_id={ANILIST_CLIENT_ID}&response_type=code&redirect_uri=http://localhost:8080/callback"
    
    # Iniciar servidor
    server_thread = threading.Thread(target=lambda: setattr(get_authorization_code, 'result', start_callback_server()))
    server_thread.daemon = True
    server_thread.start()
    
    dialog = xbmcgui.Dialog()
    dialog.ok('AniList Auth', 'Servidor iniciado en puerto 8080\n\nSe abrirá el navegador.\nAutoriza la aplicación.')
    
    try:
        webbrowser.open(url)
    except:
        pass
    
    # Esperar resultado
    server_thread.join(timeout=60)
    code = getattr(get_authorization_code, 'result', None)
    
    if not code:
        dialog.notification('AniList Auth', 'Timeout o error del servidor')
        return None
        
    return code

def get_access_token(auth_code):
    if not auth_code or not ANILIST_CLIENT_ID:
        xbmcgui.Dialog().notification('AniList', 'Código o Client ID faltante')
        return None
    
    auth_code = auth_code.strip()
    data = {
        'grant_type': 'authorization_code',
        'client_id': ANILIST_CLIENT_ID,
        'client_secret': ANILIST_CLIENT_SECRET,
        'redirect_uri': 'http://localhost:8080/callback',
        'code': auth_code
    }
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(ANILIST_TOKEN_URL, json=data, headers=headers, timeout=15)
        
        if response.status_code != 200:
            error_detail = response.text[:300] if response.text else 'Sin detalles'
            xbmcgui.Dialog().notification('AniList Error', f'Status: {response.status_code}\n{error_detail}')
            return None
            
        token_data = response.json()
        with open(ANILIST_TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        return token_data.get('access_token')
        
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().notification('AniList', f'Request Error: {str(e)}')
        return None
    except Exception as e:
        xbmcgui.Dialog().notification('AniList', f'Error: {str(e)}')
        return None

def load_access_token():
    try:
        with open(ANILIST_TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('access_token')
    except:
        return None