import json
import time
import requests
import xbmc
import xbmcgui
from .config import USER_AGENT, rate_limit

# Soporte multi-idioma
LANGUAGES = {
    'en': 'English',
    'es': 'Español', 
    'ja': '日本語',
    'fr': 'Français',
    'de': 'Deutsch',
    'pt': 'Português',
    'it': 'Italiano',
    'ru': 'Русский',
    'ko': '한국어',
    'zh': '中文'
}

# Eventos de anime japoneses
ANIME_EVENTS = {
    'comiket': {
        'name': 'Comiket',
        'dates': ['2024-08-11', '2024-12-29'],
        'description': 'El evento de doujinshi más grande del mundo'
    },
    'anime_expo': {
        'name': 'Anime Expo',
        'dates': ['2024-07-04'],
        'description': 'Convención de anime más grande de Norteamérica'
    },
    'anime_japan': {
        'name': 'AnimeJapan',
        'dates': ['2024-03-23'],
        'description': 'Festival oficial de anime de Japón'
    }
}

def setup_language():
    """Configurar idioma del addon"""
    current_lang = get_current_language()
    
    lang_options = []
    lang_codes = []
    
    for code, name in LANGUAGES.items():
        marker = ' ✓' if code == current_lang else ''
        lang_options.append(f"{name}{marker}")
        lang_codes.append(code)
    
    selected = xbmcgui.Dialog().select('Seleccionar Idioma:', lang_options)
    
    if selected != -1:
        new_lang = lang_codes[selected]
        save_language_setting(new_lang)
        
        xbmcgui.Dialog().notification('MAL Tracker', f'Idioma cambiado a: {LANGUAGES[new_lang]}')
        xbmc.executebuiltin('Container.Refresh')

def get_current_language():
    """Obtener idioma actual"""
    try:
        from .config import TOKEN_PATH
        import os
        
        lang_file = os.path.join(TOKEN_PATH, 'language.json')
        
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('language', 'en')
                
    except:
        pass
    
    return 'en'  # Default

def save_language_setting(lang_code):
    """Guardar configuración de idioma"""
    try:
        from .config import TOKEN_PATH
        import os
        
        lang_file = os.path.join(TOKEN_PATH, 'language.json')
        
        data = {
            'language': lang_code,
            'updated': int(time.time())
        }
        
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        xbmc.log(f'Global Features: Save language error - {str(e)}', xbmc.LOGERROR)

def show_anime_calendar():
    """Mostrar calendario de eventos de anime"""
    current_time = time.time()
    
    info = "📅 CALENDARIO DE EVENTOS DE ANIME\n\n"
    
    for event_id, event_data in ANIME_EVENTS.items():
        info += f"🎪 {event_data['name']}\n"
        info += f"   {event_data['description']}\n"
        
        # Mostrar próximas fechas
        for date_str in event_data['dates']:
            try:
                event_time = time.mktime(time.strptime(date_str, '%Y-%m-%d'))
                days_until = int((event_time - current_time) / 86400)
                
                if days_until > 0:
                    info += f"   📅 {date_str} (en {days_until} días)\n"
                elif days_until > -30:  # Eventos recientes
                    info += f"   📅 {date_str} (hace {abs(days_until)} días)\n"
                    
            except:
                info += f"   📅 {date_str}\n"
        
        info += "\n"
    
    info += "💡 Mantente al día con los eventos más importantes del anime!"
    
    xbmcgui.Dialog().textviewer('Calendario de Eventos', info)

def get_seasonal_trends():
    """Obtener tendencias de temporada"""
    try:
        # Usar Jikan API para obtener anime de temporada
        rate_limit()
        url = "https://api.jikan.moe/v4/seasons/now"
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data:
                # Analizar tendencias
                trends = analyze_seasonal_trends(data['data'])
                return trends
                
    except Exception as e:
        xbmc.log(f'Global Features: Seasonal trends error - {str(e)}', xbmc.LOGERROR)
    
    return {}

def analyze_seasonal_trends(anime_data):
    """Analizar tendencias de anime de temporada"""
    try:
        trends = {
            'top_genres': {},
            'top_studios': {},
            'avg_score': 0,
            'total_anime': len(anime_data)
        }
        
        all_genres = []
        all_studios = []
        scores = []
        
        for anime in anime_data:
            # Géneros
            if anime.get('genres'):
                for genre in anime['genres']:
                    all_genres.append(genre['name'])
            
            # Estudios
            if anime.get('studios'):
                for studio in anime['studios']:
                    all_studios.append(studio['name'])
            
            # Puntuaciones
            if anime.get('score'):
                scores.append(anime['score'])
        
        # Top géneros
        from collections import Counter
        genre_counts = Counter(all_genres)
        trends['top_genres'] = dict(genre_counts.most_common(5))
        
        # Top estudios
        studio_counts = Counter(all_studios)
        trends['top_studios'] = dict(studio_counts.most_common(5))
        
        # Promedio de puntuación
        if scores:
            trends['avg_score'] = round(sum(scores) / len(scores), 2)
        
        return trends
        
    except Exception as e:
        xbmc.log(f'Global Features: Analyze trends error - {str(e)}', xbmc.LOGERROR)
        return {}

def show_seasonal_trends():
    """Mostrar tendencias de temporada"""
    trends = get_seasonal_trends()
    
    if not trends:
        xbmcgui.Dialog().notification('Tendencias', 'No se pudieron obtener tendencias')
        return
    
    info = "📊 TENDENCIAS DE TEMPORADA\n\n"
    
    info += f"📺 Total de anime: {trends.get('total_anime', 0)}\n"
    info += f"⭐ Puntuación promedio: {trends.get('avg_score', 0)}/10\n\n"
    
    # Top géneros
    info += "🎭 GÉNEROS MÁS POPULARES:\n"
    for genre, count in trends.get('top_genres', {}).items():
        info += f"• {genre}: {count} anime\n"
    info += "\n"
    
    # Top estudios
    info += "🏢 ESTUDIOS MÁS ACTIVOS:\n"
    for studio, count in trends.get('top_studios', {}).items():
        info += f"• {studio}: {count} anime\n"
    
    xbmcgui.Dialog().textviewer('Tendencias de Temporada', info)

def setup_streaming_services():
    """Configurar servicios de streaming"""
    services = [
        {'name': 'Crunchyroll', 'url': 'https://crunchyroll.com', 'type': 'subscription'},
        {'name': 'Funimation', 'url': 'https://funimation.com', 'type': 'subscription'},
        {'name': 'Netflix', 'url': 'https://netflix.com', 'type': 'subscription'},
        {'name': 'Hulu', 'url': 'https://hulu.com', 'type': 'subscription'},
        {'name': 'AnimeLab', 'url': 'https://animelab.com', 'type': 'subscription'}
    ]
    
    info = "📺 SERVICIOS DE STREAMING RECOMENDADOS\n\n"
    
    for service in services:
        info += f"🎬 {service['name']}\n"
        info += f"   {service['url']}\n"
        info += f"   Tipo: {service['type']}\n\n"
    
    info += "💡 Configura tus servicios favoritos para mejor integración!"
    
    xbmcgui.Dialog().textviewer('Servicios de Streaming', info)

def show_global_menu():
    """Mostrar menú de características globales"""
    options = [
        '🌐 Cambiar idioma',
        '📅 Calendario de eventos',
        '📊 Tendencias de temporada',
        '📺 Servicios de streaming',
        '🎌 Cultura japonesa',
        '🌍 Configuración regional'
    ]
    
    selected = xbmcgui.Dialog().select('Características Globales:', options)
    
    if selected == 0:
        setup_language()
    elif selected == 1:
        show_anime_calendar()
    elif selected == 2:
        show_seasonal_trends()
    elif selected == 3:
        setup_streaming_services()
    elif selected == 4:
        show_japanese_culture()
    elif selected == 5:
        setup_regional_config()

def show_japanese_culture():
    """Mostrar información de cultura japonesa"""
    info = "🎌 CULTURA JAPONESA Y ANIME\n\n"
    
    info += "🏮 FESTIVALES TRADICIONALES:\n"
    info += "• Hanami (春) - Primavera, flores de cerezo\n"
    info += "• Tanabata (七夕) - Festival de las estrellas\n"
    info += "• Obon (お盆) - Festival de los ancestros\n"
    info += "• Matsuri (祭り) - Festivales locales\n\n"
    
    info += "🎭 TÉRMINOS ANIME COMUNES:\n"
    info += "• Otaku (オタク) - Fan dedicado\n"
    info += "• Senpai (先輩) - Superior/veterano\n"
    info += "• Kouhai (後輩) - Junior/novato\n"
    info += "• Kawaii (可愛い) - Lindo/adorable\n\n"
    
    info += "📚 GÉNEROS ÚNICOS:\n"
    info += "• Isekai - Otro mundo\n"
    info += "• Moe - Personajes adorables\n"
    info += "• Ecchi - Contenido sugerente\n"
    info += "• Shounen/Shoujo - Para chicos/chicas\n"
    
    xbmcgui.Dialog().textviewer('Cultura Japonesa', info)

def setup_regional_config():
    """Configurar opciones regionales"""
    regions = ['América', 'Europa', 'Asia', 'Oceanía', 'África']
    
    selected = xbmcgui.Dialog().select('Seleccionar región:', regions)
    
    if selected != -1:
        region = regions[selected]
        
        # Configurar según región
        regional_settings = {
            'region': region,
            'timezone_offset': get_timezone_offset(region),
            'preferred_services': get_regional_services(region)
        }
        
        save_regional_config(regional_settings)
        xbmcgui.Dialog().notification('Regional', f'Configurado para: {region}')

def get_timezone_offset(region):
    """Obtener offset de zona horaria por región"""
    offsets = {
        'América': -5,  # EST
        'Europa': 1,    # CET
        'Asia': 9,      # JST
        'Oceanía': 10,  # AEST
        'África': 2     # CAT
    }
    return offsets.get(region, 0)

def get_regional_services(region):
    """Obtener servicios recomendados por región"""
    services = {
        'América': ['Crunchyroll', 'Funimation', 'Netflix'],
        'Europa': ['Crunchyroll', 'Netflix', 'Wakanim'],
        'Asia': ['Crunchyroll', 'Bilibili', 'iQIYI'],
        'Oceanía': ['AnimeLab', 'Crunchyroll', 'Netflix'],
        'África': ['Crunchyroll', 'Netflix']
    }
    return services.get(region, ['Crunchyroll'])

def save_regional_config(config):
    """Guardar configuración regional"""
    try:
        from .config import TOKEN_PATH
        import os
        
        config_file = os.path.join(TOKEN_PATH, 'regional.json')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
    except Exception as e:
        xbmc.log(f'Global Features: Save regional config error - {str(e)}', xbmc.LOGERROR)