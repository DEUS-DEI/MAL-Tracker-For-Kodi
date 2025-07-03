"""
Autenticación manual alternativa para MAL OAuth
Sin servidor local - usando copia manual de código
"""

import webbrowser
import requests
import json
import base64
import hashlib
import secrets
import urllib.parse
import xbmcgui
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, TOKEN_FILE, USER_AGENT, rate_limit

def manual_oauth_flow():
    """Flujo OAuth manual sin servidor local"""
    import xbmc
    
    if not CLIENT_ID or CLIENT_ID.strip() == '':
        xbmcgui.Dialog().ok('MAL Tracker', 
            'Client ID no configurado.\n\n'
            'Ve a Configuración → Addons → MAL Tracker\n'
            'y configura tu Client ID de MyAnimeList.')
        return None
    
    # Generar PKCE
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Construir URL
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID.strip(),
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    auth_url = AUTH_URL + '?' + urllib.parse.urlencode(params)
    
    # Mostrar instrucciones
    dialog = xbmcgui.Dialog()
    dialog.ok('Autenticación Manual', 
        'PASO 1: Se abrirá tu navegador\n'
        'PASO 2: Autoriza la aplicación en MAL\n'
        'PASO 3: Copia el código de la URL\n'
        'PASO 4: Pégalo en el siguiente campo')
    
    # Abrir navegador
    try:
        webbrowser.open(auth_url)
    except:
        dialog.textviewer('URL Manual', f'Ve a esta URL:\n\n{auth_url}')
    
    # Solicitar código manualmente
    auth_code = dialog.input('Pega el código de autorización aquí:')
    if not auth_code:
        return None
    
    auth_code = auth_code.strip()
    
    # Intercambiar por token
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID.strip(),
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    
    if CLIENT_SECRET and CLIENT_SECRET.strip():
        data['client_secret'] = CLIENT_SECRET.strip()
    
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        rate_limit()
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Error desconocido')
            except:
                error_msg = f'HTTP {response.status_code}'
            
            dialog.ok('Error OAuth', f'Error: {error_msg}\n\nVerifica el código copiado.')
            return None
        
        token_data = response.json()
        
        if 'access_token' not in token_data:
            dialog.ok('Error', 'Token inválido recibido')
            return None
        
        # Guardar token
        import time
        token_data['obtained_at'] = int(time.time())
        
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        xbmc.log('MAL Manual Auth: Token saved successfully', xbmc.LOGINFO)
        return token_data.get('access_token')
        
    except Exception as e:
        dialog.ok('Error', f'Error de conexión:\n{str(e)}')
        return None

def show_manual_auth_help():
    """Mostrar ayuda para autenticación manual"""
    help_text = """AUTENTICACIÓN MANUAL MAL:

1. CONFIGURAR CLIENT ID:
   - Ve a https://myanimelist.net/apiconfig
   - Crea una nueva aplicación
   - Copia el Client ID
   - Ve a Configuración → MAL Tracker
   - Pega el Client ID

2. AUTENTICAR:
   - Selecciona "Autenticación Manual"
   - Se abrirá tu navegador
   - Autoriza la aplicación
   - Copia el código de la URL
   - Pégalo en Kodi

3. ALTERNATIVA SIN NAVEGADOR:
   - Usa la app auxiliar oauth_helper.py
   - Ejecuta desde PC/móvil
   - Genera el token
   - Cópialo a Kodi

¿Problemas? Verifica:
- Client ID correcto
- Conexión a internet
- Código copiado completo"""
    
    xbmcgui.Dialog().textviewer('Ayuda - Autenticación Manual', help_text)