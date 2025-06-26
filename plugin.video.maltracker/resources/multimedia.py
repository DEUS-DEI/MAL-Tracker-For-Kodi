import xbmc
import xbmcgui
import requests
import re
from . import public_api

def search_youtube_content(query, content_type='opening'):
    """Buscar contenido en YouTube"""
    try:
        # Construir query de búsqueda
        search_terms = {
            'opening': f"{query} opening OP",
            'ending': f"{query} ending ED", 
            'trailer': f"{query} trailer PV",
            'ost': f"{query} OST soundtrack"
        }
        
        search_query = search_terms.get(content_type, f"{query} {content_type}")
        
        # Usar plugin de YouTube si está disponible
        youtube_url = f"plugin://plugin.video.youtube/search/?q={search_query}"
        
        return {
            'url': youtube_url,
            'title': f"{content_type.title()} - {query}",
            'type': content_type
        }
        
    except Exception as e:
        xbmc.log(f'Multimedia: YouTube search error - {str(e)}', xbmc.LOGERROR)
        return None

def get_anime_multimedia(anime_id, anime_title):
    """Obtener contenido multimedia de un anime"""
    multimedia_options = []
    
    # Verificar si YouTube addon está disponible
    youtube_available = check_youtube_addon()
    
    if youtube_available:
        # Openings
        opening = search_youtube_content(anime_title, 'opening')
        if opening:
            multimedia_options.append(opening)
        
        # Endings
        ending = search_youtube_content(anime_title, 'ending')
        if ending:
            multimedia_options.append(ending)
        
        # Trailer
        trailer = search_youtube_content(anime_title, 'trailer')
        if trailer:
            multimedia_options.append(trailer)
        
        # OST
        ost = search_youtube_content(anime_title, 'ost')
        if ost:
            multimedia_options.append(ost)
    
    # Galería de imágenes (usando detalles de API)
    try:
        details = public_api.get_anime_details_public(anime_id)
        if details:
            images = extract_anime_images(details)
            if images:
                multimedia_options.append({
                    'url': 'gallery',
                    'title': f"Galería - {anime_title}",
                    'type': 'gallery',
                    'images': images
                })
    except:
        pass
    
    return multimedia_options

def check_youtube_addon():
    """Verificar si YouTube addon está disponible"""
    try:
        import xbmcaddon
        xbmcaddon.Addon('plugin.video.youtube')
        return True
    except:
        return False

def extract_anime_images(anime_details):
    """Extraer imágenes del anime"""
    images = []
    
    try:
        # Imagen principal
        main_image = anime_details.get('images', {}).get('jpg', {})
        if main_image.get('large_image_url'):
            images.append({
                'url': main_image['large_image_url'],
                'type': 'poster',
                'title': 'Poster Principal'
            })
        
        # Imagen pequeña como thumbnail
        if main_image.get('image_url'):
            images.append({
                'url': main_image['image_url'],
                'type': 'thumbnail',
                'title': 'Thumbnail'
            })
        
        # WebP images si están disponibles
        webp_images = anime_details.get('images', {}).get('webp', {})
        if webp_images.get('large_image_url'):
            images.append({
                'url': webp_images['large_image_url'],
                'type': 'webp_large',
                'title': 'Imagen WebP'
            })
    
    except Exception as e:
        xbmc.log(f'Multimedia: Extract images error - {str(e)}', xbmc.LOGERROR)
    
    return images

def show_multimedia_menu(anime_id, anime_title):
    """Mostrar menú multimedia para un anime"""
    multimedia_options = get_anime_multimedia(anime_id, anime_title)
    
    if not multimedia_options:
        xbmcgui.Dialog().notification('MAL Tracker', 'No hay contenido multimedia disponible')
        return
    
    # Crear opciones de menú
    menu_options = []
    for option in multimedia_options:
        menu_options.append(option['title'])
    
    selected = xbmcgui.Dialog().select(f'Multimedia - {anime_title}:', menu_options)
    
    if selected == -1:
        return
    
    selected_option = multimedia_options[selected]
    play_multimedia_content(selected_option)

def play_multimedia_content(content):
    """Reproducir contenido multimedia"""
    try:
        if content['type'] == 'gallery':
            show_image_gallery(content['images'])
        elif content['url'].startswith('plugin://plugin.video.youtube'):
            # Abrir YouTube
            xbmc.executebuiltin(f'Container.Update({content["url"]})')
        else:
            xbmcgui.Dialog().notification('MAL Tracker', f'Reproduciendo: {content["title"]}')
            
    except Exception as e:
        xbmc.log(f'Multimedia: Play content error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def show_image_gallery(images):
    """Mostrar galería de imágenes"""
    if not images:
        xbmcgui.Dialog().notification('MAL Tracker', 'No hay imágenes disponibles')
        return
    
    # Crear lista de imágenes para el diálogo
    image_list = []
    for img in images:
        image_list.append(img['url'])
    
    # Mostrar galería usando diálogo de imágenes
    try:
        # Usar diálogo personalizado para mostrar imágenes
        image_info = "GALERÍA DE IMÁGENES:\n\n"
        for i, img in enumerate(images, 1):
            image_info += f"{i}. {img['title']} ({img['type']})\n"
        
        xbmcgui.Dialog().textviewer('Galería de Imágenes', image_info)
        
    except Exception as e:
        xbmc.log(f'Multimedia: Image gallery error - {str(e)}', xbmc.LOGERROR)

def get_anime_soundtrack_info(anime_id):
    """Obtener información de soundtrack"""
    try:
        details = public_api.get_anime_details_public(anime_id)
        if not details:
            return None
        
        # Extraer información de tema musical si está disponible
        theme_info = details.get('theme', {})
        
        soundtrack_info = {
            'openings': theme_info.get('openings', []),
            'endings': theme_info.get('endings', []),
            'title': details.get('title', 'Unknown')
        }
        
        return soundtrack_info
        
    except Exception as e:
        xbmc.log(f'Multimedia: Soundtrack info error - {str(e)}', xbmc.LOGERROR)
        return None

def show_soundtrack_info(anime_id, anime_title):
    """Mostrar información de soundtrack"""
    soundtrack = get_anime_soundtrack_info(anime_id)
    
    if not soundtrack:
        xbmcgui.Dialog().notification('MAL Tracker', 'No hay información de soundtrack')
        return
    
    info = f"SOUNDTRACK - {anime_title}\n\n"
    
    if soundtrack['openings']:
        info += "OPENINGS:\n"
        for i, op in enumerate(soundtrack['openings'], 1):
            info += f"{i}. {op}\n"
        info += "\n"
    
    if soundtrack['endings']:
        info += "ENDINGS:\n"
        for i, ed in enumerate(soundtrack['endings'], 1):
            info += f"{i}. {ed}\n"
    
    if not soundtrack['openings'] and not soundtrack['endings']:
        info += "No hay información de temas musicales disponible."
    
    xbmcgui.Dialog().textviewer('Información de Soundtrack', info)

def create_multimedia_context_menu(anime_id, anime_title):
    """Crear menú contextual multimedia"""
    context_menu = []
    
    # Verificar disponibilidad de YouTube
    if check_youtube_addon():
        context_menu.extend([
            ('🎵 Ver Opening', f'RunPlugin(plugin://plugin.video.maltracker/?action=play_multimedia&anime_id={anime_id}&type=opening&title={anime_title})'),
            ('🎶 Ver Ending', f'RunPlugin(plugin://plugin.video.maltracker/?action=play_multimedia&anime_id={anime_id}&type=ending&title={anime_title})'),
            ('🎬 Ver Trailer', f'RunPlugin(plugin://plugin.video.maltracker/?action=play_multimedia&anime_id={anime_id}&type=trailer&title={anime_title})'),
        ])
    
    context_menu.extend([
        ('🖼️ Ver Galería', f'RunPlugin(plugin://plugin.video.maltracker/?action=multimedia_gallery&anime_id={anime_id}&title={anime_title})'),
        ('🎼 Info Soundtrack', f'RunPlugin(plugin://plugin.video.maltracker/?action=soundtrack_info&anime_id={anime_id}&title={anime_title})')
    ])
    
    return context_menu