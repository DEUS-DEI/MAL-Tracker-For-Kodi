
import webbrowser
import requests
import json
import base64
import hashlib
import secrets
import threading
import xbmcgui
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, TOKEN_FILE, USER_AGENT, rate_limit
from .local_server import start_callback_server

# Paso 1: Obtener el código de autorización

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

def get_authorization_code():
    if not CLIENT_ID:
        xbmcgui.Dialog().ok('MAL Tracker', 'Client ID no configurado.\n\nVe a Configuración → Addons → MAL Tracker\ny configura tu Client ID de MyAnimeList.\n\nObten las credenciales en:\nhttps://myanimelist.net/apiconfig')
        return None, None
    
    code_verifier, code_challenge = generate_pkce_pair()
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    url = AUTH_URL + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    
    # Iniciar servidor en hilo separado
    server_thread = threading.Thread(target=lambda: setattr(get_authorization_code, 'result', start_callback_server()))
    server_thread.daemon = True
    server_thread.start()
    
    dialog = xbmcgui.Dialog()
    dialog.ok('MAL Auth', f'Servidor iniciado en puerto 8080\n\nSe abrirá el navegador.\nAutoriza la aplicación.')
    
    try:
        webbrowser.open(url)
    except:
        pass
    
    # Esperar resultado del servidor
    server_thread.join(timeout=60)
    code = getattr(get_authorization_code, 'result', None)
    
    if not code:
        dialog.notification('MAL Auth', 'Timeout o error del servidor')
        return None, None
        
    return code, code_verifier

# Paso 2: Intercambiar el código por un token de acceso

def get_access_token(auth_code, code_verifier):
    if not auth_code:
        xbmcgui.Dialog().notification('MAL Tracker', 'Código de autorización faltante')
        return None
    if not CLIENT_ID:
        xbmcgui.Dialog().notification('MAL Tracker', 'Client ID no configurado')
        return None
    
    # Limpiar el código (remover espacios y saltos de línea)
    auth_code = auth_code.strip()
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET
    
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        import xbmc
        xbmc.log(f'MAL Auth: Iniciando intercambio de token con code: {auth_code[:10]}...', xbmc.LOGINFO)
        
        rate_limit()
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
        
        xbmc.log(f'MAL Auth: Response status: {response.status_code}', xbmc.LOGINFO)
        
        if response.status_code != 200:
            error_detail = response.text[:300] if response.text else 'Sin detalles'
            xbmc.log(f'MAL Auth Error: {response.status_code} - {error_detail}', xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MAL Error', f'Status: {response.status_code}\n{error_detail}')
            return None
            
        token_data = response.json()
        
        # Validar estructura del token (estilo MALSync)
        if 'access_token' not in token_data:
            xbmc.log('MAL Auth Error: No access_token in response', xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MAL Error', 'Token inválido recibido')
            return None
            
        # Agregar timestamp para expiración
        import time
        token_data['obtained_at'] = int(time.time())
        
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
            
        xbmc.log('MAL Auth: Token guardado exitosamente', xbmc.LOGINFO)
        return token_data.get('access_token')
        
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().notification('MAL Tracker', f'Request Error: {str(e)}')
        return None
    except Exception as e:
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')
        return None

# Paso 3: Cargar el token de acceso guardado

def load_access_token():
    import xbmc
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
            
        access_token = token_data.get('access_token')
        if not access_token:
            return None
            
        # Verificar expiración (estilo MALSync)
        expires_in = token_data.get('expires_in', 3600)
        obtained_at = token_data.get('obtained_at', 0)
        
        if obtained_at > 0:
            import time
            current_time = int(time.time())
            token_age = current_time - obtained_at
            
            # Si el token expira en menos de 5 minutos, intentar refresh
            if token_age > (expires_in - 300):
                xbmc.log('MAL Auth: Token near expiration, attempting refresh', xbmc.LOGINFO)
                refreshed_token = refresh_access_token()
                if refreshed_token:
                    return refreshed_token
                else:
                    xbmc.log('MAL Auth: Token refresh failed, using current token', xbmc.LOGWARNING)
                    
        return access_token
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        xbmc.log(f'MAL Auth: Error loading token - {str(e)}', xbmc.LOGDEBUG)
        return None

def refresh_access_token():
    import xbmc
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            xbmc.log('MAL Auth: No refresh token available', xbmc.LOGWARNING)
            return None
            
        xbmc.log('MAL Auth: Refreshing access token', xbmc.LOGINFO)
        
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
        
        if response.status_code != 200:
            xbmc.log(f'MAL Auth: Refresh failed with status {response.status_code}', xbmc.LOGERROR)
            return None
            
        new_token_data = response.json()
        
        # Validar nuevo token
        if 'access_token' not in new_token_data:
            xbmc.log('MAL Auth: Invalid refresh response', xbmc.LOGERROR)
            return None
            
        # Preservar refresh_token si no viene nuevo
        if 'refresh_token' not in new_token_data:
            new_token_data['refresh_token'] = refresh_token
            
        # Agregar timestamp
        import time
        new_token_data['obtained_at'] = int(time.time())
        
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_token_data, f, ensure_ascii=False, indent=2)
            
        xbmc.log('MAL Auth: Token refreshed successfully', xbmc.LOGINFO)
        return new_token_data.get('access_token')
        
    except Exception as e:
        xbmc.log(f'MAL Auth: Refresh error - {str(e)}', xbmc.LOGERROR)
        return None
