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
