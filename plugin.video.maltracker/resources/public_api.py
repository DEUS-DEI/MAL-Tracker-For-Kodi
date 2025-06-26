import requests
import json
from .config import USER_AGENT, rate_limit

# APIs públicas sin autenticación (solo lectura)

def search_anime_public(query, limit=20):
    """Búsqueda pública usando Jikan API (MyAnimeList scraper)"""
    try:
        rate_limit()
        url = f"https://api.jikan.moe/v4/anime"
        params = {
            'q': query,
            'limit': limit,
            'order_by': 'popularity',
            'sort': 'desc'
        }
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None

def get_anime_details_public(anime_id):
    """Detalles públicos usando Jikan API"""
    try:
        rate_limit()
        url = f"https://api.jikan.moe/v4/anime/{anime_id}/full"
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json().get('data')
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None

def get_top_anime_public(limit=50):
    """Top anime público"""
    try:
        rate_limit()
        url = f"https://api.jikan.moe/v4/top/anime"
        params = {'limit': limit}
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None

def get_seasonal_anime_public():
    """Anime de temporada actual"""
    try:
        rate_limit()
        url = f"https://api.jikan.moe/v4/seasons/now"
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None

def get_schedule_public(day=None):
    """Calendario de emisiones de anime"""
    try:
        rate_limit()
        if day:
            url = f"https://api.jikan.moe/v4/schedules/{day.lower()}"
        else:
            url = f"https://api.jikan.moe/v4/schedules"
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None

def get_upcoming_anime_public():
    """Próximos estrenos de anime"""
    try:
        rate_limit()
        url = f"https://api.jikan.moe/v4/seasons/upcoming"
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        import xbmc
        xbmc.log(f'Public API Error: {str(e)}', xbmc.LOGERROR)
        return None