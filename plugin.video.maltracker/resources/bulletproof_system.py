import functools
import traceback
import time
import os
import json
import sqlite3
import threading
import queue
import xbmc
import xbmcgui
from .config import TOKEN_PATH

class BulletproofSystem:
    
    def __init__(self):
        self.error_queue = queue.Queue()
        self.recovery_thread = None
        self.system_health = 100
        self.critical_errors = 0
        self.auto_recovery_enabled = True
        
    def bulletproof_decorator(self, max_retries=3, fallback_value=None, critical=False):
        """Decorador que hace cualquier función a prueba de errores"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        # Pre-validación
                        if not self.pre_execution_check(func.__name__):
                            return fallback_value
                        
                        # Ejecutar función con timeout
                        result = self.execute_with_timeout(func, args, kwargs, timeout=30)
                        
                        # Post-validación
                        if self.validate_result(result, func.__name__):
                            return result
                        else:
                            raise ValueError(f"Invalid result from {func.__name__}")
                            
                    except Exception as e:
                        last_exception = e
                        
                        # Log del error
                        self.log_error(e, func.__name__, attempt + 1)
                        
                        # Intentar recuperación automática
                        if attempt < max_retries:
                            recovery_success = self.attempt_recovery(e, func.__name__)
                            if recovery_success:
                                continue
                            
                            # Esperar antes del siguiente intento
                            time.sleep(2 ** attempt)  # Backoff exponencial
                        
                        # Actualizar salud del sistema
                        self.update_system_health(critical)
                
                # Todos los intentos fallaron
                self.handle_final_failure(last_exception, func.__name__, critical)
                return fallback_value
                
            return wrapper
        return decorator
    
    def execute_with_timeout(self, func, args, kwargs, timeout=30):
        """Ejecutar función con timeout para evitar cuelgues"""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Función se colgó
            raise TimeoutError(f"Function {func.__name__} timed out after {timeout}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def pre_execution_check(self, func_name):
        """Verificaciones antes de ejecutar función"""
        try:
            # Verificar salud del sistema
            if self.system_health < 20:
                xbmc.log(f'Bulletproof: System health too low for {func_name}', xbmc.LOGWARNING)
                return False
            
            # Verificar recursos disponibles
            if not self.check_system_resources():
                return False
            
            # Verificar integridad de archivos críticos
            if not self.verify_critical_files():
                self.attempt_file_recovery()
            
            return True
            
        except Exception as e:
            xbmc.log(f'Bulletproof: Pre-check failed - {str(e)}', xbmc.LOGERROR)
            return False
    
    def validate_result(self, result, func_name):
        """Validar resultado de función"""
        try:
            # Validaciones específicas por tipo de función
            if 'database' in func_name.lower():
                return self.validate_database_result(result)
            elif 'api' in func_name.lower():
                return self.validate_api_result(result)
            elif 'file' in func_name.lower():
                return self.validate_file_result(result)
            
            # Validación general
            return result is not None
            
        except Exception:
            return False
    
    def attempt_recovery(self, error, func_name):
        """Intentar recuperación automática del error"""
        try:
            error_type = type(error).__name__
            
            recovery_strategies = {
                'sqlite3.DatabaseError': self.recover_database,
                'ConnectionError': self.recover_connection,
                'FileNotFoundError': self.recover_missing_file,
                'PermissionError': self.recover_permissions,
                'JSONDecodeError': self.recover_json_corruption,
                'TimeoutError': self.recover_timeout
            }
            
            recovery_func = recovery_strategies.get(error_type)
            if recovery_func:
                return recovery_func(error, func_name)
            
            # Recuperación genérica
            return self.generic_recovery(error, func_name)
            
        except Exception as e:
            xbmc.log(f'Bulletproof: Recovery failed - {str(e)}', xbmc.LOGERROR)
            return False
    
    def recover_database(self, error, func_name):
        """Recuperar errores de base de datos"""
        try:
            from . import local_database
            
            # Verificar integridad
            conn = sqlite3.connect(local_database.DB_PATH)
            cursor = conn.cursor()
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()[0]
            conn.close()
            
            if result != 'ok':
                # Intentar reparación
                self.repair_database()
                return True
            
            # Recrear conexión
            return True
            
        except Exception:
            # Crear nueva base de datos
            return self.create_emergency_database()
    
    def recover_connection(self, error, func_name):
        """Recuperar errores de conexión"""
        try:
            # Verificar conectividad
            import requests
            
            test_urls = [
                'https://api.jikan.moe/v4/anime/1',
                'https://httpbin.org/status/200'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def recover_missing_file(self, error, func_name):
        """Recuperar archivos faltantes"""
        try:
            missing_file = str(error).split("'")[1] if "'" in str(error) else ""
            
            if missing_file:
                # Crear archivo con valores por defecto
                default_content = self.get_default_file_content(missing_file)
                
                if default_content:
                    with open(missing_file, 'w', encoding='utf-8') as f:
                        if isinstance(default_content, dict):
                            json.dump(default_content, f, indent=2)
                        else:
                            f.write(default_content)
                    
                    return True
            
            return False
            
        except Exception:
            return False
    
    def create_emergency_database(self):
        """Crear base de datos de emergencia"""
        try:
            from . import local_database
            
            # Backup de la BD corrupta
            if os.path.exists(local_database.DB_PATH):
                backup_path = f"{local_database.DB_PATH}.corrupted_{int(time.time())}"
                os.rename(local_database.DB_PATH, backup_path)
            
            # Crear nueva BD
            return local_database.init_database()
            
        except Exception as e:
            xbmc.log(f'Bulletproof: Emergency DB creation failed - {str(e)}', xbmc.LOGERROR)
            return False
    
    def get_default_file_content(self, filename):
        """Obtener contenido por defecto para archivos"""
        defaults = {
            'token.json': {'access_token': '', 'refresh_token': '', 'expires_at': 0},
            'notifications.json': {'new_episodes': True, 'check_interval': 3600},
            'themes.json': {'current_theme': 'default'},
            'permissions.json': {'read_anime': True, 'write_anime': True},
            'social_data.json': {'friends': [], 'reviews': []},
            'external_apis.json': {}
        }
        
        filename_only = os.path.basename(filename)
        return defaults.get(filename_only, {})
    
    def update_system_health(self, critical_error=False):
        """Actualizar salud del sistema"""
        if critical_error:
            self.system_health -= 20
            self.critical_errors += 1
        else:
            self.system_health -= 5
        
        # Recuperación gradual
        if self.system_health < 100:
            self.system_health = min(100, self.system_health + 1)
        
        # Activar modo de emergencia si es necesario
        if self.system_health < 30 or self.critical_errors > 5:
            self.activate_emergency_mode()
    
    def activate_emergency_mode(self):
        """Activar modo de emergencia del sistema"""
        try:
            emergency_file = os.path.join(TOKEN_PATH, 'SYSTEM_EMERGENCY')
            with open(emergency_file, 'w') as f:
                f.write(f"Emergency mode activated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Notificar usuario
            xbmcgui.Dialog().notification(
                '🚨 MODO DE EMERGENCIA',
                'Sistema en modo seguro',
                icon=xbmcgui.NOTIFICATION_WARNING,
                time=8000
            )
            
            # Reiniciar contadores
            self.system_health = 50
            self.critical_errors = 0
            
        except Exception as e:
            xbmc.log(f'Bulletproof: Emergency mode activation failed - {str(e)}', xbmc.LOGERROR)
    
    def check_system_resources(self):
        """Verificar recursos del sistema"""
        try:
            # Verificar espacio en disco
            statvfs = os.statvfs(TOKEN_PATH)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            
            if free_space < 10 * 1024 * 1024:  # 10MB mínimo
                return False
            
            return True
            
        except Exception:
            return True  # Asumir OK si no se puede verificar
    
    def verify_critical_files(self):
        """Verificar integridad de archivos críticos"""
        try:
            critical_files = [
                os.path.join(TOKEN_PATH, 'mal_tracker.db'),
                os.path.join(TOKEN_PATH, 'token.json')
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    # Verificar que el archivo no esté vacío y sea legible
                    if os.path.getsize(file_path) == 0:
                        return False
                    
                    # Verificar permisos de lectura
                    if not os.access(file_path, os.R_OK):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def start_health_monitor(self):
        """Iniciar monitor de salud del sistema"""
        if self.recovery_thread and self.recovery_thread.is_alive():
            return
        
        self.recovery_thread = threading.Thread(target=self.health_monitor_loop)
        self.recovery_thread.daemon = True
        self.recovery_thread.start()
    
    def health_monitor_loop(self):
        """Bucle de monitoreo de salud"""
        while True:
            try:
                # Verificar salud cada 60 segundos
                time.sleep(60)
                
                # Auto-recuperación de salud
                if self.system_health < 100:
                    self.system_health = min(100, self.system_health + 2)
                
                # Verificar archivos críticos
                if not self.verify_critical_files():
                    self.attempt_file_recovery()
                
                # Limpiar errores antiguos
                self.cleanup_old_errors()
                
            except Exception as e:
                xbmc.log(f'Bulletproof: Health monitor error - {str(e)}', xbmc.LOGERROR)
                time.sleep(300)  # Esperar 5 minutos si hay error
    
    def attempt_file_recovery(self):
        """Intentar recuperar archivos críticos"""
        try:
            critical_files = ['mal_tracker.db', 'token.json']
            
            for filename in critical_files:
                file_path = os.path.join(TOKEN_PATH, filename)
                
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    # Buscar backup
                    backup_found = self.restore_from_backup(filename)
                    
                    if not backup_found:
                        # Crear archivo por defecto
                        default_content = self.get_default_file_content(filename)
                        if default_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                if isinstance(default_content, dict):
                                    json.dump(default_content, f, indent=2)
                                else:
                                    f.write(default_content)
            
        except Exception as e:
            xbmc.log(f'Bulletproof: File recovery error - {str(e)}', xbmc.LOGERROR)
    
    def restore_from_backup(self, filename):
        """Restaurar archivo desde backup"""
        try:
            backup_patterns = [
                f"{filename}.backup",
                f"{filename}.bak",
                f"backup_{filename}"
            ]
            
            for pattern in backup_patterns:
                backup_path = os.path.join(TOKEN_PATH, pattern)
                if os.path.exists(backup_path):
                    original_path = os.path.join(TOKEN_PATH, filename)
                    
                    # Copiar backup al archivo original
                    with open(backup_path, 'rb') as src:
                        with open(original_path, 'wb') as dst:
                            dst.write(src.read())
                    
                    return True
            
            return False
            
        except Exception:
            return False
    
    def log_error(self, error, func_name, attempt):
        """Log seguro de errores"""
        try:
            error_info = {
                'timestamp': time.time(),
                'function': func_name,
                'attempt': attempt,
                'error_type': type(error).__name__,
                'error_message': str(error)[:200],  # Limitar longitud
                'system_health': self.system_health
            }
            
            # Agregar a cola de errores
            if not self.error_queue.full():
                self.error_queue.put(error_info)
            
            # Log básico
            xbmc.log(f'Bulletproof: {func_name} failed (attempt {attempt}) - {str(error)[:100]}', xbmc.LOGERROR)
            
        except Exception:
            # Si falla el logging, continuar silenciosamente
            pass
    
    def handle_final_failure(self, error, func_name, critical):
        """Manejar fallo final después de todos los intentos"""
        try:
            if critical:
                # Error crítico - activar modo de emergencia
                self.activate_emergency_mode()
                
                xbmcgui.Dialog().notification(
                    '🚨 ERROR CRÍTICO',
                    f'Función {func_name} falló completamente',
                    icon=xbmcgui.NOTIFICATION_ERROR,
                    time=5000
                )
            else:
                # Error no crítico - notificación suave
                xbmcgui.Dialog().notification(
                    '⚠️ Error',
                    'Operación falló, continuando...',
                    icon=xbmcgui.NOTIFICATION_WARNING,
                    time=3000
                )
            
        except Exception:
            # Si falla la notificación, continuar
            pass
    
    def cleanup_old_errors(self):
        """Limpiar errores antiguos"""
        try:
            current_time = time.time()
            
            # Limpiar cola de errores (mantener solo últimas 2 horas)
            temp_queue = queue.Queue()
            
            while not self.error_queue.empty():
                try:
                    error_info = self.error_queue.get_nowait()
                    if current_time - error_info['timestamp'] < 7200:  # 2 horas
                        temp_queue.put(error_info)
                except queue.Empty:
                    break
            
            self.error_queue = temp_queue
            
        except Exception:
            pass
    
    def get_system_status(self):
        """Obtener estado del sistema"""
        try:
            return {
                'health': self.system_health,
                'critical_errors': self.critical_errors,
                'total_errors': self.error_queue.qsize(),
                'emergency_mode': os.path.exists(os.path.join(TOKEN_PATH, 'SYSTEM_EMERGENCY')),
                'auto_recovery': self.auto_recovery_enabled
            }
        except Exception:
            return {'health': 0, 'critical_errors': 999, 'emergency_mode': True}

# Instancia global del sistema bulletproof
bulletproof = BulletproofSystem()

# Decoradores listos para usar
def safe_execute(max_retries=3, fallback=None):
    """Decorador para ejecución segura"""
    return bulletproof.bulletproof_decorator(max_retries=max_retries, fallback_value=fallback)

def critical_safe(max_retries=5, fallback=None):
    """Decorador para funciones críticas"""
    return bulletproof.bulletproof_decorator(max_retries=max_retries, fallback_value=fallback, critical=True)

def show_bulletproof_status():
    """Mostrar estado del sistema bulletproof"""
    try:
        status = bulletproof.get_system_status()
        
        status_text = "🛡️ ESTADO DEL SISTEMA BULLETPROOF\n\n"
        
        # Salud del sistema
        health_icon = "🟢" if status['health'] >= 80 else "🟡" if status['health'] >= 50 else "🔴"
        status_text += f"{health_icon} Salud del Sistema: {status['health']}/100\n"
        
        # Errores
        status_text += f"🚨 Errores Críticos: {status['critical_errors']}\n"
        status_text += f"⚠️ Total de Errores: {status['total_errors']}\n"
        
        # Estados
        status_text += f"🚨 Modo de Emergencia: {'Activo' if status['emergency_mode'] else 'Inactivo'}\n"
        status_text += f"🔄 Auto-Recuperación: {'Activa' if status['auto_recovery'] else 'Inactiva'}\n\n"
        
        # Recomendaciones
        if status['health'] < 50:
            status_text += "⚠️ RECOMENDACIÓN: Ejecutar mantenimiento del sistema\n"
        elif status['critical_errors'] > 3:
            status_text += "⚠️ RECOMENDACIÓN: Revisar logs de errores\n"
        else:
            status_text += "✅ Sistema funcionando correctamente\n"
        
        xbmcgui.Dialog().textviewer('Estado Bulletproof', status_text)
        
    except Exception as e:
        xbmcgui.Dialog().notification('Bulletproof', f'Error mostrando estado: {str(e)}')