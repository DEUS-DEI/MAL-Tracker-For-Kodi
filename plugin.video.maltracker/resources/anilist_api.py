import requests
from .anilist_auth import load_access_token

ANILIST_API_URL = 'https://graphql.anilist.co'

def _make_request(query, variables=None):
    token = load_access_token()
    if not token:
        return None
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {'query': query}
    if variables:
        data['variables'] = variables
    try:
        response = requests.post(ANILIST_API_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_user_anime_list():
    query = '''
    query {
        Viewer {
            mediaListOptions { scoreFormat }
            lists: MediaListCollection(type: ANIME) {
                lists {
                    name
                    entries {
                        id
                        status
                        score
                        progress
                        media {
                            id
                            title { romaji english }
                            episodes
                            coverImage { medium }
                            meanScore
                        }
                    }
                }
            }
        }
    }
    '''
    return _make_request(query)

def update_anime_status(media_id, status, progress=None, score=None):
    query = '''
    mutation($mediaId: Int, $status: MediaListStatus, $progress: Int, $score: Int) {
        SaveMediaListEntry(mediaId: $mediaId, status: $status, progress: $progress, score: $score) {
            id
            status
            progress
            score
        }
    }
    '''
    variables = {'mediaId': media_id, 'status': status}
    if progress is not None:
        variables['progress'] = progress
    if score is not None:
        variables['score'] = score
    response = _make_request(query, variables)
    return response is not None

def search_anime(query):
    search_query = '''
    query($search: String) {
        Page(page: 1, perPage: 50) {
            media(search: $search, type: ANIME) {
                id
                title { romaji english }
                episodes
                meanScore
                coverImage { medium }
                description
                status
            }
        }
    }
    '''
    return _make_request(search_query, {'search': query})