
import webbrowser
import requests
import json
import base64
import hashlib
import secrets
import threading
import urllib.parse
import xbmcgui
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, TOKEN_FILE, USER_AGENT, rate_limit
from .local_server import start_callback_server

# Paso 1: Obtener el código de autorización

def generate_pkce_pair():
    # Generar code_verifier de 43-128 caracteres (MAL requirement)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    # Generar code_challenge usando SHA256
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def get_authorization_code():
    import xbmc
    
    # Validar CLIENT_ID
    if not CLIENT_ID or CLIENT_ID.strip() == '':
        xbmcgui.Dialog().ok('MAL Tracker', 
            'Client ID no configurado o vacío.\n\n'
            'Ve a Configuración → Addons → MAL Tracker\n'
            'y configura tu Client ID de MyAnimeList.\n\n'
            'Obtén las credenciales en:\n'
            'https://myanimelist.net/apiconfig')
        return None, None
    
    xbmc.log(f'MAL Auth: Starting OAuth with Client ID: {CLIENT_ID[:10]}...', xbmc.LOGINFO)
    
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Construir URL de autorización
    import urllib.parse
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID.strip(),
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': secrets.token_urlsafe(16)  # Agregar state para seguridad
    }
    
    url = AUTH_URL + '?' + urllib.parse.urlencode(params)
    xbmc.log(f'MAL Auth: Authorization URL generated', xbmc.LOGDEBUG)
    
    # Mostrar instrucciones al usuario
    dialog = xbmcgui.Dialog()
    if not dialog.yesno('MAL Autenticación', 
                       'Se iniciará el servidor local en puerto 8080\n'
                       'y se abrirá tu navegador.\n\n'
                       '¿Continuar con la autenticación?'):
        return None, None
    
    # Iniciar servidor en hilo separado con mejor manejo
    server_result = {'code': None, 'error': None}
    
    def server_worker():
        try:
            result = start_callback_server()
            server_result['code'] = result
        except Exception as e:
            server_result['error'] = str(e)
            xbmc.log(f'MAL Auth: Server thread error - {str(e)}', xbmc.LOGERROR)
    
    server_thread = threading.Thread(target=server_worker)
    server_thread.daemon = True
    server_thread.start()
    
    # Esperar un momento para que el servidor se inicie
    import time
    time.sleep(1)
    
    # Abrir navegador
    try:
        webbrowser.open(url)
        xbmc.log('MAL Auth: Browser opened successfully', xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f'MAL Auth: Failed to open browser - {str(e)}', xbmc.LOGWARNING)
        dialog.ok('MAL Auth', f'No se pudo abrir el navegador automáticamente.\n\nVe manualmente a:\n{url}')
    
    # Mostrar progreso mientras esperamos
    progress = xbmcgui.DialogProgress()
    progress.create('MAL Autenticación', 'Esperando autorización...')
    
    # Esperar resultado con timeout de 2 minutos
    timeout = 120
    for i in range(timeout):
        if progress.iscanceled():
            dialog.notification('MAL Auth', 'Autenticación cancelada')
            return None, None
            
        if server_result['code'] or server_result['error']:
            break
            
        progress.update(int((i / timeout) * 100), f'Esperando autorización... ({timeout - i}s)')
        time.sleep(1)
    
    progress.close()
    
    # Verificar resultado
    if server_result['error']:
        dialog.notification('MAL Auth', f'Error del servidor: {server_result["error"]}')
        return None, None
        
    code = server_result['code']
    if not code:
        dialog.notification('MAL Auth', 'Timeout - No se recibió código de autorización')
        return None, None
    
    xbmc.log('MAL Auth: Authorization code received successfully', xbmc.LOGINFO)
    return code, code_verifier

# Paso 2: Intercambiar el código por un token de acceso

def get_access_token(auth_code, code_verifier):
    import xbmc
    
    # Validaciones mejoradas
    if not auth_code or auth_code.strip() == '':
        xbmcgui.Dialog().notification('MAL Tracker', 'Código de autorización faltante o vacío')
        return None
        
    if not CLIENT_ID or CLIENT_ID.strip() == '':
        xbmcgui.Dialog().notification('MAL Tracker', 'Client ID no configurado')
        return None
    
    if not code_verifier:
        xbmcgui.Dialog().notification('MAL Tracker', 'Code verifier faltante')
        return None
    
    # Limpiar el código
    auth_code = auth_code.strip()
    
    xbmc.log(f'MAL Auth: Iniciando intercambio de token con code: {auth_code[:10]}...', xbmc.LOGINFO)
    
    # Preparar datos para el intercambio
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID.strip(),
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    
    # CLIENT_SECRET es opcional para MAL
    if CLIENT_SECRET and CLIENT_SECRET.strip():
        data['client_secret'] = CLIENT_SECRET.strip()
    
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        rate_limit()
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
        
        xbmc.log(f'MAL Auth: Response status: {response.status_code}', xbmc.LOGINFO)
        xbmc.log(f'MAL Auth: Response headers: {dict(response.headers)}', xbmc.LOGDEBUG)
        
        # Manejo mejorado de errores
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
                error_desc = error_data.get('error_description', '')
                full_error = f'{error_msg}: {error_desc}' if error_desc else error_msg
            except:
                full_error = response.text[:200] if response.text else 'Sin detalles de error'
            
            xbmc.log(f'MAL Auth Error: {response.status_code} - {full_error}', xbmc.LOGERROR)
            
            # Mostrar errores específicos al usuario
            if response.status_code == 400:
                xbmcgui.Dialog().ok('MAL Error', f'Error de solicitud (400):\n{full_error}\n\nVerifica tu Client ID y configuración.')
            elif response.status_code == 401:
                xbmcgui.Dialog().ok('MAL Error', f'No autorizado (401):\n{full_error}\n\nEl código de autorización puede haber expirado.')
            else:
                xbmcgui.Dialog().ok('MAL Error', f'Error {response.status_code}:\n{full_error}')
            
            return None
            
        # Parsear respuesta JSON
        try:
            token_data = response.json()
        except json.JSONDecodeError as e:
            xbmc.log(f'MAL Auth Error: Invalid JSON response - {str(e)}', xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MAL Error', 'Respuesta inválida del servidor')
            return None
        
        # Validar estructura del token
        if 'access_token' not in token_data:
            xbmc.log('MAL Auth Error: No access_token in response', xbmc.LOGERROR)
            xbmc.log(f'MAL Auth: Response data: {token_data}', xbmc.LOGDEBUG)
            xbmcgui.Dialog().notification('MAL Error', 'Token de acceso no encontrado en respuesta')
            return None
        
        # Agregar timestamp para manejo de expiración
        import time
        token_data['obtained_at'] = int(time.time())
        
        # Guardar token de forma segura
        try:
            with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            xbmc.log('MAL Auth: Token guardado exitosamente', xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f'MAL Auth Error: Failed to save token - {str(e)}', xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MAL Error', f'Error guardando token: {str(e)}')
            return None
            
        return token_data.get('access_token')
        
    except requests.exceptions.Timeout:
        xbmcgui.Dialog().notification('MAL Tracker', 'Timeout - El servidor tardó demasiado en responder')
        return None
    except requests.exceptions.ConnectionError:
        xbmcgui.Dialog().notification('MAL Tracker', 'Error de conexión - Verifica tu internet')
        return None
    except requests.exceptions.RequestException as e:
        xbmc.log(f'MAL Auth: Request error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error de red: {str(e)}')
        return None
    except Exception as e:
        xbmc.log(f'MAL Auth: Unexpected error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error inesperado: {str(e)}')
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
