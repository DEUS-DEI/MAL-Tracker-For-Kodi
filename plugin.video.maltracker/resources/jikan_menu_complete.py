import xbmcplugin
import xbmcgui
import xbmc
from .jikan_complete import JikanComplete

def show_complete_jikan_menu(handle, base_url, icon, fanart):
    """Menú completo de Jikan con todas las funciones"""
    xbmcplugin.setPluginCategory(handle, 'Jikan API Completa')
    xbmcplugin.setContent(handle, 'files')
    
    menu_items = [
        ('🎲 Aleatorio', 'jikan_random_menu'),
        ('🔍 Búsqueda Avanzada', 'jikan_search_menu'),
        ('🏆 Rankings', 'jikan_top_menu'),
        ('📅 Temporadas', 'jikan_seasons_menu'),
        ('⏰ Horarios', 'jikan_schedules_menu'),
        ('👥 Personajes', 'jikan_characters_menu'),
        ('👤 Personas', 'jikan_people_menu'),
        ('📚 Manga', 'jikan_manga_menu'),
        ('🏢 Productores', 'jikan_producers_menu'),
        ('👥 Clubes', 'jikan_clubs_menu'),
        ('📺 Videos Recientes', 'jikan_watch_menu'),
        ('⭐ Reviews', 'jikan_reviews_menu'),
        ('💡 Recomendaciones', 'jikan_recommendations_menu'),
        ('👤 Usuarios', 'jikan_users_menu')
    ]
    
    for title, action in menu_items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    
    xbmcplugin.endOfDirectory(handle)

def show_random_menu(handle, base_url, icon, fanart):
    """Menú de contenido aleatorio"""
    xbmcplugin.setPluginCategory(handle, 'Contenido Aleatorio')
    xbmcplugin.setContent(handle, 'files')
    
    items = [
        ('🎌 Anime Aleatorio', 'show_random_anime'),
        ('📚 Manga Aleatorio', 'show_random_manga'),
        ('👥 Personaje Aleatorio', 'show_random_character'),
        ('👤 Persona Aleatoria', 'show_random_person'),
        ('👤 Usuario Aleatorio', 'show_random_user')
    ]
    
    for title, action in items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        xbmcplugin.addDirectoryItem(handle, url, li, False)
    
    xbmcplugin.endOfDirectory(handle)

def show_watch_menu(handle, base_url, icon, fanart):
    """Menú de videos y episodios"""
    xbmcplugin.setPluginCategory(handle, 'Videos y Episodios')
    xbmcplugin.setContent(handle, 'files')
    
    items = [
        ('📺 Episodios Recientes', 'recent_episodes'),
        ('🎬 Promos Recientes', 'recent_promos'),
        ('🔥 Episodios Populares', 'popular_episodes'),
        ('⭐ Promos Populares', 'popular_promos')
    ]
    
    for title, action in items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    
    xbmcplugin.endOfDirectory(handle)

def show_recent_episodes(handle, base_url, icon, fanart):
    """Mostrar episodios recientes"""
    try:
        result = JikanComplete.get_watch_recent_episodes()
        if result and 'data' in result:
            xbmcplugin.setPluginCategory(handle, 'Episodios Recientes')
            xbmcplugin.setContent(handle, 'episodes')
            
            for episode in result['data']:
                entry = episode.get('entry', {})
                title = entry.get('title', 'Sin título')
                episode_title = episode.get('title', '')
                episode_num = episode.get('episode', '')
                
                display_title = f"{title} - Ep {episode_num}: {episode_title}"
                
                li = xbmcgui.ListItem(display_title)
                li.setArt({'icon': icon, 'fanart': fanart})
                li.setInfo('video', {
                    'title': display_title,
                    'episode': episode_num,
                    'mediatype': 'episode'
                })
                
                anime_id = entry.get('mal_id')
                url = f"{base_url}?action=anime_details&anime_id={anime_id}"
                xbmcplugin.addDirectoryItem(handle, url, li, False)
            
            xbmcplugin.endOfDirectory(handle)
        else:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo episodios')
    except Exception as e:
        xbmc.log(f'Jikan Episodes Error: {str(e)}', xbmc.LOGERROR)

def show_anime_full_details(handle, base_url, icon, fanart, anime_id):
    """Mostrar detalles completos de anime con todas las opciones"""
    try:
        anime = JikanComplete.get_anime_full(anime_id)
        if not anime or 'data' not in anime:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo detalles')
            return
        
        data = anime['data']
        title = data.get('title', 'Sin título')
        
        xbmcplugin.setPluginCategory(handle, f'Detalles: {title}')
        xbmcplugin.setContent(handle, 'files')
        
        # Opciones disponibles
        options = [
            ('📋 Información Completa', f'show_anime_info&anime_id={anime_id}'),
            ('👥 Personajes', f'show_anime_characters&anime_id={anime_id}'),
            ('🎭 Staff', f'show_anime_staff&anime_id={anime_id}'),
            ('📺 Episodios', f'show_anime_episodes&anime_id={anime_id}'),
            ('📰 Noticias', f'show_anime_news&anime_id={anime_id}'),
            ('🎬 Videos', f'show_anime_videos&anime_id={anime_id}'),
            ('🖼️ Imágenes', f'show_anime_pictures&anime_id={anime_id}'),
            ('📊 Estadísticas', f'show_anime_statistics&anime_id={anime_id}'),
            ('💡 Recomendaciones', f'show_anime_recommendations&anime_id={anime_id}'),
            ('⭐ Reviews', f'show_anime_reviews&anime_id={anime_id}'),
            ('🔗 Relacionados', f'show_anime_relations&anime_id={anime_id}'),
            ('🎵 Temas', f'show_anime_themes&anime_id={anime_id}'),
            ('🌐 Enlaces Externos', f'show_anime_external&anime_id={anime_id}'),
            ('📺 Streaming', f'show_anime_streaming&anime_id={anime_id}')
        ]
        
        for title, action in options:
            li = xbmcgui.ListItem(title)
            li.setArt({'icon': icon, 'fanart': fanart})
            url = f"{base_url}?action={action}"
            xbmcplugin.addDirectoryItem(handle, url, li, True)
        
        xbmcplugin.endOfDirectory(handle)
        
    except Exception as e:
        xbmc.log(f'Jikan Full Details Error: {str(e)}', xbmc.LOGERROR)

def show_anime_streaming(handle, base_url, icon, fanart, anime_id):
    """Mostrar plataformas de streaming disponibles"""
    try:
        result = JikanComplete.get_anime_streaming(anime_id)
        if result and 'data' in result:
            streaming_data = result['data']
            
            if not streaming_data:
                xbmcgui.Dialog().notification('Jikan', 'No hay plataformas de streaming disponibles')
                return
            
            info = "🌐 PLATAFORMAS DE STREAMING:\\n\\n"
            for platform in streaming_data:
                name = platform.get('name', 'Desconocido')
                url = platform.get('url', '')
                info += f"• {name}\\n  {url}\\n\\n"
            
            xbmcgui.Dialog().textviewer('Streaming Disponible', info)
        else:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo streaming')
    except Exception as e:
        xbmc.log(f'Jikan Streaming Error: {str(e)}', xbmc.LOGERROR)

def show_user_profile(handle, base_url, icon, fanart, username):
    """Mostrar perfil completo de usuario"""
    try:
        result = JikanComplete.get_user_profile(username)
        if result and 'data' in result:
            user = result['data']
            
            info = f"👤 PERFIL DE USUARIO: {username}\\n\\n"
            info += f"Nombre: {user.get('username', 'N/A')}\\n"
            info += f"Último acceso: {user.get('last_online', 'N/A')}\\n"
            info += f"Género: {user.get('gender', 'N/A')}\\n"
            info += f"Cumpleaños: {user.get('birthday', 'N/A')}\\n"
            info += f"Ubicación: {user.get('location', 'N/A')}\\n"
            info += f"Miembro desde: {user.get('joined', 'N/A')}\\n\\n"
            
            # Estadísticas de anime
            anime_stats = user.get('statistics', {}).get('anime', {})
            if anime_stats:
                info += f"📺 ESTADÍSTICAS ANIME:\\n"
                info += f"• Días viendo: {anime_stats.get('days_watched', 0)}\\n"
                info += f"• Puntuación media: {anime_stats.get('mean_score', 0)}\\n"
                info += f"• Viendo: {anime_stats.get('watching', 0)}\\n"
                info += f"• Completados: {anime_stats.get('completed', 0)}\\n"
                info += f"• En pausa: {anime_stats.get('on_hold', 0)}\\n"
                info += f"• Abandonados: {anime_stats.get('dropped', 0)}\\n"
                info += f"• Planeados: {anime_stats.get('plan_to_watch', 0)}\\n"
                info += f"• Total: {anime_stats.get('total_entries', 0)}\\n\\n"
            
            xbmcgui.Dialog().textviewer(f'Perfil: {username}', info)
        else:
            xbmcgui.Dialog().notification('Jikan', f'Usuario {username} no encontrado')
    except Exception as e:
        xbmc.log(f'Jikan User Profile Error: {str(e)}', xbmc.LOGERROR)