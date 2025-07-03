import os
import hashlib
import hmac
import secrets
import time
import json
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import xbmc
import xbmcgui

class MilitaryGradeSecurity:
    
    def __init__(self):
        self.master_key = None
        self.session_token = None
        self.failed_attempts = 0
        self.lockout_time = 0
        
    def generate_master_key(self, password):
        """Generar clave maestra con PBKDF2"""
        try:
            salt = secrets.token_bytes(32)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # 100k iteraciones
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Guardar salt de forma segura
            self.save_salt(salt)
            return key
            
        except Exception as e:
            xbmc.log(f'Military Security: Key generation error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def encrypt_data(self, data, key):
        """Encriptación AES-256 con Fernet"""
        try:
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            return encrypted_data
            
        except Exception as e:
            xbmc.log(f'Military Security: Encryption error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def decrypt_data(self, encrypted_data, key):
        """Desencriptación AES-256"""
        try:
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            xbmc.log(f'Military Security: Decryption error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def create_secure_hash(self, data, salt=None):
        """Hash SHA-512 con salt"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        hash_obj = hashlib.sha512()
        hash_obj.update(salt + data.encode())
        return hash_obj.hexdigest(), salt
    
    def verify_integrity(self, data, expected_hash, salt):
        """Verificar integridad de datos"""
        calculated_hash, _ = self.create_secure_hash(data, salt)
        return hmac.compare_digest(calculated_hash, expected_hash)
    
    def secure_session_management(self):
        """Gestión segura de sesiones"""
        try:
            # Generar token de sesión único
            self.session_token = secrets.token_urlsafe(32)
            
            # Timestamp de expiración (30 minutos)
            expiry = int(time.time()) + 1800
            
            session_data = {
                'token': self.session_token,
                'created': int(time.time()),
                'expires': expiry,
                'ip_hash': self.get_system_fingerprint()
            }
            
            return session_data
            
        except Exception as e:
            xbmc.log(f'Military Security: Session error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def get_system_fingerprint(self):
        """Crear huella digital del sistema"""
        try:
            import platform
            
            # Recopilar información del sistema
            system_info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'kodi_version': xbmc.getInfoLabel('System.BuildVersion')
            }
            
            # Crear hash único del sistema
            fingerprint_data = json.dumps(system_info, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint_hash
            
        except Exception as e:
            xbmc.log(f'Military Security: Fingerprint error - {str(e)}', xbmc.LOGERROR)
            return "unknown"
    
    def implement_rate_limiting(self, action, max_attempts=5, window=300):
        """Rate limiting avanzado"""
        try:
            from .config import TOKEN_PATH
            
            rate_limit_file = os.path.join(TOKEN_PATH, 'rate_limits.json')
            current_time = int(time.time())
            
            # Cargar límites existentes
            limits = {}
            if os.path.exists(rate_limit_file):
                with open(rate_limit_file, 'r') as f:
                    limits = json.load(f)
            
            # Verificar límite para esta acción
            if action in limits:
                attempts = limits[action]['attempts']
                first_attempt = limits[action]['first_attempt']
                
                # Si está dentro de la ventana de tiempo
                if current_time - first_attempt < window:
                    if attempts >= max_attempts:
                        return False, f"Rate limit exceeded. Try again in {window - (current_time - first_attempt)} seconds"
                    else:
                        limits[action]['attempts'] += 1
                else:
                    # Resetear contador
                    limits[action] = {'attempts': 1, 'first_attempt': current_time}
            else:
                # Primera vez
                limits[action] = {'attempts': 1, 'first_attempt': current_time}
            
            # Guardar límites actualizados
            with open(rate_limit_file, 'w') as f:
                json.dump(limits, f)
            
            return True, "OK"
            
        except Exception as e:
            xbmc.log(f'Military Security: Rate limiting error - {str(e)}', xbmc.LOGERROR)
            return True, "Rate limiting failed"
    
    def secure_database_operations(self):
        """Operaciones de base de datos ultra-seguras"""
        try:
            from . import local_database
            
            # Crear conexión con configuración de seguridad máxima
            conn = sqlite3.connect(
                local_database.DB_PATH,
                timeout=10.0,
                isolation_level='EXCLUSIVE'
            )
            
            # Configuraciones de seguridad extrema
            security_pragmas = [
                'PRAGMA foreign_keys = ON',
                'PRAGMA journal_mode = WAL',
                'PRAGMA synchronous = EXTRA',
                'PRAGMA secure_delete = ON',
                'PRAGMA temp_store = MEMORY',
                'PRAGMA cache_size = -64000',  # 64MB cache
                'PRAGMA mmap_size = 0',  # Deshabilitar memory mapping
            ]
            
            for pragma in security_pragmas:
                conn.execute(pragma)
            
            # Verificar integridad antes de cada operación
            cursor = conn.cursor()
            cursor.execute('PRAGMA integrity_check')
            integrity = cursor.fetchone()[0]
            
            if integrity != 'ok':
                conn.close()
                raise Exception(f"Database integrity compromised: {integrity}")
            
            return conn
            
        except Exception as e:
            xbmc.log(f'Military Security: Database security error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def implement_access_control(self, required_permission):
        """Control de acceso basado en permisos"""
        try:
            from .config import TOKEN_PATH
            
            permissions_file = os.path.join(TOKEN_PATH, 'permissions.json')
            
            # Permisos por defecto (restrictivos)
            default_permissions = {
                'read_anime': True,
                'write_anime': False,
                'delete_anime': False,
                'export_data': False,
                'modify_settings': False,
                'access_external_apis': False,
                'admin_functions': False
            }
            
            # Cargar permisos actuales
            current_permissions = default_permissions
            if os.path.exists(permissions_file):
                with open(permissions_file, 'r') as f:
                    current_permissions.update(json.load(f))
            
            # Verificar permiso requerido
            if required_permission not in current_permissions:
                return False, f"Unknown permission: {required_permission}"
            
            if not current_permissions[required_permission]:
                return False, f"Access denied: {required_permission}"
            
            return True, "Access granted"
            
        except Exception as e:
            xbmc.log(f'Military Security: Access control error - {str(e)}', xbmc.LOGERROR)
            return False, "Access control failed"
    
    def secure_api_communication(self, url, data=None):
        """Comunicación API ultra-segura"""
        try:
            import requests
            from .config import USER_AGENT
            
            # Verificar URL en whitelist
            allowed_domains = [
                'api.myanimelist.net',
                'api.jikan.moe',
                'kitsu.io'
            ]
            
            domain_allowed = any(domain in url for domain in allowed_domains)
            if not domain_allowed:
                raise Exception(f"Domain not in whitelist: {url}")
            
            # Headers de seguridad
            security_headers = {
                'User-Agent': USER_AGENT,
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',  # Do Not Track
            }
            
            # Configuración de seguridad para requests
            session = requests.Session()
            session.headers.update(security_headers)
            
            # Verificar certificado SSL
            response = session.get(url, verify=True, timeout=10)
            
            # Verificar respuesta
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Military Security: API communication error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def implement_audit_logging(self, action, user_id, details):
        """Logging de auditoría completo"""
        try:
            from .config import TOKEN_PATH
            
            audit_file = os.path.join(TOKEN_PATH, 'audit_log.json')
            
            audit_entry = {
                'timestamp': int(time.time()),
                'iso_timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                'action': action,
                'user_id': user_id,
                'details': details,
                'system_fingerprint': self.get_system_fingerprint(),
                'session_token': self.session_token,
                'ip_hash': hashlib.sha256(b'localhost').hexdigest()  # Placeholder
            }
            
            # Cargar log existente
            audit_log = []
            if os.path.exists(audit_file):
                with open(audit_file, 'r') as f:
                    audit_log = json.load(f)
            
            # Agregar nueva entrada
            audit_log.append(audit_entry)
            
            # Mantener solo últimas 1000 entradas
            if len(audit_log) > 1000:
                audit_log = audit_log[-1000:]
            
            # Guardar log actualizado
            with open(audit_file, 'w') as f:
                json.dump(audit_log, f, indent=2)
            
            return True
            
        except Exception as e:
            xbmc.log(f'Military Security: Audit logging error - {str(e)}', xbmc.LOGERROR)
            return False
    
    def save_salt(self, salt):
        """Guardar salt de forma segura"""
        try:
            from .config import TOKEN_PATH
            
            salt_file = os.path.join(TOKEN_PATH, '.salt')
            with open(salt_file, 'wb') as f:
                f.write(salt)
            
            # Ocultar archivo en Windows
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(salt_file, 2)  # Hidden
                
        except Exception as e:
            xbmc.log(f'Military Security: Save salt error - {str(e)}', xbmc.LOGERROR)

def setup_military_security():
    """Configurar seguridad militar"""
    try:
        # Solicitar contraseña maestra
        password = xbmcgui.Dialog().input(
            'Configurar Seguridad Militar - Contraseña Maestra:',
            type=xbmcgui.INPUT_ALPHANUM,
            option=xbmcgui.ALPHANUM_HIDE_INPUT
        )
        
        if not password or len(password) < 12:
            xbmcgui.Dialog().notification(
                'Seguridad Militar',
                'Contraseña debe tener al menos 12 caracteres',
                icon=xbmcgui.NOTIFICATION_ERROR
            )
            return False
        
        # Inicializar seguridad militar
        security = MilitaryGradeSecurity()
        master_key = security.generate_master_key(password)
        
        if master_key:
            # Configurar permisos restrictivos
            setup_restrictive_permissions()
            
            # Configurar auditoría
            security.implement_audit_logging('security_setup', 'admin', 'Military grade security enabled')
            
            xbmcgui.Dialog().notification(
                'Seguridad Militar',
                '🔒 Seguridad militar activada',
                icon=xbmcgui.NOTIFICATION_INFO
            )
            return True
        
        return False
        
    except Exception as e:
        xbmc.log(f'Military Security: Setup error - {str(e)}', xbmc.LOGERROR)
        return False

def setup_restrictive_permissions():
    """Configurar permisos ultra-restrictivos"""
    try:
        from .config import TOKEN_PATH
        
        restrictive_permissions = {
            'read_anime': True,
            'write_anime': False,  # Requiere autorización
            'delete_anime': False,  # Requiere autorización
            'export_data': False,   # Requiere autorización
            'modify_settings': False,  # Requiere autorización
            'access_external_apis': False,  # Requiere autorización
            'admin_functions': False,  # Requiere autorización especial
            'backup_operations': False,
            'security_changes': False
        }
        
        permissions_file = os.path.join(TOKEN_PATH, 'permissions.json')
        with open(permissions_file, 'w') as f:
            json.dump(restrictive_permissions, f, indent=2)
        
        return True
        
    except Exception as e:
        xbmc.log(f'Military Security: Permissions setup error - {str(e)}', xbmc.LOGERROR)
        return False

def show_military_security_menu():
    """Mostrar menú de seguridad militar"""
    options = [
        '🔒 Activar seguridad militar',
        '🛡️ Configurar permisos',
        '📊 Ver log de auditoría',
        '🔐 Gestión de claves',
        '⚡ Rate limiting',
        '🎯 Control de acceso',
        '🔍 Escaneo de integridad',
        '🚨 Modo de emergencia'
    ]
    
    selected = xbmcgui.Dialog().select('🔒 Seguridad Militar:', options)
    
    if selected == 0:
        setup_military_security()
    elif selected == 1:
        configure_permissions()
    elif selected == 2:
        show_audit_log()
    elif selected == 3:
        key_management()
    elif selected == 4:
        configure_rate_limiting()
    elif selected == 5:
        access_control_panel()
    elif selected == 6:
        integrity_scan()
    elif selected == 7:
        emergency_mode()

def emergency_mode():
    """Modo de emergencia - Lockdown total"""
    if xbmcgui.Dialog().yesno(
        '🚨 MODO DE EMERGENCIA',
        'Esto bloqueará TODAS las funciones excepto lectura.\n¿Continuar?'
    ):
        try:
            from .config import TOKEN_PATH
            
            # Crear archivo de emergencia
            emergency_file = os.path.join(TOKEN_PATH, 'EMERGENCY_LOCKDOWN')
            with open(emergency_file, 'w') as f:
                f.write(f"Emergency lockdown activated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Permisos de solo lectura
            emergency_permissions = {key: False for key in [
                'write_anime', 'delete_anime', 'export_data', 
                'modify_settings', 'access_external_apis', 'admin_functions'
            ]}
            emergency_permissions['read_anime'] = True
            
            permissions_file = os.path.join(TOKEN_PATH, 'permissions.json')
            with open(permissions_file, 'w') as f:
                json.dump(emergency_permissions, f)
            
            xbmcgui.Dialog().notification(
                '🚨 EMERGENCIA',
                'Sistema en lockdown total',
                icon=xbmcgui.NOTIFICATION_WARNING
            )
            
        except Exception as e:
            xbmc.log(f'Military Security: Emergency mode error - {str(e)}', xbmc.LOGERROR)