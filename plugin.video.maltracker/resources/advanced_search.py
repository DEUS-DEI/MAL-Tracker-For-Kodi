import xbmcgui
import xbmc
from . import public_api, local_database

# Géneros disponibles
GENRES = [
    'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy', 'Horror', 'Mystery', 
    'Romance', 'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural', 'Thriller',
    'Mecha', 'Music', 'Psychological', 'School', 'Military', 'Historical'
]

# Años disponibles
YEARS = list(range(2024, 1960, -1))

# Estados de anime
STATUSES = ['airing', 'complete', 'upcoming']

def show_advanced_search_menu():
    """Mostrar menú de búsqueda avanzada"""
    options = [
        'Buscar por género',
        'Buscar por año',
        'Buscar por estudio',
        'Buscar por puntuación mínima',
        'Filtros combinados',
        'Búsqueda en mi lista local'
    ]
    
    selected = xbmcgui.Dialog().select('Búsqueda Avanzada:', options)
    
    if selected == 0:
        search_by_genre()
    elif selected == 1:
        search_by_year()
    elif selected == 2:
        search_by_studio()
    elif selected == 3:
        search_by_score()
    elif selected == 4:
        combined_filters()
    elif selected == 5:
        search_local_list()

def search_by_genre():
    """Buscar anime por género"""
    selected = xbmcgui.Dialog().select('Selecciona género:', GENRES)
    if selected == -1:
        return
    
    genre = GENRES[selected]
    
    try:
        # Usar Jikan API para búsqueda por género
        url = f"https://api.jikan.moe/v4/anime"
        params = {
            'genres': get_genre_id(genre),
            'order_by': 'popularity',
            'sort': 'asc',
            'limit': 25
        }
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            return format_search_results(results, f'Género: {genre}')
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Genre search error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def search_by_year():
    """Buscar anime por año"""
    selected = xbmcgui.Dialog().select('Selecciona año:', [str(year) for year in YEARS])
    if selected == -1:
        return
    
    year = YEARS[selected]
    
    try:
        url = f"https://api.jikan.moe/v4/seasons/{year}/winter"
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            return format_search_results(results, f'Año: {year}')
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Year search error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def search_by_studio():
    """Buscar anime por estudio"""
    studio_name = xbmcgui.Dialog().input('Nombre del estudio:')
    if not studio_name:
        return
    
    try:
        # Buscar estudios primero
        url = f"https://api.jikan.moe/v4/producers"
        params = {'q': studio_name, 'limit': 10}
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            studios = response.json().get('data', [])
            if studios:
                studio_names = [s['name'] for s in studios]
                selected = xbmcgui.Dialog().select('Selecciona estudio:', studio_names)
                
                if selected != -1:
                    studio_id = studios[selected]['mal_id']
                    search_anime_by_producer(studio_id, studios[selected]['name'])
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Studio search error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def search_by_score():
    """Buscar anime por puntuación mínima"""
    score = xbmcgui.Dialog().input('Puntuación mínima (1-10):')
    if not score or not score.replace('.', '').isdigit():
        return
    
    min_score = float(score)
    if min_score < 1 or min_score > 10:
        xbmcgui.Dialog().notification('MAL Tracker', 'Puntuación debe ser entre 1 y 10')
        return
    
    try:
        url = f"https://api.jikan.moe/v4/anime"
        params = {
            'min_score': min_score,
            'order_by': 'score',
            'sort': 'desc',
            'limit': 25
        }
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            return format_search_results(results, f'Puntuación ≥ {min_score}')
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Score search error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def search_local_list():
    """Buscar en lista local"""
    query = xbmcgui.Dialog().input('Buscar en mi lista:')
    if not query:
        return
    
    local_list = local_database.get_local_anime_list()
    results = []
    
    for anime in local_list:
        if query.lower() in anime['title'].lower():
            results.append(anime)
    
    return format_local_results(results, f'En mi lista: "{query}"')

def combined_filters():
    """Filtros combinados"""
    filters = {}
    
    # Seleccionar múltiples filtros
    filter_options = ['Género', 'Año', 'Puntuación mínima', 'Estado', 'Tipo']
    selected_filters = xbmcgui.Dialog().multiselect('Selecciona filtros:', filter_options)
    
    if not selected_filters:
        return
    
    # Configurar cada filtro
    for filter_idx in selected_filters:
        if filter_idx == 0:  # Género
            genre_idx = xbmcgui.Dialog().select('Género:', GENRES)
            if genre_idx != -1:
                filters['genres'] = get_genre_id(GENRES[genre_idx])
                
        elif filter_idx == 1:  # Año
            year_idx = xbmcgui.Dialog().select('Año:', [str(y) for y in YEARS[:10]])
            if year_idx != -1:
                filters['start_date'] = f"{YEARS[year_idx]}-01-01"
                filters['end_date'] = f"{YEARS[year_idx]}-12-31"
                
        elif filter_idx == 2:  # Puntuación
            score = xbmcgui.Dialog().input('Puntuación mínima:')
            if score and score.replace('.', '').isdigit():
                filters['min_score'] = float(score)
                
        elif filter_idx == 3:  # Estado
            status_idx = xbmcgui.Dialog().select('Estado:', ['En emisión', 'Completado', 'Próximamente'])
            if status_idx != -1:
                filters['status'] = STATUSES[status_idx]
                
        elif filter_idx == 4:  # Tipo
            type_idx = xbmcgui.Dialog().select('Tipo:', ['TV', 'Movie', 'OVA', 'Special', 'ONA'])
            if type_idx != -1:
                filters['type'] = ['tv', 'movie', 'ova', 'special', 'ona'][type_idx]
    
    # Ejecutar búsqueda combinada
    execute_combined_search(filters)

def execute_combined_search(filters):
    """Ejecutar búsqueda con filtros combinados"""
    try:
        url = f"https://api.jikan.moe/v4/anime"
        params = {
            'limit': 25,
            'order_by': 'popularity',
            'sort': 'asc'
        }
        params.update(filters)
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            filter_desc = ', '.join([f"{k}: {v}" for k, v in filters.items()])
            return format_search_results(results, f'Filtros: {filter_desc}')
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Combined search error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')

def get_genre_id(genre_name):
    """Obtener ID de género para API"""
    genre_map = {
        'Action': 1, 'Adventure': 2, 'Comedy': 4, 'Drama': 8, 'Fantasy': 10,
        'Horror': 14, 'Mystery': 7, 'Romance': 22, 'Sci-Fi': 24, 'Slice of Life': 36,
        'Sports': 30, 'Supernatural': 37, 'Thriller': 41, 'Mecha': 18, 'Music': 19,
        'Psychological': 40, 'School': 23, 'Military': 38, 'Historical': 13
    }
    return genre_map.get(genre_name, 1)

def search_anime_by_producer(producer_id, producer_name):
    """Buscar anime por productor/estudio"""
    try:
        url = f"https://api.jikan.moe/v4/anime"
        params = {
            'producers': producer_id,
            'order_by': 'popularity',
            'sort': 'asc',
            'limit': 25
        }
        
        import requests
        from .config import USER_AGENT, rate_limit
        
        rate_limit()
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            return format_search_results(results, f'Estudio: {producer_name}')
        
    except Exception as e:
        xbmc.log(f'Advanced Search: Producer search error - {str(e)}', xbmc.LOGERROR)

def format_search_results(results, title):
    """Formatear resultados de búsqueda para mostrar"""
    # Esta función será llamada desde main.py para mostrar resultados
    return {
        'data': results.get('data', []),
        'title': title,
        'count': len(results.get('data', []))
    }

def format_local_results(results, title):
    """Formatear resultados locales"""
    return {
        'data': results,
        'title': title,
        'count': len(results),
        'local': True
    }