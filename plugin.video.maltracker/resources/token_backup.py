"""
Sistema de backup completo con tokens de autenticación
Permite restaurar addon con sesiones activas
"""

import json
import os
import base64
import zipfile
import time
import xbmcgui
import xbmcvfs
from .config import TOKEN_PATH, TOKEN_FILE, ANILIST_TOKEN_FILE

class TokenBackupManager:
    
    @staticmethod
    def create_complete_backup():
        """Crear backup completo incluyendo tokens"""
        import xbmc
        
        try:
            backup_data = {
                'version': '1.0',
                'timestamp': int(time.time()),
                'tokens': {},
                'settings': {},
                'database': {}
            }
            
            # 1. Backup de tokens MAL
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                    backup_data['tokens']['mal'] = json.load(f)
                xbmc.log('Token Backup: MAL token included', xbmc.LOGINFO)
            
            # 2. Backup de tokens AniList
            if os.path.exists(ANILIST_TOKEN_FILE):
                with open(ANILIST_TOKEN_FILE, 'r', encoding='utf-8') as f:
                    backup_data['tokens']['anilist'] = json.load(f)
                xbmc.log('Token Backup: AniList token included', xbmc.LOGINFO)
            
            # 3. Backup de configuraciones del addon
            try:
                import xbmcaddon
                addon = xbmcaddon.Addon()
                settings = {
                    'client_id': addon.getSetting('client_id'),
                    'client_secret': addon.getSetting('client_secret'),
                    'redirect_uri': addon.getSetting('redirect_uri'),
                    'anilist_client_id': addon.getSetting('anilist_client_id'),
                    'anilist_client_secret': addon.getSetting('anilist_client_secret')
                }
                backup_data['settings'] = settings
                xbmc.log('Token Backup: Settings included', xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f'Token Backup: Settings error - {str(e)}', xbmc.LOGWARNING)
            
            # 4. Backup de base de datos local
            try:
                from . import local_database
                db_data = local_database.export_all_data()
                backup_data['database'] = db_data
                xbmc.log('Token Backup: Database included', xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f'Token Backup: Database error - {str(e)}', xbmc.LOGWARNING)
            
            # 5. Codificar backup (opcional - para seguridad)
            backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
            backup_encoded = base64.b64encode(backup_json.encode('utf-8')).decode('utf-8')
            
            # 6. Guardar backup
            backup_file = os.path.join(TOKEN_PATH, f'mal_complete_backup_{int(time.time())}.malb')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_encoded)
            
            xbmc.log(f'Token Backup: Complete backup created - {backup_file}', xbmc.LOGINFO)
            return backup_file
            
        except Exception as e:
            xbmc.log(f'Token Backup: Creation error - {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def restore_complete_backup(backup_file):
        """Restaurar backup completo incluyendo tokens"""
        import xbmc
        import time
        
        try:
            # 1. Leer backup
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_encoded = f.read()
            
            # 2. Decodificar
            backup_json = base64.b64decode(backup_encoded.encode('utf-8')).decode('utf-8')
            backup_data = json.loads(backup_json)
            
            xbmc.log('Token Backup: Backup file loaded successfully', xbmc.LOGINFO)
            
            # 3. Restaurar tokens MAL
            if 'mal' in backup_data.get('tokens', {}):
                with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
                    json.dump(backup_data['tokens']['mal'], f, ensure_ascii=False, indent=2)
                xbmc.log('Token Backup: MAL token restored', xbmc.LOGINFO)
            
            # 4. Restaurar tokens AniList
            if 'anilist' in backup_data.get('tokens', {}):
                with open(ANILIST_TOKEN_FILE, 'w', encoding='utf-8') as f:
                    json.dump(backup_data['tokens']['anilist'], f, ensure_ascii=False, indent=2)
                xbmc.log('Token Backup: AniList token restored', xbmc.LOGINFO)
            
            # 5. Restaurar configuraciones
            if backup_data.get('settings'):
                try:
                    import xbmcaddon
                    addon = xbmcaddon.Addon()
                    settings = backup_data['settings']
                    
                    for key, value in settings.items():
                        if value:  # Solo restaurar si no está vacío
                            addon.setSetting(key, value)
                    
                    xbmc.log('Token Backup: Settings restored', xbmc.LOGINFO)
                except Exception as e:
                    xbmc.log(f'Token Backup: Settings restore error - {str(e)}', xbmc.LOGWARNING)
            
            # 6. Restaurar base de datos
            if backup_data.get('database'):
                try:
                    from . import local_database
                    local_database.import_all_data(backup_data['database'])
                    xbmc.log('Token Backup: Database restored', xbmc.LOGINFO)
                except Exception as e:
                    xbmc.log(f'Token Backup: Database restore error - {str(e)}', xbmc.LOGWARNING)
            
            return True
            
        except Exception as e:
            xbmc.log(f'Token Backup: Restore error - {str(e)}', xbmc.LOGERROR)
            return False
    
    @staticmethod
    def show_backup_menu():
        """Mostrar menú de backup completo"""
        options = [
            '💾 Crear backup completo (con tokens)',
            '📥 Restaurar backup completo',
            '📋 Ver backups disponibles',
            '🗑️ Limpiar backups antiguos'
        ]
        
        selected = xbmcgui.Dialog().select('Backup Completo:', options)
        
        if selected == 0:  # Crear backup
            TokenBackupManager.create_backup_with_progress()
        elif selected == 1:  # Restaurar backup
            TokenBackupManager.restore_backup_with_selection()
        elif selected == 2:  # Ver backups
            TokenBackupManager.show_available_backups()
        elif selected == 3:  # Limpiar
            TokenBackupManager.clean_old_backups()
    
    @staticmethod
    def create_backup_with_progress():
        """Crear backup con barra de progreso"""
        progress = xbmcgui.DialogProgress()
        progress.create('Backup Completo', 'Creando backup con tokens...')
        
        progress.update(25, 'Recopilando tokens...')
        backup_file = TokenBackupManager.create_complete_backup()
        
        progress.update(100, 'Backup completado')
        progress.close()
        
        if backup_file:
            xbmcgui.Dialog().ok('Backup Exitoso', 
                f'Backup creado exitosamente:\n{os.path.basename(backup_file)}\n\n'
                'Incluye tokens, configuraciones y base de datos.\n'
                'Guarda este archivo en lugar seguro.')
        else:
            xbmcgui.Dialog().ok('Error', 'No se pudo crear el backup')
    
    @staticmethod
    def restore_backup_with_selection():
        """Restaurar backup con selección de archivo"""
        # Buscar archivos de backup
        backup_files = []
        if os.path.exists(TOKEN_PATH):
            for file in os.listdir(TOKEN_PATH):
                if file.endswith('.malb'):
                    backup_files.append(file)
        
        if not backup_files:
            xbmcgui.Dialog().ok('Sin Backups', 'No se encontraron archivos de backup')
            return
        
        # Seleccionar backup
        selected = xbmcgui.Dialog().select('Seleccionar backup:', backup_files)
        if selected == -1:
            return
        
        backup_file = os.path.join(TOKEN_PATH, backup_files[selected])
        
        # Confirmar restauración
        if not xbmcgui.Dialog().yesno('Confirmar Restauración', 
            'Esto sobrescribirá:\n'
            '• Tokens de autenticación\n'
            '• Configuraciones del addon\n'
            '• Base de datos local\n\n'
            '¿Continuar?'):
            return
        
        # Restaurar con progreso
        progress = xbmcgui.DialogProgress()
        progress.create('Restaurando Backup', 'Restaurando configuración completa...')
        
        progress.update(50, 'Restaurando tokens y configuraciones...')
        success = TokenBackupManager.restore_complete_backup(backup_file)
        
        progress.update(100, 'Restauración completada')
        progress.close()
        
        if success:
            xbmcgui.Dialog().ok('Restauración Exitosa', 
                'Backup restaurado exitosamente.\n\n'
                'Tokens, configuraciones y datos restaurados.\n'
                'El addon está listo para usar.')
        else:
            xbmcgui.Dialog().ok('Error', 'Error durante la restauración')
    
    @staticmethod
    def show_available_backups():
        """Mostrar información de backups disponibles"""
        backup_files = []
        if os.path.exists(TOKEN_PATH):
            for file in os.listdir(TOKEN_PATH):
                if file.endswith('.malb'):
                    file_path = os.path.join(TOKEN_PATH, file)
                    size = os.path.getsize(file_path)
                    backup_files.append(f'{file} ({size} bytes)')
        
        if backup_files:
            info = 'BACKUPS DISPONIBLES:\n\n' + '\n'.join(backup_files)
        else:
            info = 'No hay backups disponibles'
        
        xbmcgui.Dialog().textviewer('Backups Disponibles', info)
    
    @staticmethod
    def clean_old_backups():
        """Limpiar backups antiguos (mantener últimos 5)"""
        import time
        
        backup_files = []
        if os.path.exists(TOKEN_PATH):
            for file in os.listdir(TOKEN_PATH):
                if file.endswith('.malb'):
                    file_path = os.path.join(TOKEN_PATH, file)
                    mtime = os.path.getmtime(file_path)
                    backup_files.append((file_path, mtime))
        
        # Ordenar por fecha (más recientes primero)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Eliminar backups antiguos (mantener 5)
        deleted = 0
        for file_path, _ in backup_files[5:]:
            try:
                os.remove(file_path)
                deleted += 1
            except:
                pass
        
        if deleted > 0:
            xbmcgui.Dialog().notification('Limpieza', f'{deleted} backups antiguos eliminados')
        else:
            xbmcgui.Dialog().notification('Limpieza', 'No hay backups antiguos para eliminar')