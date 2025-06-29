import xbmcaddon
import xbmcvfs
import os
import time
import threading

# Inicialización mejorada del addon
def init_addon_settings():
    import xbmc
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            addon = xbmcaddon.Addon()
            client_id = addon.getSetting('client_id')
            client_secret = addon.getSetting('client_secret')
            redirect_uri = addon.getSetting('redirect_uri')
            
            # Validar y limpiar configuraciones
            client_id = client_id.strip() if client_id else None
            client_secret = client_secret.strip() if client_secret else None
            redirect_uri = redirect_uri.strip() if redirect_uri else 'http://localhost:8080/callback'
            
            # Validar CLIENT_ID (requerido)
            if not client_id or len(client_id) < 10:
                xbmc.log('MAL Config: CLIENT_ID is empty or too short', xbmc.LOGWARNING)
                client_id = None
            
            user_agent = f"MALTracker-Kodi/{addon.getAddonInfo('version')} (https://github.com/user/mal-tracker-kodi)"
            
            return client_id, client_secret, redirect_uri, user_agent
            
        except Exception as e:
            xbmc.log(f'MAL Config: Initialization attempt {attempt + 1} failed - {str(e)}', xbmc.LOGDEBUG)
            if attempt < max_retries - 1:
                xbmc.sleep(200)  # Esperar antes del siguiente intento
            else:
                xbmc.log('MAL Config: All initialization attempts failed', xbmc.LOGERROR)
                return None, None, 'http://localhost:8080/callback', "MALTracker-Kodi/1.0.0"
    
    return None, None, 'http://localhost:8080/callback', "MALTracker-Kodi/1.0.0"

# Inicializar configuraciones
CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USER_AGENT = init_addon_settings()

AUTH_URL = 'https://myanimelist.net/v1/oauth2/authorize'
TOKEN_URL = 'https://myanimelist.net/v1/oauth2/token'
API_BASE_URL = 'https://api.myanimelist.net/v2'

# Rate limiting mejorado: 1 request per second
last_request_time = 0
rate_limit_lock = threading.Lock() if 'threading' in globals() else None

def rate_limit():
    global last_request_time
    
    # Usar lock si está disponible para thread safety
    if rate_limit_lock:
        with rate_limit_lock:
            current_time = time.time()
            time_diff = current_time - last_request_time
            if time_diff < 1.0:
                sleep_time = 1.0 - time_diff
                time.sleep(sleep_time)
            last_request_time = time.time()
    else:
        current_time = time.time()
        time_diff = current_time - last_request_time
        if time_diff < 1.0:
            sleep_time = 1.0 - time_diff
            time.sleep(sleep_time)
        last_request_time = time.time()

# Configuración AniList y rutas
try:
    addon = xbmcaddon.Addon()
    ANILIST_CLIENT_ID = addon.getSetting('anilist_client_id') or None
    ANILIST_CLIENT_SECRET = addon.getSetting('anilist_client_secret') or None
    TOKEN_PATH = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    ANILIST_CLIENT_ID = None
    ANILIST_CLIENT_SECRET = None
    TOKEN_PATH = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.maltracker/')

ANILIST_AUTH_URL = 'https://anilist.co/api/v2/oauth/authorize'
ANILIST_TOKEN_URL = 'https://anilist.co/api/v2/oauth/token'

# Ruta segura para tokens
if not xbmcvfs.exists(TOKEN_PATH):
    xbmcvfs.mkdirs(TOKEN_PATH)
TOKEN_FILE = os.path.join(TOKEN_PATH, 'token.json')
ANILIST_TOKEN_FILE = os.path.join(TOKEN_PATH, 'anilist_token.json')
