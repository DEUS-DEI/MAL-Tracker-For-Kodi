import sqlite3
import json
import os
import time
import xbmc
import xbmcvfs
from .config import TOKEN_PATH

# Ruta de la base de datos local
DB_PATH = os.path.join(TOKEN_PATH, 'mal_tracker.db')

def init_database():
    """Inicializar base de datos local"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabla de anime local
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_list (
                id INTEGER PRIMARY KEY,
                mal_id INTEGER UNIQUE,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'plan_to_watch',
                episodes_watched INTEGER DEFAULT 0,
                total_episodes INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                start_date TEXT,
                finish_date TEXT,
                notes TEXT,
                image_url TEXT,
                synopsis TEXT,
                genres TEXT,
                studios TEXT,
                year INTEGER,
                season TEXT,
                rating REAL,
                rank INTEGER,
                popularity INTEGER,
                added_date TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de configuración local
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de estadísticas locales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                stat_name TEXT PRIMARY KEY,
                stat_value TEXT,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de historial de actividad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                anime_id INTEGER,
                anime_title TEXT,
                old_value TEXT,
                new_value TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        xbmc.log('MAL Tracker: Database initialized successfully', xbmc.LOGINFO)
        return True
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Database init error - {str(e)}', xbmc.LOGERROR)
        return False

def add_anime_to_list(anime_data, status='plan_to_watch'):
    """Agregar anime a lista local"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO anime_list 
            (mal_id, title, status, total_episodes, image_url, synopsis, genres, studios, year, rating, rank, popularity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            anime_data.get('mal_id'),
            anime_data.get('title'),
            status,
            anime_data.get('episodes', 0),
            anime_data.get('images', {}).get('jpg', {}).get('image_url'),
            anime_data.get('synopsis'),
            json.dumps([g.get('name') for g in anime_data.get('genres', [])]),
            json.dumps([s.get('name') for s in anime_data.get('studios', [])]),
            anime_data.get('year'),
            anime_data.get('score'),
            anime_data.get('rank'),
            anime_data.get('popularity')
        ))
        
        # Log de actividad
        log_activity('add_anime', anime_data.get('mal_id'), anime_data.get('title'), None, status)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Add anime error - {str(e)}', xbmc.LOGERROR)
        return False

def update_anime_status(mal_id, status, episodes_watched=None, score=None):
    """Actualizar estado de anime local"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener valores actuales
        cursor.execute('SELECT status, episodes_watched, score FROM anime_list WHERE mal_id = ?', (mal_id,))
        current = cursor.fetchone()
        
        if not current:
            return False
            
        old_status, old_episodes, old_score = current
        
        # Actualizar valores
        updates = []
        params = []
        
        if status:
            updates.append('status = ?')
            params.append(status)
            
        if episodes_watched is not None:
            updates.append('episodes_watched = ?')
            params.append(episodes_watched)
            
        if score is not None:
            updates.append('score = ?')
            params.append(score)
            
        updates.append('updated_date = CURRENT_TIMESTAMP')
        updates.append('synced = 0')
        
        params.append(mal_id)
        
        cursor.execute(f'''
            UPDATE anime_list 
            SET {', '.join(updates)}
            WHERE mal_id = ?
        ''', params)
        
        # Log de actividad
        if status != old_status:
            log_activity('update_status', mal_id, None, old_status, status)
        if episodes_watched and episodes_watched != old_episodes:
            log_activity('update_episodes', mal_id, None, str(old_episodes), str(episodes_watched))
        if score and score != old_score:
            log_activity('update_score', mal_id, None, str(old_score), str(score))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Update anime error - {str(e)}', xbmc.LOGERROR)
        return False

def get_local_anime_list(status=None):
    """Obtener lista local de anime"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM anime_list WHERE status = ? ORDER BY updated_date DESC', (status,))
        else:
            cursor.execute('SELECT * FROM anime_list ORDER BY updated_date DESC')
            
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
                'synopsis': row[10],
                'genres': json.loads(row[11]) if row[11] else [],
                'studios': json.loads(row[12]) if row[12] else [],
                'year': row[13],
                'rating': row[15],
                'synced': row[20]
            })
            
        return anime_list
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Get list error - {str(e)}', xbmc.LOGERROR)
        return []

def get_local_stats():
    """Obtener estadísticas locales"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Estadísticas básicas
        cursor.execute('SELECT COUNT(*) FROM anime_list')
        total_anime = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE status = "completed"')
        completed = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE status = "watching"')
        watching = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(score) FROM anime_list WHERE score > 0')
        avg_score = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(episodes_watched) FROM anime_list')
        total_episodes = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_anime': total_anime,
            'completed': completed,
            'watching': watching,
            'avg_score': round(avg_score, 2),
            'total_episodes': total_episodes
        }
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Get stats error - {str(e)}', xbmc.LOGERROR)
        return {}

def log_activity(action, anime_id, anime_title, old_value, new_value):
    """Registrar actividad local"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (action, anime_id, anime_title, old_value, new_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (action, anime_id, anime_title, old_value, new_value))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Log activity error - {str(e)}', xbmc.LOGERROR)

def get_activity_log(limit=50):
    """Obtener historial de actividad"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action, anime_title, old_value, new_value, timestamp 
            FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Get activity error - {str(e)}', xbmc.LOGERROR)
        return []

def remove_anime_from_list(mal_id):
    """Eliminar anime de lista local"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT title FROM anime_list WHERE mal_id = ?', (mal_id,))
        result = cursor.fetchone()
        
        if result:
            title = result[0]
            cursor.execute('DELETE FROM anime_list WHERE mal_id = ?', (mal_id,))
            log_activity('remove_anime', mal_id, title, 'in_list', 'removed')
            
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Remove anime error - {str(e)}', xbmc.LOGERROR)
        return False