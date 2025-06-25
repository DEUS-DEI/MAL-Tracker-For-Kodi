import xbmcaddon
from . import auth, mal_api, anilist_auth, anilist_api

addon = xbmcaddon.Addon()

def get_active_service():
    """Determina qué servicio usar basado en configuración"""
    mal_configured = bool(addon.getSetting('client_id'))
    anilist_configured = bool(addon.getSetting('anilist_client_id'))
    
    if mal_configured and anilist_configured:
        if auth.load_access_token():
            return 'mal'
        elif anilist_auth.load_access_token():
            return 'anilist'
        return 'mal'
    elif mal_configured:
        return 'mal'
    elif anilist_configured:
        return 'anilist'
    return None

def is_authenticated():
    service = get_active_service()
    if service == 'mal':
        return auth.load_access_token() is not None
    elif service == 'anilist':
        return anilist_auth.load_access_token() is not None
    return False

def authenticate():
    service = get_active_service()
    if service == 'mal':
        code, code_verifier = auth.get_authorization_code()
        if code:
            return auth.get_access_token(code, code_verifier)
    elif service == 'anilist':
        code = anilist_auth.get_authorization_code()
        if code:
            return anilist_auth.get_access_token(code)
    return None

def get_user_anime_list():
    service = get_active_service()
    if service == 'mal':
        return mal_api.get_user_anime_list()
    elif service == 'anilist':
        return anilist_api.get_user_anime_list()
    return None

def search_anime(query):
    service = get_active_service()
    if service == 'mal':
        from . import mal_search
        return mal_search.search_anime(query)
    elif service == 'anilist':
        return anilist_api.search_anime(query)
    return None

def update_anime_status(anime_id, status, episodes=None):
    service = get_active_service()
    if service == 'mal':
        return mal_api.update_anime_status(anime_id, status, episodes)
    elif service == 'anilist':
        # Convertir estados de MAL a AniList
        status_map = {
            'watching': 'CURRENT',
            'completed': 'COMPLETED',
            'on_hold': 'PAUSED',
            'dropped': 'DROPPED',
            'plan_to_watch': 'PLANNING'
        }
        anilist_status = status_map.get(status, status)
        return anilist_api.update_anime_status(anime_id, anilist_status, episodes)
    return False