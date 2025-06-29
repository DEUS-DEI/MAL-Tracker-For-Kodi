import xbmcaddon
import xbmcvfs
import os
import time

# Asegurar que el addon esté completamente inicializado
try:
    addon = xbmcaddon.Addon()
    CLIENT_ID = addon.getSetting('client_id') or None
    CLIENT_SECRET = addon.getSetting('client_secret') or None
except Exception as e:
    # Fallback si hay problemas de inicialización
    import xbmc
    xbmc.log(f'MAL Config: Initialization error - {str(e)}', xbmc.LOGDEBUG)
    xbmc.sleep(100)
    try:
        addon = xbmcaddon.Addon()
        CLIENT_ID = addon.getSetting('client_id') or None
        CLIENT_SECRET = addon.getSetting('client_secret') or None
    except:
        CLIENT_ID = None
        CLIENT_SECRET = None
try:
    REDIRECT_URI = addon.getSetting('redirect_uri') or 'http://localhost:8080/callback'
    USER_AGENT = f"MALTracker-Kodi/{addon.getAddonInfo('version')} (https://github.com/user/mal-tracker-kodi)"
except:
    REDIRECT_URI = 'http://localhost:8080/callback'
    USER_AGENT = "MALTracker-Kodi/1.0.0 (https://github.com/user/mal-tracker-kodi)"

AUTH_URL = 'https://myanimelist.net/v1/oauth2/authorize'
TOKEN_URL = 'https://myanimelist.net/v1/oauth2/token'
API_BASE_URL = 'https://api.myanimelist.net/v2'

# Rate limiting: 1 request per second
last_request_time = 0

def rate_limit():
    global last_request_time
    current_time = time.time()
    if current_time - last_request_time < 1.0:
        time.sleep(1.0 - (current_time - last_request_time))
    last_request_time = time.time()

# Configuración AniList
try:
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
