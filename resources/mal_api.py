import requests
from .config import API_BASE_URL
from .auth import load_access_token

def get_user_anime_list():
    token = load_access_token()
    if not token:
        return None
    headers = {'Authorization': f'Bearer {token}'}
    params = {'limit': 10, 'fields': 'list_status'}
    url = f"{API_BASE_URL}/users/@me/animelist"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def update_anime_status(anime_id, status, num_watched_episodes=None):
    token = load_access_token()
    if not token:
        return False
    headers = {'Authorization': f'Bearer {token}'}
    data = {'status': status}
    if num_watched_episodes is not None:
        data['num_watched_episodes'] = num_watched_episodes
    url = f"{API_BASE_URL}/anime/{anime_id}/my_list_status"
    response = requests.put(url, headers=headers, data=data)
    return response.status_code == 200
