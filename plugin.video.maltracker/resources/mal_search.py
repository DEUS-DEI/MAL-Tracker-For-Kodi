import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import API_BASE_URL
from auth import load_access_token

def search_anime(query, limit=10):
    token = load_access_token()
    if not token:
        return None
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'limit': limit, 'fields': 'id,title,main_picture'}
    url = f"{API_BASE_URL}/anime"
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

def get_anime_details(anime_id):
    token = load_access_token()
    if not token:
        return None
    headers = {'Authorization': f'Bearer {token}'}
    params = {'fields': 'id,title,main_picture,synopsis,mean,rank,popularity,num_episodes,status,genres'}
    url = f"{API_BASE_URL}/anime/{anime_id}"
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None
