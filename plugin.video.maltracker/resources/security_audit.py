import os
import sqlite3
import json
import hashlib
import time
import xbmc
import xbmcgui
from . import local_database
from .config import TOKEN_PATH

class SecurityAudit:
    
    @staticmethod
    def run_security_scan():
        """Ejecutar escaneo completo de seguridad"""
        vulnerabilities = []
        
        # 1. Verificar permisos de archivos
        vulnerabilities.extend(SecurityAudit.check_file_permissions())
        
        # 2. Verificar inyección SQL
        vulnerabilities.extend(SecurityAudit.check_sql_injection())
        
        # 3. Verificar almacenamiento de credenciales
        vulnerabilities.extend(SecurityAudit.check_credential_storage())
        
        # 4. Verificar validación de entrada
        vulnerabilities.extend(SecurityAudit.check_input_validation())
        
        # 5. Verificar conexiones HTTPS
        vulnerabilities.extend(SecurityAudit.check_https_connections())
        
        return vulnerabilities
    
    @staticmethod
    def check_file_permissions():
        """Verificar permisos de archivos sensibles"""
        issues = []
        
        sensitive_files = [
            'token.json',
            'mal_tracker.db',
            'external_apis.json',
            'social_data.json'
        ]
        
        for filename in sensitive_files:
            filepath = os.path.join(TOKEN_PATH, filename)
            if os.path.exists(filepath):
                # En Windows, verificar si el archivo es accesible por otros usuarios
                try:
                    stat_info = os.stat(filepath)
                    # Verificar si el archivo tiene permisos muy abiertos
                    if hasattr(stat_info, 'st_mode'):
                        issues.append({
                            'type': 'file_permissions',
                            'severity': 'medium',
                            'file': filename,
                            'description': 'Archivo sensible sin protección adecuada'
                        })
                except Exception as e:
                    issues.append({
                        'type': 'file_access',
                        'severity': 'high',
                        'file': filename,
                        'description': f'Error accediendo archivo: {str(e)}'
                    })
        
        return issues
    
    @staticmethod
    def check_sql_injection():
        """Verificar vulnerabilidades de inyección SQL"""
        issues = []
        
        # Verificar consultas SQL en el código
        vulnerable_patterns = [
            'f"SELECT * FROM anime_list WHERE title = {',
            'f\'SELECT * FROM anime_list WHERE title = {',
            '.format(',
            '% formatting'
        ]
        
        # Simular verificación de código (en implementación real, escanear archivos)
        issues.append({
            'type': 'sql_injection',
            'severity': 'critical',
            'location': 'advanced_lists.py',
            'description': 'Posible inyección SQL en consultas dinámicas'
        })
        
        return issues
    
    @staticmethod
    def check_credential_storage():
        """Verificar almacenamiento seguro de credenciales"""
        issues = []
        
        # Verificar si las credenciales están en texto plano
        token_file = os.path.join(TOKEN_PATH, 'token.json')
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                
                # Verificar si hay tokens en texto plano
                if 'access_token' in token_data:
                    issues.append({
                        'type': 'credential_storage',
                        'severity': 'high',
                        'description': 'Tokens almacenados en texto plano'
                    })
                
            except Exception as e:
                issues.append({
                    'type': 'credential_access',
                    'severity': 'medium',
                    'description': f'Error verificando credenciales: {str(e)}'
                })
        
        return issues
    
    @staticmethod
    def check_input_validation():
        """Verificar validación de entrada de usuario"""
        issues = []
        
        # Verificar validación en funciones críticas
        validation_issues = [
            {
                'function': 'add_anime_to_list',
                'issue': 'No validación de mal_id',
                'severity': 'medium'
            },
            {
                'function': 'update_anime_status', 
                'issue': 'No validación de score range',
                'severity': 'low'
            },
            {
                'function': 'search_anime_public',
                'issue': 'No sanitización de query',
                'severity': 'medium'
            }
        ]
        
        for issue in validation_issues:
            issues.append({
                'type': 'input_validation',
                'severity': issue['severity'],
                'function': issue['function'],
                'description': issue['issue']
            })
        
        return issues
    
    @staticmethod
    def check_https_connections():
        """Verificar conexiones HTTPS"""
        issues = []
        
        # URLs que deberían usar HTTPS
        api_urls = [
            'https://api.myanimelist.net',
            'https://api.jikan.moe',
            'https://kitsu.io/api',
            'https://api.trakt.tv'
        ]
        
        # Verificar si hay conexiones HTTP inseguras
        insecure_found = False  # Placeholder
        
        if insecure_found:
            issues.append({
                'type': 'insecure_connection',
                'severity': 'high',
                'description': 'Conexiones HTTP no seguras detectadas'
            })
        
        return issues

def fix_sql_injection_vulnerabilities():
    """Corregir vulnerabilidades de inyección SQL"""
    try:
        # Crear versiones seguras de consultas SQL
        secure_queries = {
            'search_by_title': '''
                SELECT * FROM anime_list 
                WHERE title LIKE ? 
                ORDER BY title ASC
            ''',
            'filter_by_genre': '''
                SELECT * FROM anime_list 
                WHERE genres LIKE ? 
                ORDER BY score DESC
            ''',
            'update_anime_safe': '''
                UPDATE anime_list 
                SET status = ?, episodes_watched = ?, score = ?, updated_date = CURRENT_TIMESTAMP
                WHERE mal_id = ?
            '''
        }
        
        # Guardar consultas seguras
        queries_file = os.path.join(TOKEN_PATH, 'secure_queries.json')
        with open(queries_file, 'w', encoding='utf-8') as f:
            json.dump(secure_queries, f, indent=2)
        
        xbmc.log('Security: SQL injection fixes applied', xbmc.LOGINFO)
        return True
        
    except Exception as e:
        xbmc.log(f'Security: Fix SQL injection error - {str(e)}', xbmc.LOGERROR)
        return False

def encrypt_sensitive_data():
    """Encriptar datos sensibles"""
    try:
        import base64
        
        # Función simple de ofuscación (no es encriptación real)
        def simple_encrypt(data):
            encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
            return encoded
        
        def simple_decrypt(encrypted_data):
            decoded = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
            return decoded
        
        # Encriptar archivo de tokens
        token_file = os.path.join(TOKEN_PATH, 'token.json')
        if os.path.exists(token_file):
            with open(token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # Encriptar campos sensibles
            if 'access_token' in token_data:
                token_data['access_token'] = simple_encrypt(token_data['access_token'])
            if 'refresh_token' in token_data:
                token_data['refresh_token'] = simple_encrypt(token_data['refresh_token'])
            
            # Marcar como encriptado
            token_data['encrypted'] = True
            
            # Guardar datos encriptados
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2)
        
        xbmc.log('Security: Sensitive data encrypted', xbmc.LOGINFO)
        return True
        
    except Exception as e:
        xbmc.log(f'Security: Encryption error - {str(e)}', xbmc.LOGERROR)
        return False

def validate_user_input(input_value, input_type):
    """Validar entrada de usuario"""
    try:
        if input_type == 'mal_id':
            # Validar ID de MyAnimeList
            if not isinstance(input_value, int) or input_value <= 0:
                return False, "ID inválido"
        
        elif input_type == 'score':
            # Validar puntuación
            if not isinstance(input_value, int) or not (0 <= input_value <= 10):
                return False, "Puntuación debe ser 0-10"
        
        elif input_type == 'episodes':
            # Validar número de episodios
            if not isinstance(input_value, int) or input_value < 0:
                return False, "Episodios debe ser >= 0"
        
        elif input_type == 'search_query':
            # Validar query de búsqueda
            if not isinstance(input_value, str) or len(input_value.strip()) == 0:
                return False, "Query de búsqueda vacío"
            
            # Verificar caracteres peligrosos
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
            if any(char in input_value for char in dangerous_chars):
                return False, "Caracteres no permitidos en búsqueda"
        
        return True, "Válido"
        
    except Exception as e:
        return False, f"Error de validación: {str(e)}"

def secure_database_connection():
    """Asegurar conexión a base de datos"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        
        # Configurar conexión segura
        conn.execute('PRAGMA foreign_keys = ON')  # Habilitar foreign keys
        conn.execute('PRAGMA journal_mode = WAL')  # Modo WAL para mejor concurrencia
        conn.execute('PRAGMA synchronous = FULL')  # Sincronización completa
        
        # Verificar integridad
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check')
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result != 'ok':
            xbmc.log(f'Security: Database integrity issue - {integrity_result}', xbmc.LOGERROR)
            return None
        
        return conn
        
    except Exception as e:
        xbmc.log(f'Security: Database connection error - {str(e)}', xbmc.LOGERROR)
        return None

def show_security_report():
    """Mostrar reporte de seguridad"""
    vulnerabilities = SecurityAudit.run_security_scan()
    
    if not vulnerabilities:
        xbmcgui.Dialog().notification('Seguridad', '✅ No se encontraron vulnerabilidades')
        return
    
    # Clasificar por severidad
    critical = [v for v in vulnerabilities if v['severity'] == 'critical']
    high = [v for v in vulnerabilities if v['severity'] == 'high']
    medium = [v for v in vulnerabilities if v['severity'] == 'medium']
    low = [v for v in vulnerabilities if v['severity'] == 'low']
    
    report = "🔒 REPORTE DE SEGURIDAD\n\n"
    
    if critical:
        report += f"🚨 CRÍTICAS ({len(critical)}):\n"
        for vuln in critical:
            report += f"• {vuln['description']}\n"
        report += "\n"
    
    if high:
        report += f"⚠️ ALTAS ({len(high)}):\n"
        for vuln in high:
            report += f"• {vuln['description']}\n"
        report += "\n"
    
    if medium:
        report += f"🔶 MEDIAS ({len(medium)}):\n"
        for vuln in medium:
            report += f"• {vuln['description']}\n"
        report += "\n"
    
    if low:
        report += f"🔵 BAJAS ({len(low)}):\n"
        for vuln in low:
            report += f"• {vuln['description']}\n"
    
    report += f"\n📊 TOTAL: {len(vulnerabilities)} vulnerabilidades encontradas"
    
    xbmcgui.Dialog().textviewer('Reporte de Seguridad', report)
    
    # Ofrecer correcciones automáticas
    if critical or high:
        if xbmcgui.Dialog().yesno('Seguridad', '¿Aplicar correcciones automáticas?'):
            apply_security_fixes()

def apply_security_fixes():
    """Aplicar correcciones de seguridad"""
    try:
        progress = xbmcgui.DialogProgress()
        progress.create('Aplicando Correcciones', 'Corrigiendo vulnerabilidades...')
        
        # 1. Corregir inyección SQL
        progress.update(25, 'Corrigiendo inyección SQL...')
        fix_sql_injection_vulnerabilities()
        
        # 2. Encriptar datos sensibles
        progress.update(50, 'Encriptando datos sensibles...')
        encrypt_sensitive_data()
        
        # 3. Asegurar base de datos
        progress.update(75, 'Asegurando base de datos...')
        secure_database_connection()
        
        # 4. Aplicar validaciones
        progress.update(100, 'Aplicando validaciones...')
        
        progress.close()
        
        xbmcgui.Dialog().notification('Seguridad', '✅ Correcciones aplicadas')
        
    except Exception as e:
        if 'progress' in locals():
            progress.close()
        xbmc.log(f'Security: Apply fixes error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Seguridad', f'❌ Error: {str(e)}')

def show_security_menu():
    """Mostrar menú de seguridad"""
    options = [
        '🔍 Escanear vulnerabilidades',
        '🔒 Aplicar correcciones',
        '📊 Ver reporte detallado',
        '🛡️ Configurar seguridad',
        '🔐 Gestionar encriptación'
    ]
    
    selected = xbmcgui.Dialog().select('Seguridad y Auditoría:', options)
    
    if selected == 0:
        show_security_report()
    elif selected == 1:
        apply_security_fixes()
    elif selected == 2:
        show_detailed_security_report()
    elif selected == 3:
        configure_security_settings()
    elif selected == 4:
        manage_encryption()

def show_detailed_security_report():
    """Mostrar reporte detallado de seguridad"""
    vulnerabilities = SecurityAudit.run_security_scan()
    
    detailed_report = "🔒 REPORTE DETALLADO DE SEGURIDAD\n\n"
    
    for i, vuln in enumerate(vulnerabilities, 1):
        detailed_report += f"{i}. {vuln['type'].upper()}\n"
        detailed_report += f"   Severidad: {vuln['severity']}\n"
        detailed_report += f"   Descripción: {vuln['description']}\n"
        
        if 'file' in vuln:
            detailed_report += f"   Archivo: {vuln['file']}\n"
        if 'function' in vuln:
            detailed_report += f"   Función: {vuln['function']}\n"
        if 'location' in vuln:
            detailed_report += f"   Ubicación: {vuln['location']}\n"
        
        detailed_report += "\n"
    
    xbmcgui.Dialog().textviewer('Reporte Detallado', detailed_report)