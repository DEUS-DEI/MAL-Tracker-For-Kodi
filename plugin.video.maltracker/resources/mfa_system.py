import secrets
import time
import hashlib
import hmac
import base64
import qrcode
import io
import xbmc
import xbmcgui
from .config import TOKEN_PATH
import os
import json

class MFASystem:
    
    def __init__(self):
        self.secret_length = 32
        self.code_length = 6
        self.time_window = 30  # 30 segundos
        
    def generate_secret(self):
        """Generar secreto para TOTP"""
        return base64.b32encode(secrets.token_bytes(self.secret_length)).decode()
    
    def generate_totp(self, secret, timestamp=None):
        """Generar código TOTP"""
        if timestamp is None:
            timestamp = int(time.time())
        
        # Calcular contador basado en tiempo
        counter = timestamp // self.time_window
        
        # Convertir a bytes
        counter_bytes = counter.to_bytes(8, byteorder='big')
        secret_bytes = base64.b32decode(secret)
        
        # Generar HMAC-SHA1
        hmac_hash = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()
        
        # Extraer código de 6 dígitos
        offset = hmac_hash[-1] & 0x0f
        code = (
            (hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff)
        ) % (10 ** self.code_length)
        
        return f"{code:0{self.code_length}d}"
    
    def verify_totp(self, secret, user_code, window=1):
        """Verificar código TOTP con ventana de tolerancia"""
        current_time = int(time.time())
        
        # Verificar código actual y ventanas adyacentes
        for i in range(-window, window + 1):
            timestamp = current_time + (i * self.time_window)
            expected_code = self.generate_totp(secret, timestamp)
            
            if hmac.compare_digest(expected_code, user_code):
                return True
        
        return False
    
    def setup_mfa(self):
        """Configurar autenticación multi-factor"""
        try:
            # Generar secreto único
            secret = self.generate_secret()
            
            # Crear URI para QR
            app_name = "MAL Tracker"
            account_name = "Kodi User"
            
            totp_uri = f"otpauth://totp/{app_name}:{account_name}?secret={secret}&issuer={app_name}"
            
            # Mostrar información de configuración
            setup_info = f"CONFIGURACIÓN MFA:\n\n"
            setup_info += f"1. Instala una app de autenticación:\n"
            setup_info += f"   • Google Authenticator\n"
            setup_info += f"   • Microsoft Authenticator\n"
            setup_info += f"   • Authy\n\n"
            setup_info += f"2. Escanea el código QR o ingresa manualmente:\n"
            setup_info += f"   Secreto: {secret}\n\n"
            setup_info += f"3. Ingresa el código de 6 dígitos para verificar"
            
            xbmcgui.Dialog().textviewer('Configurar MFA', setup_info)
            
            # Solicitar código de verificación
            verification_code = xbmcgui.Dialog().input(
                'Ingresa código de verificación (6 dígitos):',
                type=xbmcgui.INPUT_NUMERIC
            )
            
            if verification_code and len(verification_code) == 6:
                if self.verify_totp(secret, verification_code):
                    # Guardar secreto de forma segura
                    self.save_mfa_secret(secret)
                    
                    xbmcgui.Dialog().notification(
                        'MFA Configurado',
                        '✅ Autenticación multi-factor activada',
                        icon=xbmcgui.NOTIFICATION_INFO
                    )
                    return True
                else:
                    xbmcgui.Dialog().notification(
                        'MFA Error',
                        '❌ Código incorrecto',
                        icon=xbmcgui.NOTIFICATION_ERROR
                    )
            
            return False
            
        except Exception as e:
            xbmc.log(f'MFA System: Setup error - {str(e)}', xbmc.LOGERROR)
            return False
    
    def authenticate_mfa(self):
        """Autenticar con MFA"""
        try:
            secret = self.load_mfa_secret()
            if not secret:
                return False, "MFA no configurado"
            
            # Solicitar código
            user_code = xbmcgui.Dialog().input(
                'Código de autenticación (6 dígitos):',
                type=xbmcgui.INPUT_NUMERIC
            )
            
            if not user_code or len(user_code) != 6:
                return False, "Código inválido"
            
            # Verificar código
            if self.verify_totp(secret, user_code):
                return True, "Autenticación exitosa"
            else:
                return False, "Código incorrecto"
                
        except Exception as e:
            xbmc.log(f'MFA System: Auth error - {str(e)}', xbmc.LOGERROR)
            return False, "Error de autenticación"
    
    def save_mfa_secret(self, secret):
        """Guardar secreto MFA de forma segura"""
        try:
            from .military_security import MilitaryGradeSecurity
            
            # Encriptar secreto
            security = MilitaryGradeSecurity()
            
            # Usar contraseña derivada del sistema
            system_key = self.derive_system_key()
            encrypted_secret = security.encrypt_data(secret, system_key)
            
            if encrypted_secret:
                mfa_file = os.path.join(TOKEN_PATH, '.mfa_secret')
                with open(mfa_file, 'wb') as f:
                    f.write(encrypted_secret)
                
                # Ocultar archivo
                if os.name == 'nt':
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(mfa_file, 2)
                
                return True
            
        except Exception as e:
            xbmc.log(f'MFA System: Save secret error - {str(e)}', xbmc.LOGERROR)
        
        return False
    
    def load_mfa_secret(self):
        """Cargar secreto MFA"""
        try:
            mfa_file = os.path.join(TOKEN_PATH, '.mfa_secret')
            
            if not os.path.exists(mfa_file):
                return None
            
            with open(mfa_file, 'rb') as f:
                encrypted_secret = f.read()
            
            from .military_security import MilitaryGradeSecurity
            security = MilitaryGradeSecurity()
            
            system_key = self.derive_system_key()
            secret = security.decrypt_data(encrypted_secret, system_key)
            
            return secret
            
        except Exception as e:
            xbmc.log(f'MFA System: Load secret error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def derive_system_key(self):
        """Derivar clave del sistema"""
        try:
            import platform
            
            # Información única del sistema
            system_info = f"{platform.machine()}{platform.processor()}"
            
            # Crear clave derivada
            key_material = hashlib.sha256(system_info.encode()).digest()
            return base64.urlsafe_b64encode(key_material)
            
        except Exception:
            # Fallback key
            return base64.urlsafe_b64encode(b'fallback_key_32_bytes_long_here')
    
    def backup_codes_generate(self):
        """Generar códigos de respaldo"""
        try:
            backup_codes = []
            
            for _ in range(10):  # 10 códigos de respaldo
                code = secrets.token_hex(4).upper()  # 8 caracteres
                backup_codes.append(code)
            
            # Guardar códigos de forma segura
            self.save_backup_codes(backup_codes)
            
            # Mostrar códigos al usuario
            codes_text = "CÓDIGOS DE RESPALDO MFA:\n\n"
            codes_text += "⚠️ IMPORTANTE: Guarda estos códigos en un lugar seguro.\n"
            codes_text += "Cada código solo se puede usar una vez.\n\n"
            
            for i, code in enumerate(backup_codes, 1):
                codes_text += f"{i:2d}. {code}\n"
            
            xbmcgui.Dialog().textviewer('Códigos de Respaldo', codes_text)
            
            return backup_codes
            
        except Exception as e:
            xbmc.log(f'MFA System: Backup codes error - {str(e)}', xbmc.LOGERROR)
            return []
    
    def save_backup_codes(self, codes):
        """Guardar códigos de respaldo"""
        try:
            backup_data = {
                'codes': codes,
                'used': [False] * len(codes),
                'created': int(time.time())
            }
            
            backup_file = os.path.join(TOKEN_PATH, '.mfa_backup')
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f)
            
            # Ocultar archivo
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(backup_file, 2)
                
        except Exception as e:
            xbmc.log(f'MFA System: Save backup codes error - {str(e)}', xbmc.LOGERROR)
    
    def verify_backup_code(self, user_code):
        """Verificar código de respaldo"""
        try:
            backup_file = os.path.join(TOKEN_PATH, '.mfa_backup')
            
            if not os.path.exists(backup_file):
                return False
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            codes = backup_data['codes']
            used = backup_data['used']
            
            # Buscar código
            for i, code in enumerate(codes):
                if code.upper() == user_code.upper() and not used[i]:
                    # Marcar como usado
                    used[i] = True
                    backup_data['used'] = used
                    
                    # Guardar estado actualizado
                    with open(backup_file, 'w') as f:
                        json.dump(backup_data, f)
                    
                    return True
            
            return False
            
        except Exception as e:
            xbmc.log(f'MFA System: Verify backup code error - {str(e)}', xbmc.LOGERROR)
            return False

def show_mfa_menu():
    """Mostrar menú MFA"""
    mfa = MFASystem()
    
    options = [
        '🔐 Configurar MFA',
        '🔑 Autenticar con MFA',
        '📋 Generar códigos de respaldo',
        '🔓 Usar código de respaldo',
        '❌ Desactivar MFA'
    ]
    
    selected = xbmcgui.Dialog().select('Autenticación Multi-Factor:', options)
    
    if selected == 0:
        mfa.setup_mfa()
    elif selected == 1:
        success, message = mfa.authenticate_mfa()
        xbmcgui.Dialog().notification('MFA', message)
    elif selected == 2:
        mfa.backup_codes_generate()
    elif selected == 3:
        backup_code = xbmcgui.Dialog().input('Código de respaldo:')
        if backup_code and mfa.verify_backup_code(backup_code):
            xbmcgui.Dialog().notification('MFA', '✅ Código de respaldo válido')
        else:
            xbmcgui.Dialog().notification('MFA', '❌ Código inválido')
    elif selected == 4:
        if xbmcgui.Dialog().yesno('Desactivar MFA', '¿Estás seguro?'):
            # Eliminar archivos MFA
            try:
                mfa_files = ['.mfa_secret', '.mfa_backup']
                for filename in mfa_files:
                    filepath = os.path.join(TOKEN_PATH, filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                
                xbmcgui.Dialog().notification('MFA', '❌ MFA desactivado')
            except Exception as e:
                xbmc.log(f'MFA: Disable error - {str(e)}', xbmc.LOGERROR)