"""
Gestor de servicios - Configuración y selección de API
"""

import xbmcgui
import xbmc
from . import anilist_auth, auth as mal_auth, hybrid_api

class ServiceManager:
    
    @staticmethod
    def show_service_selection_menu():
        """Menú para seleccionar servicio preferido"""
        options = [
            '🔵 Configurar AniList (Recomendado)',
            '🔴 Configurar MyAnimeList',
            '🔄 Configurar ambos (Híbrido)',
            '📊 Ver estado de servicios',
            '❓ ¿Cuál elegir?'
        ]
        
        selected = xbmcgui.Dialog().select('Configuración de Servicios:', options)
        
        if selected == 0:  # AniList
            ServiceManager.setup_anilist()
        elif selected == 1:  # MAL
            ServiceManager.setup_mal()
        elif selected == 2:  # Híbrido
            ServiceManager.setup_hybrid()
        elif selected == 3:  # Estado
            hybrid_api.HybridAPI.show_service_status()
        elif selected == 4:  # Ayuda
            ServiceManager.show_service_comparison()
    
    @staticmethod
    def setup_anilist():
        """Configurar AniList como principal"""
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno('Configurar AniList', 
            'AniList es la opción recomendada:\n\n'
            '✅ API más estable\n'
            '✅ Sin límites estrictos\n'
            '✅ Interfaz moderna\n'
            '✅ Mejor para desarrollo\n\n'
            '¿Continuar con AniList?'):
            
            # Mostrar instrucciones
            dialog.ok('Instrucciones AniList',
                'PASOS PARA CONFIGURAR:\n\n'
                '1. Ve a https://anilist.co/settings/developer\n'
                '2. Crea nueva aplicación\n'
                '3. Redirect URL: http://localhost:8080/callback\n'
                '4. Copia Client ID y Client Secret\n'
                '5. Configúralos en el addon')
            
            # Abrir configuración
            import xbmcaddon
            addon = xbmcaddon.Addon()
            addon.openSettings()
    
    @staticmethod
    def setup_mal():
        """Configurar MAL"""
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno('Configurar MyAnimeList',
            'MyAnimeList tiene limitaciones:\n\n'
            '⚠️ Rate limits estrictos\n'
            '⚠️ OAuth más complejo\n'
            '⚠️ API menos estable\n\n'
            'Pero es más popular.\n\n'
            '¿Continuar con MAL?'):
            
            dialog.ok('Instrucciones MAL',
                'PASOS PARA CONFIGURAR:\n\n'
                '1. Ve a https://myanimelist.net/apiconfig\n'
                '2. Crea nueva aplicación\n'
                '3. App Redirect URL: http://localhost:8080/callback\n'
                '4. Copia Client ID\n'
                '5. Configúralo en el addon')
            
            import xbmcaddon
            addon = xbmcaddon.Addon()
            addon.openSettings()
    
    @staticmethod
    def setup_hybrid():
        """Configurar sistema híbrido"""
        dialog = xbmcgui.Dialog()
        
        dialog.ok('Sistema Híbrido',
            'CONFIGURACIÓN HÍBRIDA (Recomendada):\n\n'
            '🔵 AniList como principal\n'
            '🔴 MAL como backup\n\n'
            'VENTAJAS:\n'
            '• Máxima disponibilidad\n'
            '• Fallback automático\n'
            '• Sincronización cruzada\n'
            '• Mejor experiencia')
        
        # Configurar AniList primero
        if dialog.yesno('Paso 1/2', '¿Configurar AniList primero?'):
            ServiceManager.setup_anilist()
        
        # Luego MAL
        if dialog.yesno('Paso 2/2', '¿Configurar MAL como backup?'):
            ServiceManager.setup_mal()
    
    @staticmethod
    def show_service_comparison():
        """Mostrar comparación detallada"""
        comparison = """🥊 ANILIST vs MYANIMELIST

🔵 ANILIST (Recomendado):
✅ API GraphQL flexible
✅ 90 requests/minuto
✅ OAuth más estable
✅ Interfaz moderna
✅ Estadísticas avanzadas
✅ Búsqueda potente
✅ Actualizaciones rápidas
❌ Menos popular

🔴 MYANIMELIST:
✅ Más popular (50M+ usuarios)
✅ Base de datos más grande
✅ Mejor comunidad
✅ Estándar universal
❌ API REST limitado
❌ 1 request/segundo
❌ OAuth problemático
❌ Interfaz antigua

🏆 RECOMENDACIÓN:
• Usa AniList como principal
• MAL como backup opcional
• Sistema híbrido = Mejor experiencia

🎯 PARA ESTE ADDON:
AniList es técnicamente superior
y más confiable para desarrollo."""
        
        xbmcgui.Dialog().textviewer('Comparación de Servicios', comparison)
    
    @staticmethod
    def auto_detect_best_service():
        """Detectar automáticamente el mejor servicio disponible"""
        anilist_token = anilist_auth.load_access_token()
        mal_token = mal_auth.load_access_token()
        
        if anilist_token and mal_token:
            return 'hybrid'  # Ambos disponibles
        elif anilist_token:
            return 'anilist'  # Solo AniList
        elif mal_token:
            return 'mal'  # Solo MAL
        else:
            return None  # Ninguno configurado
    
    @staticmethod
    def show_quick_setup():
        """Setup rápido recomendado"""
        dialog = xbmcgui.Dialog()
        
        current_service = ServiceManager.auto_detect_best_service()
        
        if current_service == 'hybrid':
            dialog.ok('✅ Configuración Óptima',
                'Ya tienes la configuración ideal:\n\n'
                '🔵 AniList: Conectado\n'
                '🔴 MAL: Conectado\n\n'
                'Sistema híbrido activo con\n'
                'fallback automático.')
            return
        
        elif current_service == 'anilist':
            dialog.ok('✅ Configuración Buena',
                'Tienes AniList configurado:\n\n'
                '🔵 AniList: Conectado\n'
                '🔴 MAL: No configurado\n\n'
                'Opcionalmente puedes agregar\n'
                'MAL como backup.')
            return
        
        elif current_service == 'mal':
            if dialog.yesno('⚠️ Configuración Subóptima',
                'Solo tienes MAL configurado:\n\n'
                '🔴 MAL: Conectado\n'
                '🔵 AniList: No configurado\n\n'
                'Se recomienda agregar AniList\n'
                'para mejor rendimiento.\n\n'
                '¿Configurar AniList ahora?'):
                ServiceManager.setup_anilist()
            return
        
        else:
            # Ningún servicio configurado
            if dialog.yesno('🚀 Setup Rápido',
                'No tienes servicios configurados.\n\n'
                'Se recomienda AniList por:\n'
                '• API más estable\n'
                '• Mejor rendimiento\n'
                '• Menos restricciones\n\n'
                '¿Configurar AniList ahora?'):
                ServiceManager.setup_anilist()
            else:
                ServiceManager.show_service_selection_menu()