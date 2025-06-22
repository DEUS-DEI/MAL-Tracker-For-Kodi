import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib.parse
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources'))
from resources import auth, mal_api

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params:
        if params.get('action') == 'list':
            list_anime()
        elif params.get('action') == 'update':
            update_anime(params)
        elif params.get('action') == 'auth':
            authenticate()
        elif params.get('action') == 'search':
            search_anime()
        elif params.get('action') == 'details':
            show_anime_details(params)
        else:
            show_main_menu()
    else:
        show_main_menu()

def show_main_menu():
    xbmcplugin.setPluginCategory(HANDLE, 'MAL Tracker')
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=auth', xbmcgui.ListItem('Autenticar con MyAnimeList'), False)
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=list', xbmcgui.ListItem('Ver mi lista de anime'), True)
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=search', xbmcgui.ListItem('Buscar anime'), True)
    xbmcplugin.endOfDirectory(HANDLE)

def search_anime():
    import resources.mal_search as mal_search
    query = xbmcgui.Dialog().input('Buscar anime:')
    if not query:
        xbmcplugin.endOfDirectory(HANDLE)
        return
    results = mal_search.search_anime(query)
    if not results or 'data' not in results:
        xbmcgui.Dialog().notification('MAL Tracker', 'No se encontraron resultados')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    for entry in results['data']:
        anime = entry['node']
        title = anime.get('title', 'Sin título')
        anime_id = anime.get('id')
        li = xbmcgui.ListItem(title)
        url = f"{BASE_URL}?action=details&anime_id={anime_id}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_anime_details(params):
    import resources.mal_search as mal_search
    anime_id = params.get('anime_id')
    if not anime_id:
        xbmcgui.Dialog().notification('MAL Tracker', 'ID de anime no proporcionado')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    details = mal_search.get_anime_details(anime_id)
    if not details:
        xbmcgui.Dialog().notification('MAL Tracker', 'No se pudo obtener detalles')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    info = f"Título: {details.get('title','')}\nEpisodios: {details.get('num_episodes','')}\nEstado: {details.get('status','')}\nRanking: {details.get('rank','')}\nPopularidad: {details.get('popularity','')}\n\n{details.get('synopsis','')}"
    xbmcgui.Dialog().textviewer('Detalles de Anime', info)
    xbmcplugin.endOfDirectory(HANDLE)

def authenticate():
    code = auth.get_authorization_code()
    token = auth.get_access_token(code)
    if token:
        xbmcgui.Dialog().notification('MAL Tracker', 'Autenticación exitosa')
    else:
        xbmcgui.Dialog().notification('MAL Tracker', 'Error en autenticación')

def list_anime():
    anime_list = mal_api.get_user_anime_list()
    if not anime_list or 'data' not in anime_list:
        xbmcgui.Dialog().notification('MAL Tracker', 'No se pudo obtener la lista')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    for entry in anime_list['data']:
        anime = entry['node']
        title = anime.get('title', 'Sin título')
        anime_id = anime.get('id')
        li = xbmcgui.ListItem(title)
        url = f"{BASE_URL}?action=update&anime_id={anime_id}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    xbmcplugin.endOfDirectory(HANDLE)

def update_anime(params):
    anime_id = params.get('anime_id')
    if not anime_id:
        xbmcgui.Dialog().notification('MAL Tracker', 'ID de anime no proporcionado')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    status = xbmcgui.Dialog().input('Nuevo estado (watching, completed, etc):')
    episodes = xbmcgui.Dialog().input('Episodios vistos (opcional):')
    episodes = int(episodes) if episodes.isdigit() else None
    ok = mal_api.update_anime_status(anime_id, status, episodes)
    if ok:
        xbmcgui.Dialog().notification('MAL Tracker', 'Actualización exitosa')
    else:
        xbmcgui.Dialog().notification('MAL Tracker', 'Error al actualizar')
    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    router(sys.argv[2][1:])
