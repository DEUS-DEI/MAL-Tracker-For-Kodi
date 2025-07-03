import sqlite3
import json
import xbmc
import xbmcgui
from . import local_database

# Estados extendidos
EXTENDED_STATUSES = {
    # Estados básicos
    'watching': {'name': 'Viendo', 'icon': '▶️', 'color': '#4CAF50'},
    'completed': {'name': 'Completado', 'icon': '✅', 'color': '#2196F3'},
    'on_hold': {'name': 'En pausa', 'icon': '⏸️', 'color': '#FF9800'},
    'dropped': {'name': 'Abandonado', 'icon': '❌', 'color': '#F44336'},
    'plan_to_watch': {'name': 'Planeo ver', 'icon': '📋', 'color': '#9C27B0'},
    
    # Estados extendidos
    'rewatching': {'name': 'Reviendo', 'icon': '🔄', 'color': '#00BCD4'},
    'favorite': {'name': 'Favoritos', 'icon': '⭐', 'color': '#FFD700'},
    'priority_high': {'name': 'Prioridad Alta', 'icon': '🔥', 'color': '#FF5722'},
    'priority_low': {'name': 'Prioridad Baja', 'icon': '❄️', 'color': '#607D8B'}
}

# Filtros inteligentes
SMART_FILTERS = {
    'recently_added': {
        'name': 'Agregados Recientemente',
        'icon': '🆕',
        'query': 'ORDER BY added_date DESC LIMIT 20'
    },
    'recently_updated': {
        'name': 'Actualizados Recientemente', 
        'icon': '🔄',
        'query': 'ORDER BY updated_date DESC LIMIT 20'
    },
    'high_rated': {
        'name': 'Mejor Puntuados (8+)',
        'icon': '⭐',
        'query': 'WHERE score >= 8 ORDER BY score DESC'
    },
    'low_rated': {
        'name': 'Peor Puntuados (≤5)',
        'icon': '👎',
        'query': 'WHERE score <= 5 AND score > 0 ORDER BY score ASC'
    },
    'unscored': {
        'name': 'Sin Puntuar',
        'icon': '❓',
        'query': 'WHERE score = 0'
    },
    'almost_complete': {
        'name': 'Casi Completos (80%+)',
        'icon': '🎯',
        'query': 'WHERE status = "watching" AND (episodes_watched * 1.0 / total_episodes) >= 0.8'
    },
    'long_anime': {
        'name': 'Anime Largos (50+ eps)',
        'icon': '📺',
        'query': 'WHERE total_episodes >= 50'
    },
    'short_anime': {
        'name': 'Anime Cortos (≤12 eps)',
        'icon': '⚡',
        'query': 'WHERE total_episodes <= 12 AND total_episodes > 0'
    },
    'current_year': {
        'name': 'De Este Año',
        'icon': '📅',
        'query': 'WHERE year = strftime("%Y", "now")'
    },
    'old_school': {
        'name': 'Clásicos (Pre-2000)',
        'icon': '📼',
        'query': 'WHERE year < 2000'
    }
}

# Listas por género
GENRE_LISTS = {
    'action': {'name': 'Acción', 'icon': '⚔️'},
    'romance': {'name': 'Romance', 'icon': '💕'},
    'comedy': {'name': 'Comedia', 'icon': '😂'},
    'drama': {'name': 'Drama', 'icon': '🎭'},
    'fantasy': {'name': 'Fantasía', 'icon': '🧙'},
    'horror': {'name': 'Terror', 'icon': '👻'},
    'sci_fi': {'name': 'Sci-Fi', 'icon': '🚀'},
    'slice_of_life': {'name': 'Slice of Life', 'icon': '🌸'}
}

def get_advanced_list_menu():
    """Obtener menú de listas avanzadas"""
    menu_items = []
    
    # Estados básicos con contadores
    for status_id, status_info in EXTENDED_STATUSES.items():
        count = get_anime_count_by_status(status_id)
        if count > 0 or status_id in ['watching', 'completed', 'plan_to_watch']:
            menu_items.append({
                'title': f"{status_info['icon']} {status_info['name']} ({count})",
                'action': 'list_by_status',
                'status': status_id,
                'count': count
            })
    
    # Separador
    menu_items.append({'title': '─── Filtros Inteligentes ───', 'separator': True})
    
    # Filtros inteligentes
    for filter_id, filter_info in SMART_FILTERS.items():
        count = get_smart_filter_count(filter_id)
        if count > 0:
            menu_items.append({
                'title': f"{filter_info['icon']} {filter_info['name']} ({count})",
                'action': 'smart_filter',
                'filter': filter_id,
                'count': count
            })
    
    # Separador
    menu_items.append({'title': '─── Por Género ───', 'separator': True})
    
    # Listas por género
    for genre_id, genre_info in GENRE_LISTS.items():
        count = get_genre_count(genre_id)
        if count > 0:
            menu_items.append({
                'title': f"{genre_info['icon']} {genre_info['name']} ({count})",
                'action': 'list_by_genre',
                'genre': genre_id,
                'count': count
            })
    
    return menu_items

def get_anime_count_by_status(status):
    """Obtener contador de anime por estado"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE status = ?', (status,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    except:
        return 0

def get_smart_filter_count(filter_id):
    """Obtener contador para filtro inteligente"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        filter_info = SMART_FILTERS[filter_id]
        query = f"SELECT COUNT(*) FROM anime_list {filter_info['query']}"
        
        cursor.execute(query)
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    except:
        return 0

def get_genre_count(genre):
    """Obtener contador por género"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # CORREGIDO: Usar parámetros seguros
        cursor.execute('''
            SELECT COUNT(*) FROM anime_list 
            WHERE genres LIKE ?
        ''', (f'%{genre}%',))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def get_anime_by_smart_filter(filter_id):
    """Obtener anime por filtro inteligente"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        filter_info = SMART_FILTERS[filter_id]
        query = f"SELECT * FROM anime_list {filter_info['query']}"
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        # Convertir a formato compatible
        anime_list = []
        for row in results:
            anime_list.append({
                'mal_id': row[1],
                'title': row[2],
                'status': row[3],
                'episodes_watched': row[4],
                'total_episodes': row[5],
                'score': row[6],
                'image_url': row[9],
                'genres': json.loads(row[11]) if row[11] else [],
                'year': row[13],
                'synced': row[20]
            })
        
        return anime_list
    except Exception as e:
        xbmc.log(f'Advanced Lists: Smart filter error - {str(e)}', xbmc.LOGERROR)
        return []

def get_anime_by_genre(genre):
    """Obtener anime por género"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM anime_list 
            WHERE genres LIKE ?
            ORDER BY score DESC, title ASC
        ''', (f'%{genre}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convertir a formato compatible
        anime_list = []
        for row in results:
            anime_list.append({
                'mal_id': row[1],
                'title': row[2],
                'status': row[3],
                'episodes_watched': row[4],
                'total_episodes': row[5],
                'score': row[6],
                'image_url': row[9],
                'genres': json.loads(row[11]) if row[11] else [],
                'year': row[13],
                'synced': row[20]
            })
        
        return anime_list
    except Exception as e:
        xbmc.log(f'Advanced Lists: Genre filter error - {str(e)}', xbmc.LOGERROR)
        return []

def create_custom_list(name, criteria):
    """Crear lista personalizada"""
    try:
        # Implementar creación de listas personalizadas
        # Por ahora, usar filtros predefinidos
        pass
    except Exception as e:
        xbmc.log(f'Advanced Lists: Create custom list error - {str(e)}', xbmc.LOGERROR)

def get_list_statistics():
    """Obtener estadísticas de listas"""
    try:
        stats = {}
        
        # Contadores por estado
        for status_id in EXTENDED_STATUSES.keys():
            stats[status_id] = get_anime_count_by_status(status_id)
        
        # Estadísticas adicionales
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Promedio de puntuación por estado
        cursor.execute('''
            SELECT status, AVG(score) 
            FROM anime_list 
            WHERE score > 0 
            GROUP BY status
        ''')
        
        avg_scores = dict(cursor.fetchall())
        stats['avg_scores'] = avg_scores
        
        conn.close()
        return stats
        
    except Exception as e:
        xbmc.log(f'Advanced Lists: Statistics error - {str(e)}', xbmc.LOGERROR)
        return {}