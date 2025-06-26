import requests
from .config import API_BASE_URL, USER_AGENT, rate_limit
from .auth import load_access_token, refresh_access_token

def _make_request(method, url, max_retries=3, **kwargs):
    import xbmc
    token = load_access_token()
    if not token:
        xbmc.log('MAL API: No access token available', xbmc.LOGWARNING)
        return None
        
    headers = kwargs.get('headers', {})
    headers.update({
        'Authorization': f'Bearer {token}',
        'User-Agent': USER_AGENT
    })
    kwargs['headers'] = headers
    
    # Retry logic estilo MALSync
    for attempt in range(max_retries):
        try:
            rate_limit()
            xbmc.log(f'MAL API: {method} {url} (attempt {attempt + 1})', xbmc.LOGDEBUG)
            
            response = requests.request(method, url, timeout=10, **kwargs)
            
            # Token expirado - intentar refresh
            if response.status_code == 401:
                xbmc.log('MAL API: Token expired, refreshing', xbmc.LOGINFO)
                new_token = refresh_access_token()
                if new_token:
                    headers['Authorization'] = f'Bearer {new_token}'
                    rate_limit()
                    response = requests.request(method, url, timeout=10, **kwargs)
                else:
                    xbmc.log('MAL API: Token refresh failed', xbmc.LOGERROR)
                    return None
                    
            # Rate limit - esperar y reintentar
            if response.status_code == 429:
                wait_time = 2 ** attempt
                xbmc.log(f'MAL API: Rate limited, waiting {wait_time}s', xbmc.LOGWARNING)
                import time
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            xbmc.log(f'MAL API: Request successful ({response.status_code})', xbmc.LOGDEBUG)
            return response
            
        except requests.RequestException as e:
            xbmc.log(f'MAL API: Request failed (attempt {attempt + 1}): {str(e)}', xbmc.LOGWARNING)
            if attempt == max_retries - 1:
                xbmc.log('MAL API: All retry attempts failed', xbmc.LOGERROR)
                return None
            import time
            time.sleep(1)
            
    return None

def get_user_anime_list(limit=100):
    params = {'limit': limit, 'fields': 'list_status,num_episodes,status,mean'}
    url = f"{API_BASE_URL}/users/@me/animelist"
    response = _make_request('GET', url, params=params)
    return response.json() if response else None

def update_anime_status(anime_id, status, num_watched_episodes=None):
    data = {'status': status}
    if num_watched_episodes is not None:
        data['num_watched_episodes'] = num_watched_episodes
    url = f"{API_BASE_URL}/anime/{anime_id}/my_list_status"
    response = _make_request('PUT', url, data=data)
    return response is not None
