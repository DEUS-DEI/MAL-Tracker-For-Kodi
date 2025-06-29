import xbmcplugin
import xbmcgui
import xbmc
from .jikan_api import JikanAPI

def show_jikan_menu(handle, base_url, icon, fanart):
    """Mostrar menú principal de Jikan"""
    xbmcplugin.setPluginCategory(handle, 'Jikan API - Gratis')
    xbmcplugin.setContent(handle, 'files')
    
    menu_items = [
        ('🎲 Anime Aleatorio', 'jikan_random'),
        ('🔥 Top Anime', 'top_anime'),
        ('📅 Temporada Actual', 'current_season'),
        ('⏰ Horarios Semanales', 'schedules'),
        ('🎭 Géneros', 'jikan_genres'),
        ('👥 Personajes', 'jikan_characters'),
        ('🔍 Búsqueda Avanzada', 'jikan_search'),
        ('📰 Noticias', 'jikan_news'),
        ('📊 Estadísticas', 'jikan_stats')
    ]
    
    for title, action in menu_items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    
    xbmcplugin.endOfDirectory(handle)

def show_random_anime(handle, base_url, icon, fanart):
    """Mostrar anime aleatorio"""
    try:
        result = JikanAPI.get_random_anime()
        if result and 'data' in result:
            anime = result['data']
            title = anime.get('title', 'Sin título')
            
            info = f"🎲 ANIME ALEATORIO\\n\\n"
            info += f"Título: {title}\\n"
            info += f"Episodios: {anime.get('episodes', 'N/A')}\\n"
            info += f"Puntuación: {anime.get('score', 'N/A')}/10\\n"
            info += f"Estado: {anime.get('status', 'N/A')}\\n"
            info += f"Año: {anime.get('year', 'N/A')}\\n\\n"
            info += anime.get('synopsis', 'Sin sinopsis')
            
            xbmcgui.Dialog().textviewer(f'Anime Aleatorio: {title}', info)
        else:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo anime aleatorio')
    except Exception as e:
        xbmc.log(f'Jikan Random Error: {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Jikan', f'Error: {str(e)}')

def show_genres_menu(handle, base_url, icon, fanart):
    """Mostrar géneros disponibles"""
    try:
        result = JikanAPI.get_anime_genres()
        if result and 'data' in result:
            xbmcplugin.setPluginCategory(handle, 'Géneros de Anime')
            xbmcplugin.setContent(handle, 'files')
            
            for genre in result['data']:
                name = genre.get('name', 'Sin nombre')
                count = genre.get('count', 0)
                genre_id = genre.get('mal_id')
                
                li = xbmcgui.ListItem(f"{name} ({count} anime)")
                li.setArt({'icon': icon, 'fanart': fanart})
                url = f"{base_url}?action=anime_by_genre&genre_id={genre_id}&genre_name={name}"
                xbmcplugin.addDirectoryItem(handle, url, li, True)
            
            xbmcplugin.endOfDirectory(handle)
        else:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo géneros')
    except Exception as e:
        xbmc.log(f'Jikan Genres Error: {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Jikan', f'Error: {str(e)}')

def show_characters_menu(handle, base_url, icon, fanart):
    """Mostrar top personajes"""
    try:
        result = JikanAPI.get_top_characters()
        if result and 'data' in result:
            xbmcplugin.setPluginCategory(handle, 'Top Personajes')
            xbmcplugin.setContent(handle, 'tvshows')
            
            for character in result['data']:
                name = character.get('name', 'Sin nombre')
                favorites = character.get('favorites', 0)
                image_url = character.get('images', {}).get('jpg', {}).get('image_url', icon)
                
                li = xbmcgui.ListItem(f"{name} ({favorites:,} favoritos)")
                li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': fanart})
                li.setInfo('video', {
                    'title': name,
                    'plot': f'Favoritos: {favorites:,}',
                    'mediatype': 'tvshow'
                })
                
                char_id = character.get('mal_id')
                url = f"{base_url}?action=character_details&char_id={char_id}"
                xbmcplugin.addDirectoryItem(handle, url, li, False)
            
            xbmcplugin.endOfDirectory(handle)
        else:
            xbmcgui.Dialog().notification('Jikan', 'Error obteniendo personajes')
    except Exception as e:
        xbmc.log(f'Jikan Characters Error: {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Jikan', f'Error: {str(e)}')