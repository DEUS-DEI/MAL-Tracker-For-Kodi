"""
Verificador de dependencias para funciones avanzadas
"""

import xbmcgui
import xbmc

class DependencyChecker:
    
    @staticmethod
    def check_scraping_dependencies():
        """Verificar dependencias para scraping"""
        missing = []
        
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            missing.append('script.module.beautifulsoup4')
        
        try:
            import requests
        except ImportError:
            missing.append('script.module.requests')
        
        return missing
    
    @staticmethod
    def show_dependency_status():
        """Mostrar estado de dependencias"""
        missing = DependencyChecker.check_scraping_dependencies()
        
        if not missing:
            status = """✅ DEPENDENCIAS COMPLETAS

🔧 Módulos instalados:
• BeautifulSoup4 ✅
• Requests ✅

🎬 Funciones disponibles:
• Scraping de video ✅
• Reproducción en Kodi ✅
• Extracción de enlaces ✅

Todo listo para usar scrapers."""
        
        else:
            status = f"""⚠️ DEPENDENCIAS FALTANTES

❌ Módulos faltantes:
{chr(10).join([f'• {dep}' for dep in missing])}

🔧 SOLUCIÓN:
1. Ve a Configuración → Addons
2. Busca e instala los módulos faltantes
3. O instala desde repositorio oficial

📱 ALTERNATIVA:
Usa opciones de navegador externo
que no requieren dependencias."""
        
        xbmcgui.Dialog().textviewer('Estado de Dependencias', status)
    
    @staticmethod
    def auto_install_dependencies():
        """Intentar instalación automática"""
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno('Instalar Dependencias',
            'Se intentará instalar automáticamente:\n\n'
            '• script.module.beautifulsoup4\n'
            '• script.module.requests\n\n'
            '¿Continuar?'):
            
            try:
                # Intentar instalación via JSON-RPC
                import json
                
                # Comando para instalar addon
                install_cmd = {
                    "jsonrpc": "2.0",
                    "method": "Addons.InstallAddon",
                    "params": {"addonid": "script.module.beautifulsoup4"},
                    "id": 1
                }
                
                # Esto requiere implementación más compleja
                dialog.ok('Instalación Manual',
                    'Por favor instala manualmente:\n\n'
                    '1. Ve a Configuración → Addons\n'
                    '2. Instalar desde repositorio\n'
                    '3. Busca "BeautifulSoup4"\n'
                    '4. Instala script.module.beautifulsoup4')
                
            except Exception as e:
                dialog.ok('Error de Instalación',
                    f'No se pudo instalar automáticamente.\n\n'
                    f'Error: {str(e)}\n\n'
                    'Instala manualmente desde repositorio.')
    
    @staticmethod
    def get_fallback_options():
        """Obtener opciones alternativas sin dependencias"""
        return [
            {
                'title': '🌐 Abrir en navegador (sin dependencias)',
                'description': 'Usa navegador externo para ver anime',
                'requires_deps': False
            },
            {
                'title': '🔍 Búsqueda directa en sitios',
                'description': 'Enlaces directos a sitios de streaming',
                'requires_deps': False
            },
            {
                'title': '▶️ Reproducción en Kodi (requiere deps)',
                'description': 'Scraping y reproducción integrada',
                'requires_deps': True
            }
        ]