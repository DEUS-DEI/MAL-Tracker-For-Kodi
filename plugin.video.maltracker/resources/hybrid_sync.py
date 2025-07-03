import xbmc
import sqlite3
from . import local_database, mal_api, auth

# Estados compatibles con MAL API
MAL_COMPATIBLE_STATUSES = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']

# Estados solo locales (no sincronizables)
LOCAL_ONLY_STATUSES = ['rewatching', 'favorite', 'priority_high', 'priority_low']

def hybrid_sync_with_mal():
    """Sincronización híbrida que preserva datos locales únicos"""
    if not auth.load_access_token():
        xbmc.log('Hybrid Sync: No authentication', xbmc.LOGWARNING)
        return False
    
    try:
        xbmc.log('Hybrid Sync: Starting hybrid sync', xbmc.LOGINFO)
        
        # 1. Descargar lista remota de MAL
        remote_list = mal_api.get_user_anime_list(limit=1000)
        if not remote_list or 'data' not in remote_list:
            return False
        
        # 2. Sincronizar datos compatibles
        sync_compatible_data(remote_list)
        
        # 3. Subir cambios locales compatibles
        upload_compatible_changes()
        
        # 4. Preservar datos locales únicos
        preserve_local_extensions()
        
        xbmc.log('Hybrid Sync: Completed successfully', xbmc.LOGINFO)
        return True
        
    except Exception as e:
        xbmc.log(f'Hybrid Sync: Error - {str(e)}', xbmc.LOGERROR)
        return False

def sync_compatible_data(remote_list):
    """Sincronizar solo datos compatibles con MAL"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        for entry in remote_list['data']:
            anime = entry['node']
            list_status = entry.get('list_status', {})
            mal_id = anime.get('id')
            mal_status = list_status.get('status', 'plan_to_watch')
            
            # Solo procesar estados compatibles
            if mal_status in MAL_COMPATIBLE_STATUSES:
                # Verificar si existe localmente
                cursor.execute('SELECT status FROM anime_list WHERE mal_id = ?', (mal_id,))
                local_result = cursor.fetchone()
                
                if local_result:
                    local_status = local_result[0]
                    
                    # Solo actualizar si el estado local es compatible
                    if local_status in MAL_COMPATIBLE_STATUSES:
                        cursor.execute('''
                            UPDATE anime_list 
                            SET status = ?, episodes_watched = ?, score = ?, synced = 1
                            WHERE mal_id = ?
                        ''', (
                            mal_status,
                            list_status.get('num_episodes_watched', 0),
                            list_status.get('score', 0),
                            mal_id
                        ))
                else:
                    # Agregar nuevo anime desde MAL
                    local_database.add_anime_to_list({
                        'mal_id': mal_id,
                        'title': anime.get('title'),
                        'episodes': anime.get('num_episodes'),
                        'images': anime.get('main_picture', {}),
                        'synopsis': anime.get('synopsis'),
                        'genres': anime.get('genres', []),
                        'studios': anime.get('studios', []),
                        'score': anime.get('mean'),
                        'rank': anime.get('rank'),
                        'popularity': anime.get('popularity')
                    }, mal_status)
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        xbmc.log(f'Hybrid Sync: Compatible data error - {str(e)}', xbmc.LOGERROR)

def upload_compatible_changes():
    """Subir solo cambios compatibles con MAL"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Obtener anime no sincronizado con estados compatibles
        cursor.execute('''
            SELECT mal_id, status, episodes_watched, score 
            FROM anime_list 
            WHERE synced = 0 AND status IN ({})
        '''.format(','.join(['?' for _ in MAL_COMPATIBLE_STATUSES])), MAL_COMPATIBLE_STATUSES)
        
        unsynced_anime = cursor.fetchall()
        
        for mal_id, status, episodes_watched, score in unsynced_anime:
            # Intentar actualizar en MAL
            success = mal_api.update_anime_status(mal_id, status, episodes_watched)
            
            if success:
                # Marcar como sincronizado
                cursor.execute('UPDATE anime_list SET synced = 1 WHERE mal_id = ?', (mal_id,))
                xbmc.log(f'Hybrid Sync: Uploaded {mal_id}', xbmc.LOGDEBUG)
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        xbmc.log(f'Hybrid Sync: Upload changes error - {str(e)}', xbmc.LOGERROR)

def preserve_local_extensions():
    """Preservar extensiones locales que no existen en MAL"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Mantener estados locales únicos como no sincronizados
        for status in LOCAL_ONLY_STATUSES:
            cursor.execute('''
                UPDATE anime_list 
                SET synced = 0 
                WHERE status = ?
            ''', (status,))
        
        conn.commit()
        conn.close()
        
        xbmc.log('Hybrid Sync: Local extensions preserved', xbmc.LOGDEBUG)
        
    except Exception as e:
        xbmc.log(f'Hybrid Sync: Preserve extensions error - {str(e)}', xbmc.LOGERROR)

def get_sync_compatibility_status():
    """Obtener estado de compatibilidad de sincronización"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Contar anime por tipo de estado
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status IN ({}) THEN 1 ELSE 0 END) as compatible,
                SUM(CASE WHEN status IN ({}) THEN 1 ELSE 0 END) as local_only,
                COUNT(*) as total
            FROM anime_list
        '''.format(
            ','.join(['?' for _ in MAL_COMPATIBLE_STATUSES]),
            ','.join(['?' for _ in LOCAL_ONLY_STATUSES])
        ), MAL_COMPATIBLE_STATUSES + LOCAL_ONLY_STATUSES)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'compatible': result[0] if result else 0,
            'local_only': result[1] if result else 0,
            'total': result[2] if result else 0,
            'sync_percentage': round((result[0] / result[2] * 100) if result and result[2] > 0 else 0, 1)
        }
        
    except Exception as e:
        xbmc.log(f'Hybrid Sync: Compatibility status error - {str(e)}', xbmc.LOGERROR)
        return {'compatible': 0, 'local_only': 0, 'total': 0, 'sync_percentage': 0}

def show_sync_compatibility_info():
    """Mostrar información de compatibilidad de sincronización"""
    import xbmcgui
    
    status = get_sync_compatibility_status()
    
    info = "COMPATIBILIDAD DE SINCRONIZACIÓN:\n\n"
    info += f"📊 Total de anime: {status['total']}\n"
    info += f"✅ Sincronizable con MAL: {status['compatible']}\n"
    info += f"📱 Solo local: {status['local_only']}\n"
    info += f"🔄 Porcentaje sincronizable: {status['sync_percentage']}%\n\n"
    
    info += "ESTADOS SINCRONIZABLES:\n"
    for status_id in MAL_COMPATIBLE_STATUSES:
        info += f"• {status_id}\n"
    
    info += "\nESTADOS SOLO LOCALES:\n"
    for status_id in LOCAL_ONLY_STATUSES:
        info += f"• {status_id} (no se sincroniza)\n"
    
    info += "\nNOTA: Los filtros inteligentes y listas por género\n"
    info += "son funciones locales y no se sincronizan con MAL."
    
    xbmcgui.Dialog().textviewer('Compatibilidad de Sincronización', info)