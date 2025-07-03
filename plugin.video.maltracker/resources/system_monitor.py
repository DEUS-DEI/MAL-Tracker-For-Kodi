import threading
import time
import psutil
import os
import json
import xbmc
import xbmcgui
from .config import TOKEN_PATH
from .bulletproof_system import bulletproof

class SystemMonitor:
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.performance_data = []
        self.alerts = []
        
    def start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        if self.monitoring:
            return False, "Monitoreo ya activo"
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Iniciar sistema bulletproof
        bulletproof.start_health_monitor()
        
        return True, "Monitoreo iniciado"
    
    def monitor_loop(self):
        """Bucle principal de monitoreo"""
        while self.monitoring:
            try:
                # Recopilar métricas del sistema
                metrics = self.collect_system_metrics()
                
                # Analizar métricas
                self.analyze_metrics(metrics)
                
                # Guardar datos de rendimiento
                self.save_performance_data(metrics)
                
                # Esperar antes del siguiente ciclo
                time.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                xbmc.log(f'System Monitor: Loop error - {str(e)}', xbmc.LOGERROR)
                time.sleep(60)  # Esperar más en caso de error
    
    def collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        try:
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                'kodi_memory': self.get_kodi_memory_usage(),
                'addon_files_count': self.count_addon_files(),
                'database_size': self.get_database_size(),
                'bulletproof_health': bulletproof.system_health,
                'active_threads': threading.active_count()
            }
            
            return metrics
            
        except Exception as e:
            xbmc.log(f'System Monitor: Metrics collection error - {str(e)}', xbmc.LOGERROR)
            return {'timestamp': time.time(), 'error': str(e)}
    
    def get_kodi_memory_usage(self):
        """Obtener uso de memoria de Kodi"""
        try:
            # Buscar proceso de Kodi
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                if 'kodi' in proc.info['name'].lower():
                    return proc.info['memory_percent']
            return 0
        except:
            return 0
    
    def count_addon_files(self):
        """Contar archivos del addon"""
        try:
            count = 0
            for root, dirs, files in os.walk(TOKEN_PATH):
                count += len(files)
            return count
        except:
            return 0
    
    def get_database_size(self):
        """Obtener tamaño de la base de datos"""
        try:
            from . import local_database
            if os.path.exists(local_database.DB_PATH):
                return os.path.getsize(local_database.DB_PATH)
            return 0
        except:
            return 0
    
    def analyze_metrics(self, metrics):
        """Analizar métricas y generar alertas"""
        try:
            alerts = []
            
            # Verificar uso de CPU
            if metrics.get('cpu_percent', 0) > 80:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'message': f"Alto uso de CPU: {metrics['cpu_percent']:.1f}%",
                    'timestamp': metrics['timestamp']
                })
            
            # Verificar uso de memoria
            if metrics.get('memory_percent', 0) > 85:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning',
                    'message': f"Alto uso de memoria: {metrics['memory_percent']:.1f}%",
                    'timestamp': metrics['timestamp']
                })
            
            # Verificar espacio en disco
            if metrics.get('disk_usage', 0) > 90:
                alerts.append({
                    'type': 'low_disk_space',
                    'severity': 'critical',
                    'message': f"Poco espacio en disco: {metrics['disk_usage']:.1f}%",
                    'timestamp': metrics['timestamp']
                })
            
            # Verificar salud del sistema bulletproof
            if metrics.get('bulletproof_health', 100) < 50:
                alerts.append({
                    'type': 'system_health',
                    'severity': 'critical',
                    'message': f"Salud del sistema baja: {metrics['bulletproof_health']}/100",
                    'timestamp': metrics['timestamp']
                })
            
            # Verificar número de hilos
            if metrics.get('active_threads', 0) > 20:
                alerts.append({
                    'type': 'thread_leak',
                    'severity': 'warning',
                    'message': f"Muchos hilos activos: {metrics['active_threads']}",
                    'timestamp': metrics['timestamp']
                })
            
            # Procesar alertas
            if alerts:
                self.process_alerts(alerts)
                
        except Exception as e:
            xbmc.log(f'System Monitor: Metrics analysis error - {str(e)}', xbmc.LOGERROR)
    
    def process_alerts(self, alerts):
        """Procesar alertas del sistema"""
        try:
            critical_alerts = [a for a in alerts if a['severity'] == 'critical']
            
            # Respuesta automática a alertas críticas
            for alert in critical_alerts:
                self.handle_critical_alert(alert)
            
            # Guardar alertas
            self.alerts.extend(alerts)
            
            # Mantener solo últimas 100 alertas
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            # Notificar alertas importantes
            if critical_alerts:
                self.notify_critical_alerts(critical_alerts)
                
        except Exception as e:
            xbmc.log(f'System Monitor: Alert processing error - {str(e)}', xbmc.LOGERROR)
    
    def handle_critical_alert(self, alert):
        """Manejar alerta crítica"""
        try:
            if alert['type'] == 'low_disk_space':
                self.cleanup_temporary_files()
            elif alert['type'] == 'system_health':
                bulletproof.activate_emergency_mode()
            elif alert['type'] == 'high_memory':
                self.force_garbage_collection()
                
        except Exception as e:
            xbmc.log(f'System Monitor: Critical alert handling error - {str(e)}', xbmc.LOGERROR)
    
    def cleanup_temporary_files(self):
        """Limpiar archivos temporales"""
        try:
            temp_patterns = [
                '*.tmp',
                '*.log.old',
                '*_backup_*',
                '*.cache'
            ]
            
            cleaned_count = 0
            for pattern in temp_patterns:
                for root, dirs, files in os.walk(TOKEN_PATH):
                    for file in files:
                        if file.endswith(pattern.replace('*', '')):
                            try:
                                os.remove(os.path.join(root, file))
                                cleaned_count += 1
                            except:
                                continue
            
            xbmc.log(f'System Monitor: Cleaned {cleaned_count} temporary files', xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f'System Monitor: Cleanup error - {str(e)}', xbmc.LOGERROR)
    
    def force_garbage_collection(self):
        """Forzar recolección de basura"""
        try:
            import gc
            collected = gc.collect()
            xbmc.log(f'System Monitor: Garbage collection freed {collected} objects', xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f'System Monitor: GC error - {str(e)}', xbmc.LOGERROR)
    
    def notify_critical_alerts(self, alerts):
        """Notificar alertas críticas"""
        try:
            message = f"{len(alerts)} alertas críticas detectadas"
            xbmcgui.Dialog().notification(
                '🚨 ALERTA CRÍTICA',
                message,
                icon=xbmcgui.NOTIFICATION_ERROR,
                time=8000
            )
        except Exception as e:
            xbmc.log(f'System Monitor: Notification error - {str(e)}', xbmc.LOGERROR)
    
    def save_performance_data(self, metrics):
        """Guardar datos de rendimiento"""
        try:
            self.performance_data.append(metrics)
            
            # Mantener solo últimas 24 horas de datos (2880 puntos a 30s cada uno)
            if len(self.performance_data) > 2880:
                self.performance_data = self.performance_data[-2880:]
            
            # Guardar cada 10 minutos
            if len(self.performance_data) % 20 == 0:  # 20 * 30s = 10 min
                self.persist_performance_data()
                
        except Exception as e:
            xbmc.log(f'System Monitor: Save performance data error - {str(e)}', xbmc.LOGERROR)
    
    def persist_performance_data(self):
        """Persistir datos de rendimiento"""
        try:
            perf_file = os.path.join(TOKEN_PATH, 'performance_data.json')
            
            # Guardar solo últimos 100 puntos para no llenar el disco
            recent_data = self.performance_data[-100:]
            
            with open(perf_file, 'w') as f:
                json.dump(recent_data, f, indent=2)
                
        except Exception as e:
            xbmc.log(f'System Monitor: Persist data error - {str(e)}', xbmc.LOGERROR)
    
    def get_system_report(self):
        """Generar reporte del sistema"""
        try:
            if not self.performance_data:
                return "No hay datos de rendimiento disponibles"
            
            latest = self.performance_data[-1]
            
            report = "📊 REPORTE DEL SISTEMA\n\n"
            
            # Métricas actuales
            report += "📈 MÉTRICAS ACTUALES:\n"
            report += f"• CPU: {latest.get('cpu_percent', 0):.1f}%\n"
            report += f"• Memoria: {latest.get('memory_percent', 0):.1f}%\n"
            report += f"• Disco: {latest.get('disk_usage', 0):.1f}%\n"
            report += f"• Salud Bulletproof: {latest.get('bulletproof_health', 0)}/100\n"
            report += f"• Hilos Activos: {latest.get('active_threads', 0)}\n\n"
            
            # Estadísticas de alertas
            critical_alerts = len([a for a in self.alerts if a['severity'] == 'critical'])
            warning_alerts = len([a for a in self.alerts if a['severity'] == 'warning'])
            
            report += "🚨 ALERTAS:\n"
            report += f"• Críticas: {critical_alerts}\n"
            report += f"• Advertencias: {warning_alerts}\n\n"
            
            # Recomendaciones
            report += "💡 RECOMENDACIONES:\n"
            
            if latest.get('cpu_percent', 0) > 70:
                report += "• Reducir carga de CPU\n"
            if latest.get('memory_percent', 0) > 80:
                report += "• Liberar memoria\n"
            if latest.get('disk_usage', 0) > 85:
                report += "• Limpiar archivos temporales\n"
            if latest.get('bulletproof_health', 100) < 70:
                report += "• Ejecutar mantenimiento del sistema\n"
            
            if not any([
                latest.get('cpu_percent', 0) > 70,
                latest.get('memory_percent', 0) > 80,
                latest.get('disk_usage', 0) > 85,
                latest.get('bulletproof_health', 100) < 70
            ]):
                report += "• Sistema funcionando correctamente ✅\n"
            
            return report
            
        except Exception as e:
            return f"Error generando reporte: {str(e)}"
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        return True, "Monitoreo detenido"

# Instancia global del monitor
system_monitor = SystemMonitor()

def show_system_monitor_menu():
    """Mostrar menú del monitor del sistema"""
    options = [
        '🚀 Iniciar monitoreo',
        '⏹️ Detener monitoreo',
        '📊 Ver reporte del sistema',
        '🛡️ Estado Bulletproof',
        '🚨 Ver alertas',
        '🧹 Limpiar datos de rendimiento'
    ]
    
    selected = xbmcgui.Dialog().select('Monitor del Sistema:', options)
    
    if selected == 0:
        success, message = system_monitor.start_monitoring()
        xbmcgui.Dialog().notification('Monitor', message)
    elif selected == 1:
        success, message = system_monitor.stop_monitoring()
        xbmcgui.Dialog().notification('Monitor', message)
    elif selected == 2:
        report = system_monitor.get_system_report()
        xbmcgui.Dialog().textviewer('Reporte del Sistema', report)
    elif selected == 3:
        from .bulletproof_system import show_bulletproof_status
        show_bulletproof_status()
    elif selected == 4:
        show_system_alerts()
    elif selected == 5:
        system_monitor.performance_data = []
        system_monitor.alerts = []
        xbmcgui.Dialog().notification('Monitor', 'Datos limpiados')

def show_system_alerts():
    """Mostrar alertas del sistema"""
    try:
        if not system_monitor.alerts:
            xbmcgui.Dialog().notification('Monitor', 'No hay alertas')
            return
        
        alerts_text = "🚨 ALERTAS DEL SISTEMA\n\n"
        
        # Mostrar últimas 10 alertas
        recent_alerts = system_monitor.alerts[-10:]
        
        for alert in reversed(recent_alerts):
            timestamp = time.strftime('%H:%M:%S', time.localtime(alert['timestamp']))
            severity_icon = {'critical': '🚨', 'warning': '⚠️', 'info': 'ℹ️'}.get(alert['severity'], '❓')
            
            alerts_text += f"{severity_icon} {timestamp} - {alert['message']}\n"
        
        xbmcgui.Dialog().textviewer('Alertas del Sistema', alerts_text)
        
    except Exception as e:
        xbmcgui.Dialog().notification('Monitor', f'Error: {str(e)}')