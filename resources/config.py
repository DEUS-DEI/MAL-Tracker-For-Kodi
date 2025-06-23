
# Configuración para OAuth2 de MyAnimeList
import xbmcaddon
addon = xbmcaddon.Addon()
CLIENT_ID = addon.getSetting('client_id')
CLIENT_SECRET = 'TU_CLIENT_SECRET'  # Si quieres, puedes agregarlo como setting también
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
AUTH_URL = 'https://myanimelist.net/v1/oauth2/authorize'
TOKEN_URL = 'https://myanimelist.net/v1/oauth2/token'
API_BASE_URL = 'https://api.myanimelist.net/v2'

# Aquí se almacenará el token de acceso
ACCESS_TOKEN = None
REFRESH_TOKEN = None
