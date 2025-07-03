import traceback
import time
import os
import xbmc
import xbmcgui
from .config import TOKEN_PATH

class ErrorHandler:
    
    @staticmethod
    def handle_exception(func):
        """Decorador para manejo seguro de excepciones"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, func.__name__)
                ErrorHandler.show_user_friendly_error(str(e))
                return None
        return wrapper
    
    @staticmethod
    def log_error(error, function_name=None):
        """Registrar error de forma segura"""
        try:
            error_msg = f"Error in {function_name}: {str(error)}"
            xbmc.log(error_msg, xbmc.LOGERROR)
            
            # Guardar en archivo de log local
            ErrorHandler.save_error_log(error, function_name)
            
        except Exception as log_error:
            # Si falla el logging, al menos intentar log básico
            xbmc.log(f"Logging failed: {str(log_error)}", xbmc.LOGERROR)
    
    @staticmethod
    def save_error_log(error, function_name):
        """Guardar log de errores localmente"""
        try:
            log_file = os.path.join(TOKEN_PATH, 'error_log.txt')
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            error_entry = f"[{timestamp}] {function_name}: {str(error)}\n"
            
            # Limitar tamaño del archivo de log
            if os.path.exists(log_file):
                file_size = os.path.getsize(log_file)
                if file_size > 1024 * 1024:  # 1MB
                    # Rotar log
                    backup_file = os.path.join(TOKEN_PATH, 'error_log_old.txt')
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(log_file, backup_file)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(error_entry)
                
        except Exception:
            # Si falla guardar el log, continuar silenciosamente
            pass
    
    @staticmethod
    def show_user_friendly_error(error_msg):
        """Mostrar error amigable al usuario"""
        try:
            # Mapear errores técnicos a mensajes amigables
            friendly_messages = {
                'ConnectionError': 'Error de conexión. Verifica tu internet.',
                'TimeoutError': 'La operación tardó demasiado. Inténtalo de nuevo.',
                'JSONDecodeError': 'Error procesando datos. Inténtalo más tarde.',
                'FileNotFoundError': 'Archivo no encontrado. Reinstala el addon.',
                'PermissionError': 'Sin permisos. Verifica configuración de Kodi.',
                'sqlite3.Error': 'Error de base de datos. Ejecuta mantenimiento.'
            }
            
            friendly_msg = "Error inesperado. Consulta el log para detalles."
            
            for error_type, message in friendly_messages.items():
                if error_type in error_msg:
                    friendly_msg = message
                    break
            
            xbmcgui.Dialog().notification(
                'MAL Tracker - Error',
                friendly_msg,
                icon=xbmcgui.NOTIFICATION_ERROR,
                time=5000
            )
            
        except Exception:
            # Si falla mostrar el error, continuar silenciosamente
            pass
    
    @staticmethod
    def get_error_statistics():
        """Obtener estadísticas de errores"""
        try:
            log_file = os.path.join(TOKEN_PATH, 'error_log.txt')
            
            if not os.path.exists(log_file):
                return {'total_errors': 0, 'recent_errors': 0}
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_errors = len(lines)
            
            # Contar errores recientes (últimas 24 horas)
            current_time = time.time()
            recent_errors = 0
            
            for line in reversed(lines[-50:]):  # Revisar últimas 50 líneas
                try:
                    # Extraer timestamp del log
                    timestamp_str = line.split(']')[0][1:]
                    log_time = time.mktime(time.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'))
                    
                    if current_time - log_time <= 86400:  # 24 horas
                        recent_errors += 1
                    else:
                        break
                        
                except Exception:
                    continue
            
            return {
                'total_errors': total_errors,
                'recent_errors': recent_errors,
                'log_size': os.path.getsize(log_file) if os.path.exists(log_file) else 0
            }
            
        except Exception:
            return {'total_errors': 0, 'recent_errors': 0, 'log_size': 0}
    
    @staticmethod
    def show_error_report():
        """Mostrar reporte de errores"""
        try:
            stats = ErrorHandler.get_error_statistics()
            
            report = "🐛 REPORTE DE ERRORES\n\n"
            report += f"📊 Total de errores: {stats['total_errors']}\n"
            report += f"🕐 Errores recientes (24h): {stats['recent_errors']}\n"
            report += f"📁 Tamaño del log: {stats['log_size']} bytes\n\n"
            
            if stats['recent_errors'] > 10:
                report += "⚠️ ADVERTENCIA: Muchos errores recientes\n"
                report += "Considera ejecutar mantenimiento del sistema.\n\n"
            
            # Mostrar últimos errores
            log_file = os.path.join(TOKEN_PATH, 'error_log.txt')
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if lines:
                    report += "🔍 ÚLTIMOS ERRORES:\n"
                    for line in lines[-5:]:  # Últimos 5 errores
                        report += f"• {line.strip()}\n"
            
            xbmcgui.Dialog().textviewer('Reporte de Errores', report)
            
        except Exception as e:
            xbmcgui.Dialog().notification('Error Handler', f'Error mostrando reporte: {str(e)}')
    
    @staticmethod
    def clear_error_log():
        """Limpiar log de errores"""
        try:
            log_file = os.path.join(TOKEN_PATH, 'error_log.txt')
            
            if os.path.exists(log_file):
                os.remove(log_file)
                xbmcgui.Dialog().notification('Error Handler', 'Log de errores limpiado')
            else:
                xbmcgui.Dialog().notification('Error Handler', 'No hay log de errores')
                
        except Exception as e:
            xbmcgui.Dialog().notification('Error Handler', f'Error limpiando log: {str(e)}')

# Decorador para funciones críticas
def safe_execute(func):
    """Decorador para ejecución segura"""
    return ErrorHandler.handle_exception(func)