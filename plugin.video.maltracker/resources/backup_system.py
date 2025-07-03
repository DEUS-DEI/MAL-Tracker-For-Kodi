import json
import os
import time
import zipfile
import xbmc
import xbmcgui
import xbmcvfs
from . import local_database
from .config import TOKEN_PATH

BACKUP_DIR = os.path.join(TOKEN_PATH, 'backups')
EXPORT_DIR = os.path.join(TOKEN_PATH, 'exports')

def init_backup_system():
    """Inicializar sistema de backup"""
    try:
        # Crear directorios si no existen
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
        
        return True
        
    except Exception as e:
        xbmc.log(f'Backup System: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def create_full_backup():
    """Crear backup completo"""
    try:
        timestamp = int(time.time())
        backup_name = f"mal_tracker_backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        progress = xbmcgui.DialogProgress()
        progress.create('Creando Backup', 'Preparando backup completo...')
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Backup de base de datos
            progress.update(20, 'Respaldando base de datos...')
            if os.path.exists(local_database.DB_PATH):
                backup_zip.write(local_database.DB_PATH, 'database/mal_tracker.db')
            
            # Backup de configuraciones
            progress.update(40, 'Respaldando configuraciones...')
            config_files = [
                'token.json',
                'notifications.json', 
                'themes.json',
                'layout.json',
                'achievements.json',
                'gamification_stats.json'
            ]
            
            for config_file in config_files:
                file_path = os.path.join(TOKEN_PATH, config_file)
                if os.path.exists(file_path):
                    backup_zip.write(file_path, f'config/{config_file}')
            
            # Crear manifiesto del backup
            progress.update(60, 'Creando manifiesto...')
            manifest = create_backup_manifest()
            backup_zip.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Backup de logs recientes
            progress.update(80, 'Respaldando logs...')
            activity_log = local_database.get_activity_log(100)
            if activity_log:
                log_data = {
                    'activity_log': activity_log,
                    'created_at': timestamp
                }
                backup_zip.writestr('logs/activity.json', json.dumps(log_data, indent=2))
        
        progress.update(100, 'Backup completado')
        progress.close()
        
        xbmcgui.Dialog().notification('MAL Tracker', f'Backup creado: {backup_name}')
        return backup_path
        
    except Exception as e:
        if 'progress' in locals():
            progress.close()
        xbmc.log(f'Backup System: Create backup error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error en backup: {str(e)}')
        return None

def create_backup_manifest():
    """Crear manifiesto del backup"""
    try:
        stats = local_database.get_local_stats()
        
        manifest = {
            'version': '1.0.0',
            'created_at': int(time.time()),
            'addon_version': '1.0.0',
            'total_anime': stats.get('total_anime', 0),
            'completed_anime': stats.get('completed', 0),
            'watching_anime': stats.get('watching', 0),
            'avg_score': stats.get('avg_score', 0),
            'total_episodes': stats.get('total_episodes', 0),
            'backup_type': 'full'
        }
        
        return manifest
        
    except Exception as e:
        xbmc.log(f'Backup System: Create manifest error - {str(e)}', xbmc.LOGERROR)
        return {}

def restore_from_backup(backup_path):
    """Restaurar desde backup"""
    try:
        if not os.path.exists(backup_path):
            xbmcgui.Dialog().notification('MAL Tracker', 'Archivo de backup no encontrado')
            return False
        
        # Confirmar restauración
        if not xbmcgui.Dialog().yesno('Confirmar Restauración', 
                                     '¿Restaurar desde backup?\n\nEsto sobrescribirá todos los datos actuales.'):
            return False
        
        progress = xbmcgui.DialogProgress()
        progress.create('Restaurando Backup', 'Extrayendo archivos...')
        
        with zipfile.ZipFile(backup_path, 'r') as backup_zip:
            # Verificar manifiesto
            try:
                manifest_data = backup_zip.read('manifest.json')
                manifest = json.loads(manifest_data)
                xbmc.log(f'Backup System: Restoring backup from {manifest.get("created_at")}', xbmc.LOGINFO)
            except:
                xbmc.log('Backup System: No manifest found, proceeding anyway', xbmc.LOGWARNING)
            
            # Restaurar base de datos
            progress.update(25, 'Restaurando base de datos...')
            try:
                db_data = backup_zip.read('database/mal_tracker.db')
                with open(local_database.DB_PATH, 'wb') as db_file:
                    db_file.write(db_data)
            except:
                xbmc.log('Backup System: Database not found in backup', xbmc.LOGWARNING)
            
            # Restaurar configuraciones
            progress.update(50, 'Restaurando configuraciones...')
            config_files = [
                'token.json',
                'notifications.json',
                'themes.json', 
                'layout.json',
                'achievements.json',
                'gamification_stats.json'
            ]
            
            for config_file in config_files:
                try:
                    config_data = backup_zip.read(f'config/{config_file}')
                    config_path = os.path.join(TOKEN_PATH, config_file)
                    with open(config_path, 'wb') as f:
                        f.write(config_data)
                except:
                    continue  # Archivo no existe en backup
            
            progress.update(75, 'Verificando integridad...')
            # Verificar que la base de datos se restauró correctamente
            try:
                test_stats = local_database.get_local_stats()
                xbmc.log(f'Backup System: Restored {test_stats.get("total_anime", 0)} anime', xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f'Backup System: Database verification failed - {str(e)}', xbmc.LOGERROR)
        
        progress.update(100, 'Restauración completada')
        progress.close()
        
        xbmcgui.Dialog().notification('MAL Tracker', 'Backup restaurado exitosamente')
        return True
        
    except Exception as e:
        if 'progress' in locals():
            progress.close()
        xbmc.log(f'Backup System: Restore error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error en restauración: {str(e)}')
        return False

def export_to_csv():
    """Exportar lista a CSV"""
    try:
        anime_list = local_database.get_local_anime_list()
        
        if not anime_list:
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay anime para exportar')
            return None
        
        timestamp = int(time.time())
        csv_filename = f"mal_tracker_export_{timestamp}.csv"
        csv_path = os.path.join(EXPORT_DIR, csv_filename)
        
        # Crear CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
            # Header
            csv_file.write('Title,Status,Episodes Watched,Total Episodes,Score,Genres,Studios,Year,Added Date\n')
            
            # Data
            for anime in anime_list:
                title = anime.get('title', '').replace(',', ';')
                status = anime.get('status', '')
                episodes_watched = anime.get('episodes_watched', 0)
                total_episodes = anime.get('total_episodes', 0)
                score = anime.get('score', 0)
                genres = ';'.join(anime.get('genres', []))
                studios = ';'.join(anime.get('studios', []))
                year = anime.get('year', '')
                
                csv_file.write(f'"{title}",{status},{episodes_watched},{total_episodes},{score},"{genres}","{studios}",{year},\n')
        
        xbmcgui.Dialog().notification('MAL Tracker', f'Exportado: {csv_filename}')
        return csv_path
        
    except Exception as e:
        xbmc.log(f'Backup System: CSV export error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error en exportación: {str(e)}')
        return None

def export_to_json():
    """Exportar lista a JSON"""
    try:
        anime_list = local_database.get_local_anime_list()
        stats = local_database.get_local_stats()
        
        if not anime_list:
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay anime para exportar')
            return None
        
        timestamp = int(time.time())
        json_filename = f"mal_tracker_export_{timestamp}.json"
        json_path = os.path.join(EXPORT_DIR, json_filename)
        
        export_data = {
            'export_info': {
                'created_at': timestamp,
                'version': '1.0.0',
                'total_anime': len(anime_list)
            },
            'statistics': stats,
            'anime_list': anime_list
        }
        
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(export_data, json_file, indent=2, ensure_ascii=False)
        
        xbmcgui.Dialog().notification('MAL Tracker', f'Exportado: {json_filename}')
        return json_path
        
    except Exception as e:
        xbmc.log(f'Backup System: JSON export error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Tracker', f'Error en exportación: {str(e)}')
        return None

def show_backup_menu():
    """Mostrar menú de backup"""
    options = [
        '💾 Crear backup completo',
        '📂 Restaurar desde backup',
        '📊 Exportar a CSV',
        '📄 Exportar a JSON',
        '🗂️ Ver backups existentes',
        '🗑️ Limpiar backups antiguos'
    ]
    
    selected = xbmcgui.Dialog().select('Sistema de Backup:', options)
    
    if selected == 0:
        create_full_backup()
    elif selected == 1:
        show_restore_menu()
    elif selected == 2:
        export_to_csv()
    elif selected == 3:
        export_to_json()
    elif selected == 4:
        show_existing_backups()
    elif selected == 5:
        clean_old_backups()

def show_restore_menu():
    """Mostrar menú de restauración"""
    try:
        backup_files = []
        if os.path.exists(BACKUP_DIR):
            for file in os.listdir(BACKUP_DIR):
                if file.endswith('.zip'):
                    backup_files.append(file)
        
        if not backup_files:
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay backups disponibles')
            return
        
        # Ordenar por fecha (más reciente primero)
        backup_files.sort(reverse=True)
        
        selected = xbmcgui.Dialog().select('Seleccionar Backup:', backup_files)
        
        if selected != -1:
            backup_path = os.path.join(BACKUP_DIR, backup_files[selected])
            restore_from_backup(backup_path)
        
    except Exception as e:
        xbmc.log(f'Backup System: Show restore menu error - {str(e)}', xbmc.LOGERROR)

def show_existing_backups():
    """Mostrar backups existentes"""
    try:
        if not os.path.exists(BACKUP_DIR):
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay backups')
            return
        
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
        
        if not backup_files:
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay backups disponibles')
            return
        
        info = "BACKUPS DISPONIBLES:\n\n"
        
        for backup_file in sorted(backup_files, reverse=True):
            backup_path = os.path.join(BACKUP_DIR, backup_file)
            file_size = os.path.getsize(backup_path)
            size_mb = round(file_size / (1024 * 1024), 2)
            
            # Extraer timestamp del nombre
            try:
                timestamp_str = backup_file.split('_')[-1].replace('.zip', '')
                timestamp = int(timestamp_str)
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))
            except:
                date_str = 'Fecha desconocida'
            
            info += f"📁 {backup_file}\n"
            info += f"   Fecha: {date_str}\n"
            info += f"   Tamaño: {size_mb} MB\n\n"
        
        xbmcgui.Dialog().textviewer('Backups Existentes', info)
        
    except Exception as e:
        xbmc.log(f'Backup System: Show existing backups error - {str(e)}', xbmc.LOGERROR)

def clean_old_backups():
    """Limpiar backups antiguos"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return
        
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
        
        if len(backup_files) <= 5:  # Mantener al menos 5 backups
            xbmcgui.Dialog().notification('MAL Tracker', 'No hay backups antiguos para limpiar')
            return
        
        # Ordenar por fecha y mantener solo los 5 más recientes
        backup_files.sort(reverse=True)
        old_backups = backup_files[5:]  # Backups a eliminar
        
        if xbmcgui.Dialog().yesno('Confirmar', f'¿Eliminar {len(old_backups)} backups antiguos?'):
            deleted_count = 0
            for backup_file in old_backups:
                try:
                    os.remove(os.path.join(BACKUP_DIR, backup_file))
                    deleted_count += 1
                except:
                    continue
            
            xbmcgui.Dialog().notification('MAL Tracker', f'{deleted_count} backups eliminados')
        
    except Exception as e:
        xbmc.log(f'Backup System: Clean old backups error - {str(e)}', xbmc.LOGERROR)