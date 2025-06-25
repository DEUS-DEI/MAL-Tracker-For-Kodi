import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import sys
import urllib.parse
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources'))
from resources import auth, mal_api, mal_search, config_importer

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
ADDON_NAME = ADDON.getAddonInfo('name')
ICON = ADDON.getAddonInfo('icon')
FANART = ADDON.getAddonInfo('fanart')

def is_authenticated():
    return auth.load_access_token() is not None

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
        elif params.get('action') == 'import_config':
            config_importer.import_config_from_text()
        else:
            show_main_menu()
    else:
        show_main_menu()

def show_main_menu():
    xbmcplugin.setPluginCategory(HANDLE, 'MAL Tracker')
    xbmcplugin.setContent(HANDLE, 'files')
    if is_authenticated():
        li = xbmcgui.ListItem('Ver mi lista de anime')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=list', li, True)
        
        li = xbmcgui.ListItem('Buscar anime')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=search', li, True)
        
        li = xbmcgui.ListItem('Reautenticar')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=auth', li, False)
        
        li = xbmcgui.ListItem('Importar configuración')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=import_config', li, False)
    else:
        li = xbmcgui.ListItem('Autenticar con MyAnimeList')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=auth', li, False)
        
        li = xbmcgui.ListItem('Importar configuración')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=import_config', li, False)
    xbmcplugin.endOfDirectory(HANDLE)

def search_anime():
    if not is_authenticated():
        xbmcgui.Dialog().notification(ADDON_NAME, 'Debes autenticarte primero')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    query = xbmcgui.Dialog().input('Buscar anime:')
    if not query:
        xbmcplugin.endOfDirectory(HANDLE)
        return
    try:
        xbmcplugin.setPluginCategory(HANDLE, f'Búsqueda: {query}')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        results = mal_search.search_anime(query)
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se encontraron resultados')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        for entry in results['data']:
            anime = entry['node']
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('id')
            score = anime.get('mean', 0)
            episodes = anime.get('num_episodes', 0)
            picture = anime.get('main_picture', {}).get('medium', ICON)
            
            li = xbmcgui.ListItem(title)
            li.setArt({'thumb': picture, 'poster': picture, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Puntuación: {score}/10\nEpisodios: {episodes}',
                'rating': float(score) if score else 0,
                'episode': episodes if episodes else 0,
                'mediatype': 'tvshow'
            })
            url = f"{BASE_URL}?action=details&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en búsqueda - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def show_anime_details(params):
    anime_id = params.get('anime_id')
    if not anime_id:
        xbmcgui.Dialog().notification(ADDON_NAME, 'ID de anime no proporcionado')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    try:
        details = mal_search.get_anime_details(anime_id)
        if not details:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener detalles')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        genres = ', '.join([g['name'] for g in details.get('genres', [])]) or 'N/A'
        studios = ', '.join([s['name'] for s in details.get('studios', [])]) or 'N/A'
        score = details.get('mean', 'N/A')
        info = f"Título: {details.get('title','N/A')}\nEpisodios: {details.get('num_episodes','N/A')}\nEstado: {details.get('status','N/A')}\nPuntuación: {score}\nRanking: {details.get('rank','N/A')}\nPopularidad: {details.get('popularity','N/A')}\nGéneros: {genres}\nEstudios: {studios}\nFecha inicio: {details.get('start_date','N/A')}\n\n{details.get('synopsis','Sin sinopsis disponible')}"
        xbmcgui.Dialog().textviewer('Detalles de Anime', info)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error detalles - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def authenticate():
    try:
        code, code_verifier = auth.get_authorization_code()
        if not code:
            xbmcgui.Dialog().notification(ADDON_NAME, 'Autenticación cancelada')
            return
        token = auth.get_access_token(code, code_verifier)
        if token:
            xbmc.log(f'{ADDON_NAME}: Autenticación exitosa', xbmc.LOGINFO)
            xbmcgui.Dialog().notification(ADDON_NAME, 'Autenticación exitosa')
        else:
            xbmc.log(f'{ADDON_NAME}: Error en autenticación', xbmc.LOGERROR)
            xbmcgui.Dialog().notification(ADDON_NAME, 'Error en autenticación')
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error autenticación - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')

def list_anime():
    if not is_authenticated():
        xbmcgui.Dialog().notification(ADDON_NAME, 'Debes autenticarte primero')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    try:
        xbmcplugin.setPluginCategory(HANDLE, 'Mi Lista de Anime')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        anime_list = mal_api.get_user_anime_list()
        if not anime_list or 'data' not in anime_list:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener la lista')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        for entry in anime_list['data']:
            anime = entry['node']
            list_status = entry.get('list_status', {})
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('id')
            status = list_status.get('status', 'unknown')
            watched = list_status.get('num_episodes_watched', 0)
            total = anime.get('num_episodes', 0)
            score = list_status.get('score', 0)
            picture = anime.get('main_picture', {}).get('medium', ICON)
            
            li = xbmcgui.ListItem(title)
            li.setArt({'thumb': picture, 'poster': picture, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Estado: {status}\nProgreso: {watched}/{total}',
                'rating': float(score) if score else 0,
                'episode': total if total else 0,
                'playcount': 1 if status == 'completed' else 0,
                'mediatype': 'tvshow'
            })
            url = f"{BASE_URL}?action=update&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_PLAYCOUNT)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en lista - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def update_anime(params):
    anime_id = params.get('anime_id')
    if not anime_id:
        xbmcgui.Dialog().notification(ADDON_NAME, 'ID de anime no proporcionado')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    status_labels = ['Viendo', 'Completado', 'En pausa', 'Abandonado', 'Planeo ver']
    status_options = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']
    status_idx = xbmcgui.Dialog().select('Selecciona estado:', status_labels)
    if status_idx == -1:
        xbmcplugin.endOfDirectory(HANDLE)
        return
    status = status_options[status_idx]
    episodes = xbmcgui.Dialog().input('Episodios vistos (opcional):')
    episodes = int(episodes) if episodes.isdigit() else None
    try:
        ok = mal_api.update_anime_status(anime_id, status, episodes)
        if ok:
            xbmc.log(f'{ADDON_NAME}: Anime {anime_id} actualizado a {status}', xbmc.LOGINFO)
            xbmcgui.Dialog().notification(ADDON_NAME, 'Actualización exitosa')
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmc.log(f'{ADDON_NAME}: Error actualizando anime {anime_id}', xbmc.LOGERROR)
            xbmcgui.Dialog().notification(ADDON_NAME, 'Error al actualizar')
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error actualización - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    router(sys.argv[2][1:])