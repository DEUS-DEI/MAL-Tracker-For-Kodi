import requests
from .config import API_BASE_URL, USER_AGENT, rate_limit
from .auth import load_access_token, refresh_access_token

def _make_request(method, url, **kwargs):
    token = load_access_token()
    if not token:
        return None
    headers = kwargs.get('headers', {})
    headers.update({
        'Authorization': f'Bearer {token}',
        'User-Agent': USER_AGENT
    })
    kwargs['headers'] = headers
    rate_limit()
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        if response.status_code == 401:
            new_token = refresh_access_token()
            if new_token:
                headers['Authorization'] = f'Bearer {new_token}'
                rate_limit()
                response = requests.request(method, url, timeout=10, **kwargs)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None

def search_anime(query, limit=50):
    params = {'q': query, 'limit': limit, 'fields': 'id,title,main_picture,mean,num_episodes,status'}
    url = f"{API_BASE_URL}/anime"
    response = _make_request('GET', url, params=params)
    return response.json() if response else None

def get_anime_details(anime_id):
    params = {'fields': 'id,title,main_picture,synopsis,mean,rank,popularity,num_episodes,status,genres,start_date,end_date,studios'}
    url = f"{API_BASE_URL}/anime/{anime_id}"
    response = _make_request('GET', url, params=params)
    return response.json() if response else None
