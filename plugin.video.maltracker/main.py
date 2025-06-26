import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import sys
import urllib.parse
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources'))
from resources import auth, mal_api, mal_search, config_importer, public_api, streaming_integration, local_database, sync_manager, advanced_search, notifications, ai_recommendations, multimedia, personalization, gamification, backup_system

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
        elif params.get('action') == 'search_public':
            search_anime_public()
        elif params.get('action') == 'top_anime':
            show_top_anime()
        elif params.get('action') == 'seasonal':
            show_seasonal_anime()
        elif params.get('action') == 'details_public':
            show_anime_details_public(params)
        elif params.get('action') == 'schedule':
            show_schedule_menu()
        elif params.get('action') == 'schedule_day':
            show_schedule_day(params)
        elif params.get('action') == 'upcoming':
            show_upcoming_anime()
        elif params.get('action') == 'streaming_status':
            streaming_integration.show_streaming_menu()
        elif params.get('action') == 'watch_anime':
            watch_anime(params)
        elif params.get('action') == 'install_streaming':
            streaming_integration.show_install_addons_info()
        elif params.get('action') == 'my_list':
            show_my_list()
        elif params.get('action') == 'local_stats':
            show_local_stats()
        elif params.get('action') == 'sync_now':
            sync_now()
        elif params.get('action') == 'add_to_list':
            add_to_local_list(params)
        elif params.get('action') == 'update_local':
            update_local_anime(params)
        elif params.get('action') == 'list_by_status':
            show_list_by_status(params)
        elif params.get('action') == 'advanced_search':
            advanced_search.show_advanced_search_menu()
        elif params.get('action') == 'notifications':
            notifications.configure_notifications()
        elif params.get('action') == 'ai_recommendations':
            show_ai_recommendations()
        elif params.get('action') == 'achievements':
            gamification.show_achievements_menu()
        elif params.get('action') == 'personalization':
            personalization.show_personalization_menu()
        elif params.get('action') == 'backup':
            backup_system.show_backup_menu()
        elif params.get('action') == 'multimedia':
            show_multimedia_content(params)
        else:
            show_main_menu()
    else:
        show_main_menu()

def show_main_menu():
    # Inicializar todos los sistemas
    local_database.init_database()
    notifications.init_notifications()
    personalization.init_personalization()
    gamification.init_gamification()
    backup_system.init_backup_system()
    
    # Auto-sincronización, notificaciones y gamificación
    sync_manager.auto_sync_if_authenticated()
    notifications.check_for_notifications()
    gamification.check_achievements()
    gamification.update_activity_streak()
    
    xbmcplugin.setPluginCategory(HANDLE, 'MAL Tracker')
    xbmcplugin.setContent(HANDLE, 'files')
    
    # Mi Lista Local (siempre disponible)
    local_stats = local_database.get_local_stats()
    list_title = f"📚 Mi Lista ({local_stats.get('total_anime', 0)} anime)"
    li = xbmcgui.ListItem(list_title)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=my_list', li, True)
    
    # Estadísticas locales
    stats_title = f"📈 Estadísticas (Completados: {local_stats.get('completed', 0)})"
    li = xbmcgui.ListItem(stats_title)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=local_stats', li, False)
    
    # Búsqueda mejorada
    li = xbmcgui.ListItem('🔍 Búsqueda avanzada')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=advanced_search', li, True)
    
    li = xbmcgui.ListItem('Buscar anime (básico)')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=search_public', li, True)
    
    li = xbmcgui.ListItem('Top anime')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=top_anime', li, True)
    
    li = xbmcgui.ListItem('Anime de temporada')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=seasonal', li, True)
    
    li = xbmcgui.ListItem('Calendario semanal')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=schedule', li, True)
    
    li = xbmcgui.ListItem('Próximos estrenos')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=upcoming', li, True)
    
    # Estado de streaming
    available_addons = streaming_integration.get_available_streaming_addons()
    streaming_status = f"📺 Streaming ({len(available_addons)}/2 disponibles)"
    li = xbmcgui.ListItem(streaming_status)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=streaming_status', li, False)
    
    # Estado de sincronización
    sync_status = sync_manager.get_sync_status()
    if sync_status['is_authenticated']:
        sync_title = f"🔄 Sincronizar ({sync_status['unsynced_count']} pendientes)"
        li = xbmcgui.ListItem(sync_title)
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=sync_now', li, False)
    else:
        li = xbmcgui.ListItem('🔒 Autenticar para sincronizar')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=auth', li, False)
    
    # Recomendaciones IA
    li = xbmcgui.ListItem('🤖 Recomendaciones IA')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=ai_recommendations', li, True)
    
    # Gamificación
    game_status = gamification.get_gamification_status()
    game_title = f"🎮 Logros (Nivel {game_status['level']}, {game_status['achievements_unlocked']}/{game_status['total_achievements']})"
    li = xbmcgui.ListItem(game_title)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=achievements', li, False)
    
    # Personalización
    person_status = personalization.get_personalization_status()
    person_title = f"🎨 Personalizar ({person_status['theme']} - {person_status['layout']})"
    li = xbmcgui.ListItem(person_title)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=personalization', li, False)
    
    # Backup
    li = xbmcgui.ListItem('💾 Backup y Exportación')
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=backup', li, False)
    
    # Notificaciones
    notif_status = notifications.get_notifications_status()
    notif_title = f"🔔 Notificaciones ({notif_status['active_count']}/3 activas)"
    li = xbmcgui.ListItem(notif_title)
    li.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=notifications', li, False)
    
    if is_authenticated():
        li = xbmcgui.ListItem('Ver mi lista de anime')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=list', li, True)
        
        li = xbmcgui.ListItem('Buscar anime (privado)')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=search', li, True)
        
        li = xbmcgui.ListItem('Reautenticar')
        li.setArt({'icon': ICON, 'fanart': FANART})
        xbmcplugin.addDirectoryItem(HANDLE, f'{BASE_URL}?action=auth', li, False)
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

def search_anime_public():
    query = xbmcgui.Dialog().input('Buscar anime:')
    if not query:
        xbmcplugin.endOfDirectory(HANDLE)
        return
    try:
        xbmcplugin.setPluginCategory(HANDLE, f'Búsqueda pública: {query}')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        results = public_api.search_anime_public(query)
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se encontraron resultados')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        for anime in results['data']:
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('mal_id')
            score = anime.get('score', 0)
            episodes = anime.get('episodes', 0)
            image_url = anime.get('images', {}).get('jpg', {}).get('image_url', ICON)
            
            # Crear botón de reproducción estilo Netflix
            watch_button = streaming_integration.create_watch_button(title, anime_id)
            
            li = xbmcgui.ListItem(title)
            li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Puntuación: {score}/10\nEpisodios: {episodes}\n\n{watch_button["title"]}',
                'rating': float(score) if score else 0,
                'episode': episodes if episodes else 0,
                'mediatype': 'tvshow'
            })
            
            # Menú contextual con opciones
            context_menu = []
            context_menu.append(('Ver detalles', f'RunPlugin({BASE_URL}?action=details_public&anime_id={anime_id})'))
            context_menu.append(('Agregar a mi lista', f'RunPlugin({BASE_URL}?action=add_to_list&anime_id={anime_id}&title={urllib.parse.quote(title)})'))
            
            if watch_button['available']:
                context_menu.append((watch_button['title'], f'RunPlugin({BASE_URL}?action=watch_anime&anime_title={urllib.parse.quote(title)}&anime_id={anime_id})'))
            else:
                context_menu.append((watch_button['title'], f'RunPlugin({BASE_URL}?action=install_streaming)'))
            
            li.addContextMenuItems(context_menu)
            
            url = f"{BASE_URL}?action=details_public&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en búsqueda pública - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def show_top_anime():
    try:
        xbmcplugin.setPluginCategory(HANDLE, 'Top Anime')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        results = public_api.get_top_anime_public()
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener el top')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        for anime in results['data']:
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('mal_id')
            score = anime.get('score', 0)
            rank = anime.get('rank', 0)
            image_url = anime.get('images', {}).get('jpg', {}).get('image_url', ICON)
            
            # Botón de reproducción para top anime
            watch_button = streaming_integration.create_watch_button(title, anime_id)
            
            li = xbmcgui.ListItem(f"#{rank} - {title}")
            li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Ranking: #{rank}\nPuntuación: {score}/10\n\n{watch_button["title"]}',
                'rating': float(score) if score else 0,
                'mediatype': 'tvshow'
            })
            
            # Menú contextual
            context_menu = []
            context_menu.append(('Ver detalles', f'RunPlugin({BASE_URL}?action=details_public&anime_id={anime_id})'))
            if watch_button['available']:
                context_menu.append((watch_button['title'], f'RunPlugin({BASE_URL}?action=watch_anime&anime_title={urllib.parse.quote(title)}&anime_id={anime_id})'))
            else:
                context_menu.append((watch_button['title'], f'RunPlugin({BASE_URL}?action=install_streaming)'))
            li.addContextMenuItems(context_menu)
            
            url = f"{BASE_URL}?action=details_public&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en top anime - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def show_seasonal_anime():
    try:
        xbmcplugin.setPluginCategory(HANDLE, 'Anime de Temporada')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        results = public_api.get_seasonal_anime_public()
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener anime de temporada')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        for anime in results['data']:
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('mal_id')
            score = anime.get('score', 0)
            status = anime.get('status', 'Unknown')
            image_url = anime.get('images', {}).get('jpg', {}).get('image_url', ICON)
            
            li = xbmcgui.ListItem(title)
            li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Estado: {status}\nPuntuación: {score}/10',
                'rating': float(score) if score else 0,
                'mediatype': 'tvshow'
            })
            url = f"{BASE_URL}?action=details_public&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en anime de temporada - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def show_anime_details_public(params):
    anime_id = params.get('anime_id')
    if not anime_id:
        xbmcgui.Dialog().notification(ADDON_NAME, 'ID de anime no proporcionado')
        xbmcplugin.endOfDirectory(HANDLE)
        return
    try:
        details = public_api.get_anime_details_public(anime_id)
        if not details:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener detalles')
            xbmcplugin.endOfDirectory(HANDLE)
            return
        genres = ', '.join([g['name'] for g in details.get('genres', [])]) or 'N/A'
        studios = ', '.join([s['name'] for s in details.get('studios', [])]) or 'N/A'
        score = details.get('score', 'N/A')
        info = f"Título: {details.get('title','N/A')}\nEpisodios: {details.get('episodes','N/A')}\nEstado: {details.get('status','N/A')}\nPuntuación: {score}\nRanking: {details.get('rank','N/A')}\nPopularidad: {details.get('popularity','N/A')}\nGéneros: {genres}\nEstudios: {studios}\nFecha inicio: {details.get('aired',{}).get('from','N/A')}\n\n{details.get('synopsis','Sin sinopsis disponible')}"
        # Mostrar detalles con opción de ver
        if xbmcgui.Dialog().yesno('Detalles de Anime', info, nolabel='Cerrar', yeslabel='▶ Ver Anime'):
            streaming_integration.show_streaming_options(details.get('title', 'Anime'))
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error detalles públicos - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    xbmcplugin.endOfDirectory(HANDLE)

def show_schedule_menu():
    """Menú de calendario semanal"""
    xbmcplugin.setPluginCategory(HANDLE, 'Calendario Semanal')
    xbmcplugin.setContent(HANDLE, 'files')
    
    days = [
        ('Lunes', 'monday'),
        ('Martes', 'tuesday'), 
        ('Miércoles', 'wednesday'),
        ('Jueves', 'thursday'),
        ('Viernes', 'friday'),
        ('Sábado', 'saturday'),
        ('Domingo', 'sunday'),
        ('Toda la semana', 'all')
    ]
    
    for day_name, day_code in days:
        li = xbmcgui.ListItem(day_name)
        li.setArt({'icon': ICON, 'fanart': FANART})
        url = f"{BASE_URL}?action=schedule_day&day={day_code}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_schedule_day(params):
    """Mostrar anime de un día específico"""
    day = params.get('day')
    day_name = {
        'monday': 'Lunes', 'tuesday': 'Martes', 'wednesday': 'Miércoles',
        'thursday': 'Jueves', 'friday': 'Viernes', 'saturday': 'Sábado',
        'sunday': 'Domingo', 'all': 'Toda la semana'
    }.get(day, day)
    
    try:
        xbmcplugin.setPluginCategory(HANDLE, f'Calendario - {day_name}')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        
        schedule_day = None if day == 'all' else day
        results = public_api.get_schedule_public(schedule_day)
        
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener el calendario')
            xbmcplugin.endOfDirectory(HANDLE)
            return
            
        # Procesar datos según estructura de respuesta
        anime_list = []
        if day == 'all':
            # Para toda la semana, los datos están organizados por día
            for day_data in results['data']:
                anime_list.extend(day_data)
        else:
            anime_list = results['data']
            
        for anime in anime_list:
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('mal_id')
            score = anime.get('score', 0)
            broadcast = anime.get('broadcast', {})
            time_info = broadcast.get('time', 'Hora no disponible') if broadcast else 'Sin horario'
            image_url = anime.get('images', {}).get('jpg', {}).get('image_url', ICON)
            
            li = xbmcgui.ListItem(f"{title} ({time_info})")
            li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Horario: {time_info}\nPuntuación: {score}/10',
                'rating': float(score) if score else 0,
                'mediatype': 'tvshow'
            })
            url = f"{BASE_URL}?action=details_public&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
            
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en calendario - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_upcoming_anime():
    """Mostrar próximos estrenos"""
    try:
        xbmcplugin.setPluginCategory(HANDLE, 'Próximos Estrenos')
        xbmcplugin.setContent(HANDLE, 'tvshows')
        results = public_api.get_upcoming_anime_public()
        
        if not results or 'data' not in results:
            xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudo obtener próximos estrenos')
            xbmcplugin.endOfDirectory(HANDLE)
            return
            
        for anime in results['data']:
            title = anime.get('title', 'Sin título')
            anime_id = anime.get('mal_id')
            score = anime.get('score', 0)
            aired = anime.get('aired', {})
            start_date = aired.get('from', 'Fecha no disponible') if aired else 'Sin fecha'
            image_url = anime.get('images', {}).get('jpg', {}).get('image_url', ICON)
            
            li = xbmcgui.ListItem(title)
            li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': FANART})
            li.setInfo('video', {
                'title': title,
                'plot': f'Estreno: {start_date}\nPuntuación: {score}/10',
                'rating': float(score) if score else 0,
                'mediatype': 'tvshow'
            })
            url = f"{BASE_URL}?action=details_public&anime_id={anime_id}"
            xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
            
    except Exception as e:
        xbmc.log(f'{ADDON_NAME}: Error en próximos estrenos - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification(ADDON_NAME, f'Error: {str(e)}')
    
    xbmcplugin.endOfDirectory(HANDLE)

def watch_anime(params):
    """Iniciar reproducción de anime en addons de streaming"""
    anime_title = params.get('anime_title', '')
    anime_id = params.get('anime_id', '')
    
    if not anime_title:
        xbmcgui.Dialog().notification(ADDON_NAME, 'Título de anime no proporcionado')
        return
    
    # Mostrar opciones de streaming
    streaming_integration.show_streaming_options(anime_title)

def show_my_list():
    """Mostrar lista local de anime"""
    xbmcplugin.setPluginCategory(HANDLE, 'Mi Lista Local')
    xbmcplugin.setContent(HANDLE, 'files')
    
    # Opciones por estado
    statuses = [
        ('Viendo', 'watching'),
        ('Completado', 'completed'),
        ('En pausa', 'on_hold'),
        ('Abandonado', 'dropped'),
        ('Planeo ver', 'plan_to_watch'),
        ('Toda la lista', 'all')
    ]
    
    for status_name, status_code in statuses:
        count = len(local_database.get_local_anime_list(status_code if status_code != 'all' else None))
        li = xbmcgui.ListItem(f'{status_name} ({count})')
        li.setArt({'icon': ICON, 'fanart': FANART})
        url = f"{BASE_URL}?action=list_by_status&status={status_code}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_list_by_status(params):
    """Mostrar anime por estado"""
    status = params.get('status')
    status_names = {
        'watching': 'Viendo',
        'completed': 'Completado', 
        'on_hold': 'En pausa',
        'dropped': 'Abandonado',
        'plan_to_watch': 'Planeo ver',
        'all': 'Toda la lista'
    }
    
    xbmcplugin.setPluginCategory(HANDLE, f'Mi Lista - {status_names.get(status, status)}')
    xbmcplugin.setContent(HANDLE, 'tvshows')
    
    anime_list = local_database.get_local_anime_list(status if status != 'all' else None)
    
    for anime in anime_list:
        title = anime['title']
        progress = f"{anime['episodes_watched']}/{anime['total_episodes']}"
        sync_icon = '✓' if anime['synced'] else '⏳'
        
        li = xbmcgui.ListItem(f"{sync_icon} {title} ({progress})")
        li.setArt({'thumb': anime['image_url'], 'poster': anime['image_url'], 'fanart': FANART})
        li.setInfo('video', {
            'title': title,
            'plot': f"Estado: {anime['status']}\nProgreso: {progress}\nPuntuación: {anime['score']}/10\nSincronizado: {'Sí' if anime['synced'] else 'No'}",
            'rating': float(anime['score']) if anime['score'] else 0,
            'episode': anime['total_episodes'],
            'mediatype': 'tvshow'
        })
        
        # Menú contextual
        context_menu = [
            ('Actualizar estado', f'RunPlugin({BASE_URL}?action=update_local&anime_id={anime["mal_id"]})')
        ]
        li.addContextMenuItems(context_menu)
        
        url = f"{BASE_URL}?action=update_local&anime_id={anime['mal_id']}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(HANDLE)

def show_local_stats():
    """Mostrar estadísticas locales"""
    stats = local_database.get_local_stats()
    activity = local_database.get_activity_log(10)
    
    info = f"ESTADÍSTICAS LOCALES:\n\n"
    info += f"Total de anime: {stats.get('total_anime', 0)}\n"
    info += f"Completados: {stats.get('completed', 0)}\n"
    info += f"Viendo: {stats.get('watching', 0)}\n"
    info += f"Puntuación promedio: {stats.get('avg_score', 0)}\n"
    info += f"Episodios vistos: {stats.get('total_episodes', 0)}\n\n"
    
    info += "ACTIVIDAD RECIENTE:\n"
    for act in activity[:5]:
        info += f"• {act[0]}: {act[1] or 'Anime'} ({act[4]})\n"
    
    xbmcgui.Dialog().textviewer('Estadísticas Locales', info)

def add_to_local_list(params):
    """Agregar anime a lista local"""
    anime_id = params.get('anime_id')
    title = params.get('title', 'Anime')
    
    if not anime_id:
        xbmcgui.Dialog().notification(ADDON_NAME, 'ID de anime no proporcionado')
        return
    
    # Obtener detalles del anime
    details = public_api.get_anime_details_public(anime_id)
    if not details:
        xbmcgui.Dialog().notification(ADDON_NAME, 'No se pudieron obtener detalles')
        return
    
    # Seleccionar estado
    status_options = ['Planeo ver', 'Viendo', 'Completado', 'En pausa', 'Abandonado']
    status_codes = ['plan_to_watch', 'watching', 'completed', 'on_hold', 'dropped']
    
    selected = xbmcgui.Dialog().select('Selecciona estado:', status_options)
    if selected == -1:
        return
    
    # Agregar a lista local
    success = local_database.add_anime_to_list(details, status_codes[selected])
    
    if success:
        xbmcgui.Dialog().notification(ADDON_NAME, f'Agregado: {title}')
    else:
        xbmcgui.Dialog().notification(ADDON_NAME, 'Error al agregar')

def update_local_anime(params):
    """Actualizar anime en lista local"""
    anime_id = params.get('anime_id')
    if not anime_id:
        return
    
    # Menú de actualización
    options = ['Cambiar estado', 'Actualizar episodios', 'Cambiar puntuación', 'Eliminar de lista']
    selected = xbmcgui.Dialog().select('Actualizar anime:', options)
    
    if selected == 0:  # Cambiar estado
        status_options = ['Viendo', 'Completado', 'En pausa', 'Abandonado', 'Planeo ver']
        status_codes = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']
        status_idx = xbmcgui.Dialog().select('Nuevo estado:', status_options)
        if status_idx != -1:
            local_database.update_anime_status(int(anime_id), status_codes[status_idx])
            xbmcgui.Dialog().notification(ADDON_NAME, 'Estado actualizado')
            
    elif selected == 1:  # Actualizar episodios
        episodes = xbmcgui.Dialog().input('Episodios vistos:')
        if episodes and episodes.isdigit():
            local_database.update_anime_status(int(anime_id), None, int(episodes))
            xbmcgui.Dialog().notification(ADDON_NAME, 'Episodios actualizados')
            
    elif selected == 2:  # Cambiar puntuación
        score = xbmcgui.Dialog().input('Puntuación (1-10):')
        if score and score.isdigit() and 1 <= int(score) <= 10:
            local_database.update_anime_status(int(anime_id), None, None, int(score))
            xbmcgui.Dialog().notification(ADDON_NAME, 'Puntuación actualizada')
            
    elif selected == 3:  # Eliminar
        if xbmcgui.Dialog().yesno('Confirmar', '¿Eliminar anime de la lista?'):
            local_database.remove_anime_from_list(int(anime_id))
            xbmcgui.Dialog().notification(ADDON_NAME, 'Anime eliminado')
    
    # Refrescar vista
    xbmc.executebuiltin('Container.Refresh')

def sync_now():
    """Sincronizar ahora con MAL"""
    if not auth.load_access_token():
        xbmcgui.Dialog().notification(ADDON_NAME, 'Debes autenticarte primero')
        return
    
    # Mostrar progreso
    progress = xbmcgui.DialogProgress()
    progress.create('Sincronizando', 'Sincronizando con MyAnimeList...')
    
    success = sync_manager.sync_with_mal()
    
    progress.close()
    
    if success:
        xbmcgui.Dialog().notification(ADDON_NAME, 'Sincronización completada')
    else:
        xbmcgui.Dialog().notification(ADDON_NAME, 'Error en sincronización')
    
    # Refrescar menú
    xbmc.executebuiltin('Container.Refresh')

def show_ai_recommendations():
    """Mostrar recomendaciones de IA"""
    xbmcplugin.setPluginCategory(HANDLE, 'Recomendaciones IA')
    xbmcplugin.setContent(HANDLE, 'files')
    
    options = [
        '🎯 Recomendaciones personalizadas',
        '🔥 Trending ahora',
        '🔍 Anime similar a...',
        '🎨 Por género favorito'
    ]
    
    for i, option in enumerate(options):
        li = xbmcgui.ListItem(option)
        li.setArt({'icon': ICON, 'fanart': FANART})
        url = f"{BASE_URL}?action=ai_rec_type&type={i}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_multimedia_content(params):
    """Mostrar contenido multimedia"""
    anime_id = params.get('anime_id')
    anime_title = params.get('title', 'Anime')
    
    if anime_id:
        multimedia.show_multimedia_menu(anime_id, anime_title)

if __name__ == '__main__':
    router(sys.argv[2][1:])