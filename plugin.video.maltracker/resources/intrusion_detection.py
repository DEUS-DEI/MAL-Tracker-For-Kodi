import os
import time
import hashlib
import json
import threading
import xbmc
import xbmcgui
from .config import TOKEN_PATH

class IntrusionDetectionSystem:
    
    def __init__(self):
        self.monitoring = False
        self.baseline_hashes = {}
        self.alert_threshold = 3
        self.monitoring_thread = None
        
    def create_file_baseline(self):
        """Crear línea base de archivos críticos"""
        try:
            critical_files = [
                'mal_tracker.db',
                'token.json',
                'permissions.json',
                'external_apis.json',
                'social_data.json'
            ]
            
            baseline = {}
            
            for filename in critical_files:
                filepath = os.path.join(TOKEN_PATH, filename)
                if os.path.exists(filepath):
                    # Calcular hash del archivo
                    file_hash = self.calculate_file_hash(filepath)
                    file_size = os.path.getsize(filepath)
                    file_mtime = os.path.getmtime(filepath)
                    
                    baseline[filename] = {
                        'hash': file_hash,
                        'size': file_size,
                        'mtime': file_mtime,
                        'last_check': time.time()
                    }
            
            # Guardar línea base
            baseline_file = os.path.join(TOKEN_PATH, '.file_baseline')
            with open(baseline_file, 'w') as f:
                json.dump(baseline, f, indent=2)
            
            self.baseline_hashes = baseline
            
            xbmc.log('IDS: File baseline created', xbmc.LOGINFO)
            return True
            
        except Exception as e:
            xbmc.log(f'IDS: Baseline creation error - {str(e)}', xbmc.LOGERROR)
            return False
    
    def calculate_file_hash(self, filepath):
        """Calcular hash SHA-256 de archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            xbmc.log(f'IDS: Hash calculation error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def monitor_file_integrity(self):
        """Monitorear integridad de archivos"""
        try:
            if not self.baseline_hashes:
                self.load_baseline()
            
            alerts = []
            
            for filename, baseline_info in self.baseline_hashes.items():
                filepath = os.path.join(TOKEN_PATH, filename)
                
                if not os.path.exists(filepath):
                    alerts.append({
                        'type': 'file_deleted',
                        'file': filename,
                        'severity': 'critical',
                        'timestamp': time.time()
                    })
                    continue
                
                # Verificar cambios
                current_hash = self.calculate_file_hash(filepath)
                current_size = os.path.getsize(filepath)
                current_mtime = os.path.getmtime(filepath)
                
                # Comparar con línea base
                if current_hash != baseline_info['hash']:
                    alerts.append({
                        'type': 'file_modified',
                        'file': filename,
                        'severity': 'high',
                        'old_hash': baseline_info['hash'],
                        'new_hash': current_hash,
                        'timestamp': time.time()
                    })
                
                if current_size != baseline_info['size']:
                    alerts.append({
                        'type': 'size_changed',
                        'file': filename,
                        'severity': 'medium',
                        'old_size': baseline_info['size'],
                        'new_size': current_size,
                        'timestamp': time.time()
                    })
            
            # Procesar alertas
            if alerts:
                self.process_security_alerts(alerts)
            
            return alerts
            
        except Exception as e:
            xbmc.log(f'IDS: File monitoring error - {str(e)}', xbmc.LOGERROR)
            return []
    
    def monitor_access_patterns(self):
        """Monitorear patrones de acceso sospechosos"""
        try:
            # Cargar log de auditoría
            audit_file = os.path.join(TOKEN_PATH, 'audit_log.json')
            
            if not os.path.exists(audit_file):
                return []
            
            with open(audit_file, 'r') as f:
                audit_log = json.load(f)
            
            # Analizar patrones sospechosos
            alerts = []
            current_time = time.time()
            
            # Verificar accesos frecuentes (más de 10 en 1 minuto)
            recent_actions = [
                entry for entry in audit_log 
                if current_time - entry['timestamp'] < 60
            ]
            
            if len(recent_actions) > 10:
                alerts.append({
                    'type': 'high_frequency_access',
                    'severity': 'high',
                    'count': len(recent_actions),
                    'timestamp': current_time
                })
            
            # Verificar accesos fuera de horario (ejemplo: 2-6 AM)
            night_actions = [
                entry for entry in recent_actions
                if 2 <= time.localtime(entry['timestamp']).tm_hour <= 6
            ]
            
            if night_actions:
                alerts.append({
                    'type': 'off_hours_access',
                    'severity': 'medium',
                    'count': len(night_actions),
                    'timestamp': current_time
                })
            
            # Verificar intentos de acceso a funciones administrativas
            admin_attempts = [
                entry for entry in recent_actions
                if 'admin' in entry.get('action', '').lower()
            ]
            
            if admin_attempts:
                alerts.append({
                    'type': 'admin_access_attempt',
                    'severity': 'critical',
                    'count': len(admin_attempts),
                    'timestamp': current_time
                })
            
            return alerts
            
        except Exception as e:
            xbmc.log(f'IDS: Access pattern monitoring error - {str(e)}', xbmc.LOGERROR)
            return []
    
    def detect_anomalous_behavior(self):
        """Detectar comportamiento anómalo"""
        try:
            alerts = []
            
            # Verificar uso excesivo de recursos
            if self.check_resource_usage():
                alerts.append({
                    'type': 'resource_anomaly',
                    'severity': 'medium',
                    'timestamp': time.time()
                })
            
            # Verificar conexiones de red sospechosas
            if self.check_network_connections():
                alerts.append({
                    'type': 'suspicious_network',
                    'severity': 'high',
                    'timestamp': time.time()
                })
            
            # Verificar cambios en configuración
            if self.check_config_changes():
                alerts.append({
                    'type': 'config_tampering',
                    'severity': 'critical',
                    'timestamp': time.time()
                })
            
            return alerts
            
        except Exception as e:
            xbmc.log(f'IDS: Anomaly detection error - {str(e)}', xbmc.LOGERROR)
            return []
    
    def process_security_alerts(self, alerts):
        """Procesar alertas de seguridad"""
        try:
            critical_alerts = [a for a in alerts if a['severity'] == 'critical']
            high_alerts = [a for a in alerts if a['severity'] == 'high']
            
            # Respuesta automática a alertas críticas
            if critical_alerts:
                self.trigger_emergency_response()
            
            # Notificar alertas importantes
            if high_alerts or critical_alerts:
                self.notify_security_alerts(alerts)
            
            # Guardar alertas en log
            self.log_security_alerts(alerts)
            
        except Exception as e:
            xbmc.log(f'IDS: Alert processing error - {str(e)}', xbmc.LOGERROR)
    
    def trigger_emergency_response(self):
        """Activar respuesta de emergencia"""
        try:
            # Crear archivo de bloqueo de emergencia
            lockdown_file = os.path.join(TOKEN_PATH, 'SECURITY_LOCKDOWN')
            with open(lockdown_file, 'w') as f:
                f.write(f"Security lockdown triggered at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Deshabilitar funciones críticas
            emergency_permissions = {
                'read_anime': True,
                'write_anime': False,
                'delete_anime': False,
                'export_data': False,
                'modify_settings': False,
                'access_external_apis': False,
                'admin_functions': False
            }
            
            permissions_file = os.path.join(TOKEN_PATH, 'permissions.json')
            with open(permissions_file, 'w') as f:
                json.dump(emergency_permissions, f)
            
            # Notificar usuario
            xbmcgui.Dialog().notification(
                '🚨 ALERTA DE SEGURIDAD',
                'Sistema en modo de emergencia',
                icon=xbmcgui.NOTIFICATION_ERROR,
                time=10000
            )
            
            xbmc.log('IDS: Emergency response triggered', xbmc.LOGWARNING)
            
        except Exception as e:
            xbmc.log(f'IDS: Emergency response error - {str(e)}', xbmc.LOGERROR)
    
    def notify_security_alerts(self, alerts):
        """Notificar alertas de seguridad"""
        try:
            critical_count = len([a for a in alerts if a['severity'] == 'critical'])
            high_count = len([a for a in alerts if a['severity'] == 'high'])
            
            if critical_count > 0:
                message = f"🚨 {critical_count} alertas críticas detectadas"
                xbmcgui.Dialog().notification(
                    'ALERTA CRÍTICA',
                    message,
                    icon=xbmcgui.NOTIFICATION_ERROR,
                    time=8000
                )
            elif high_count > 0:
                message = f"⚠️ {high_count} alertas importantes detectadas"
                xbmcgui.Dialog().notification(
                    'Alerta de Seguridad',
                    message,
                    icon=xbmcgui.NOTIFICATION_WARNING,
                    time=5000
                )
                
        except Exception as e:
            xbmc.log(f'IDS: Notification error - {str(e)}', xbmc.LOGERROR)
    
    def log_security_alerts(self, alerts):
        """Registrar alertas en log de seguridad"""
        try:
            security_log_file = os.path.join(TOKEN_PATH, 'security_alerts.json')
            
            # Cargar log existente
            security_log = []
            if os.path.exists(security_log_file):
                with open(security_log_file, 'r') as f:
                    security_log = json.load(f)
            
            # Agregar nuevas alertas
            security_log.extend(alerts)
            
            # Mantener solo últimas 500 alertas
            if len(security_log) > 500:
                security_log = security_log[-500:]
            
            # Guardar log actualizado
            with open(security_log_file, 'w') as f:
                json.dump(security_log, f, indent=2)
                
        except Exception as e:
            xbmc.log(f'IDS: Alert logging error - {str(e)}', xbmc.LOGERROR)
    
    def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        try:
            if self.monitoring:
                return False, "Monitoreo ya activo"
            
            # Crear línea base si no existe
            if not self.baseline_hashes:
                self.create_file_baseline()
            
            self.monitoring = True
            
            # Iniciar hilo de monitoreo
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            return True, "Monitoreo iniciado"
            
        except Exception as e:
            xbmc.log(f'IDS: Start monitoring error - {str(e)}', xbmc.LOGERROR)
            return False, f"Error: {str(e)}"
    
    def monitoring_loop(self):
        """Bucle principal de monitoreo"""
        while self.monitoring:
            try:
                # Monitorear integridad de archivos
                file_alerts = self.monitor_file_integrity()
                
                # Monitorear patrones de acceso
                access_alerts = self.monitor_access_patterns()
                
                # Detectar comportamiento anómalo
                anomaly_alerts = self.detect_anomalous_behavior()
                
                # Procesar todas las alertas
                all_alerts = file_alerts + access_alerts + anomaly_alerts
                if all_alerts:
                    self.process_security_alerts(all_alerts)
                
                # Esperar antes del siguiente ciclo
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                xbmc.log(f'IDS: Monitoring loop error - {str(e)}', xbmc.LOGERROR)
                time.sleep(60)  # Esperar más tiempo en caso de error
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        return True, "Monitoreo detenido"
    
    def check_resource_usage(self):
        """Verificar uso anómalo de recursos"""
        # Placeholder - implementar verificación real de recursos
        return False
    
    def check_network_connections(self):
        """Verificar conexiones de red sospechosas"""
        # Placeholder - implementar verificación de red
        return False
    
    def check_config_changes(self):
        """Verificar cambios no autorizados en configuración"""
        # Placeholder - implementar verificación de configuración
        return False
    
    def load_baseline(self):
        """Cargar línea base existente"""
        try:
            baseline_file = os.path.join(TOKEN_PATH, '.file_baseline')
            if os.path.exists(baseline_file):
                with open(baseline_file, 'r') as f:
                    self.baseline_hashes = json.load(f)
                return True
        except Exception as e:
            xbmc.log(f'IDS: Load baseline error - {str(e)}', xbmc.LOGERROR)
        return False

def show_ids_menu():
    """Mostrar menú del sistema de detección de intrusiones"""
    ids = IntrusionDetectionSystem()
    
    options = [
        '🛡️ Iniciar monitoreo IDS',
        '⏹️ Detener monitoreo',
        '📊 Ver alertas de seguridad',
        '🔍 Escaneo manual',
        '⚙️ Configurar IDS',
        '📋 Crear línea base',
        '🚨 Estado de emergencia'
    ]
    
    selected = xbmcgui.Dialog().select('Sistema de Detección de Intrusiones:', options)
    
    if selected == 0:
        success, message = ids.start_monitoring()
        xbmcgui.Dialog().notification('IDS', message)
    elif selected == 1:
        success, message = ids.stop_monitoring()
        xbmcgui.Dialog().notification('IDS', message)
    elif selected == 2:
        show_security_alerts()
    elif selected == 3:
        manual_security_scan(ids)
    elif selected == 4:
        configure_ids()
    elif selected == 5:
        if ids.create_file_baseline():
            xbmcgui.Dialog().notification('IDS', '✅ Línea base creada')
    elif selected == 6:
        check_emergency_status()

def show_security_alerts():
    """Mostrar alertas de seguridad"""
    try:
        security_log_file = os.path.join(TOKEN_PATH, 'security_alerts.json')
        
        if not os.path.exists(security_log_file):
            xbmcgui.Dialog().notification('IDS', 'No hay alertas registradas')
            return
        
        with open(security_log_file, 'r') as f:
            alerts = json.load(f)
        
        if not alerts:
            xbmcgui.Dialog().notification('IDS', 'No hay alertas')
            return
        
        # Mostrar últimas 10 alertas
        recent_alerts = alerts[-10:]
        
        alert_text = "🚨 ALERTAS DE SEGURIDAD RECIENTES:\n\n"
        
        for alert in reversed(recent_alerts):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert['timestamp']))
            severity_icon = {'critical': '🚨', 'high': '⚠️', 'medium': '🔶', 'low': '🔵'}.get(alert['severity'], '❓')
            
            alert_text += f"{severity_icon} {alert['type'].upper()}\n"
            alert_text += f"   Tiempo: {timestamp}\n"
            alert_text += f"   Severidad: {alert['severity']}\n"
            
            if 'file' in alert:
                alert_text += f"   Archivo: {alert['file']}\n"
            
            alert_text += "\n"
        
        xbmcgui.Dialog().textviewer('Alertas de Seguridad', alert_text)
        
    except Exception as e:
        xbmc.log(f'IDS: Show alerts error - {str(e)}', xbmc.LOGERROR)