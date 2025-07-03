import xbmc
import time
from . import local_database, mal_api, auth

def sync_with_mal():
    """Sincronizar datos locales con MyAnimeList"""
    if not auth.load_access_token():
        xbmc.log('MAL Tracker: No authentication for sync', xbmc.LOGWARNING)
        return False
    
    try:
        xbmc.log('MAL Tracker: Starting sync with MAL', xbmc.LOGINFO)
        
        # 1. Descargar lista remota
        remote_list = mal_api.get_user_anime_list(limit=1000)
        if not remote_list or 'data' not in remote_list:
            xbmc.log('MAL Tracker: Failed to get remote list', xbmc.LOGERROR)
            return False
        
        # 2. Sincronizar cada anime remoto
        for entry in remote_list['data']:
            anime = entry['node']
            list_status = entry.get('list_status', {})
            
            # Actualizar en base local
            local_database.add_anime_to_list({
                'mal_id': anime.get('id'),
                'title': anime.get('title'),
                'episodes': anime.get('num_episodes'),
                'images': anime.get('main_picture', {}),
                'synopsis': anime.get('synopsis'),
                'genres': anime.get('genres', []),
                'studios': anime.get('studios', []),
                'score': anime.get('mean'),
                'rank': anime.get('rank'),
                'popularity': anime.get('popularity')
            }, list_status.get('status', 'plan_to_watch'))
            
            # Actualizar progreso
            local_database.update_anime_status(
                anime.get('id'),
                list_status.get('status'),
                list_status.get('num_episodes_watched'),
                list_status.get('score')
            )
        
        # 3. Subir cambios locales no sincronizados
        sync_local_changes()
        
        xbmc.log('MAL Tracker: Sync completed successfully', xbmc.LOGINFO)
        return True
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Sync error - {str(e)}', xbmc.LOGERROR)
        return False

def sync_local_changes():
    """Subir cambios locales no sincronizados"""
    try:
        local_list = local_database.get_local_anime_list()
        
        for anime in local_list:
            if anime['synced'] == 0:  # No sincronizado
                # Intentar actualizar en MAL
                success = mal_api.update_anime_status(
                    anime['mal_id'],
                    anime['status'],
                    anime['episodes_watched']
                )
                
                if success:
                    # Marcar como sincronizado
                    mark_as_synced(anime['mal_id'])
                    xbmc.log(f'MAL Tracker: Synced {anime["title"]}', xbmc.LOGDEBUG)
                    
    except Exception as e:
        xbmc.log(f'MAL Tracker: Sync local changes error - {str(e)}', xbmc.LOGERROR)

def mark_as_synced(mal_id):
    """Marcar anime como sincronizado"""
    import sqlite3
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE anime_list SET synced = 1 WHERE mal_id = ?', (mal_id,))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Mark synced error - {str(e)}', xbmc.LOGERROR)

def auto_sync_if_authenticated():
    """Sincronización automática si hay autenticación"""
    if auth.load_access_token():
        # Sincronizar cada 30 minutos
        last_sync = get_last_sync_time()
        current_time = time.time()
        
        if current_time - last_sync > 1800:  # 30 minutos
            sync_with_mal()
            set_last_sync_time(current_time)

def get_last_sync_time():
    """Obtener timestamp de última sincronización"""
    try:
        import sqlite3
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM local_config WHERE key = "last_sync"')
        result = cursor.fetchone()
        
        conn.close()
        
        return float(result[0]) if result else 0
        
    except:
        return 0

def set_last_sync_time(timestamp):
    """Guardar timestamp de sincronización"""
    try:
        import sqlite3
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO local_config (key, value) 
            VALUES ("last_sync", ?)
        ''', (str(timestamp),))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Set sync time error - {str(e)}', xbmc.LOGERROR)

def get_sync_status():
    """Obtener estado de sincronización"""
    try:
        last_sync = get_last_sync_time()
        is_authenticated = auth.load_access_token() is not None
        
        # Contar elementos no sincronizados
        import sqlite3
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE synced = 0')
        unsynced_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'last_sync': last_sync,
            'is_authenticated': is_authenticated,
            'unsynced_count': unsynced_count,
            'can_sync': is_authenticated and unsynced_count > 0
        }
        
    except Exception as e:
        xbmc.log(f'MAL Tracker: Get sync status error - {str(e)}', xbmc.LOGERROR)
        return {
            'last_sync': 0,
            'is_authenticated': False,
            'unsynced_count': 0,
            'can_sync': False
        }