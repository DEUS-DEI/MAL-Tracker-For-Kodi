import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon

def show_settings_menu(handle, base_url, icon, fanart):
    """Menú principal de configuración"""
    xbmcplugin.setPluginCategory(handle, 'Configuración y Cuentas')
    xbmcplugin.setContent(handle, 'files')
    
    # Verificar autenticación
    from . import auth
    is_authenticated = auth.load_access_token() is not None
    
    menu_items = [
        ('🔧 Configuración del Addon', 'addon_settings'),
        ('🔑 Cuentas y Autenticación', 'auth_menu'),
        ('🔄 Sincronización', 'sync_menu'),
        ('📥 Importar/Exportar', 'import_export_menu'),
        ('🔒 Seguridad', 'security_menu_settings'),
        ('📊 Estadísticas de Uso', 'usage_stats'),
        ('🔧 Herramientas Avanzadas', 'advanced_tools'),
        ('ℹ️ Información del Sistema', 'system_info')
    ]
    
    for title, action in menu_items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    
    xbmcplugin.endOfDirectory(handle)

def show_auth_menu(handle, base_url, icon, fanart):
    """Menú de autenticación y cuentas"""
    xbmcplugin.setPluginCategory(handle, 'Cuentas y Autenticación')
    xbmcplugin.setContent(handle, 'files')
    
    from . import auth
    is_authenticated = auth.load_access_token() is not None
    
    if is_authenticated:
        # Usuario autenticado
        menu_items = [
            ('👤 Mi Lista de Anime', 'list'),
            ('🔍 Búsqueda Privada', 'search'),
            ('🔄 Sincronizar Ahora', 'sync_now'),
            ('📊 Estado de Sincronización', 'sync_status'),
            ('🔑 Reautenticar', 'auth'),
            ('🚪 Cerrar Sesión', 'logout')
        ]
    else:
        # Usuario no autenticado
        menu_items = [
            ('🔑 Iniciar Sesión con MAL', 'auth'),
            ('📋 Configurar API Keys', 'configure_api'),
            ('❓ Ayuda de Autenticación', 'auth_help'),
            ('📥 Importar Configuración', 'import_config')
        ]
    
    for title, action in menu_items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        is_folder = action in ['sync_status', 'auth_help']
        xbmcplugin.addDirectoryItem(handle, url, li, is_folder)
    
    xbmcplugin.endOfDirectory(handle)

def show_sync_menu(handle, base_url, icon, fanart):
    """Menú de sincronización"""
    xbmcplugin.setPluginCategory(handle, 'Sincronización')
    xbmcplugin.setContent(handle, 'files')
    
    from . import auth, sync_manager
    is_authenticated = auth.load_access_token() is not None
    
    if is_authenticated:
        sync_status = sync_manager.get_sync_status()
        
        menu_items = [
            (f'🔄 Sincronizar Ahora ({sync_status.get("unsynced_count", 0)} pendientes)', 'sync_now'),
            ('📊 Estado de Sincronización', 'sync_status'),
            ('🔧 Configurar Sincronización', 'sync_settings'),
            ('📈 Compatibilidad', 'sync_compatibility'),
            ('🔄 Sincronización Automática', 'auto_sync_toggle'),
            ('📋 Historial de Sincronización', 'sync_history')
        ]
    else:
        menu_items = [
            ('🔒 Requiere Autenticación', 'auth_required'),
            ('❓ ¿Qué es la Sincronización?', 'sync_help')
        ]
    
    for title, action in menu_items:
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': icon, 'fanart': fanart})
        url = f"{base_url}?action={action}"
        is_folder = action in ['sync_status', 'sync_help', 'sync_history']
        xbmcplugin.addDirectoryItem(handle, url, li, is_folder)
    
    xbmcplugin.endOfDirectory(handle)

def show_addon_settings():
    """Abrir configuración nativa del addon"""
    addon = xbmcaddon.Addon()
    addon.openSettings()

def show_auth_help():
    """Mostrar ayuda de autenticación"""
    help_text = """🔑 AYUDA DE AUTENTICACIÓN

Para usar funciones avanzadas necesitas:

1️⃣ CREAR APLICACIÓN EN MAL:
• Ve a: https://myanimelist.net/apiconfig
• Crea una nueva aplicación
• Copia el Client ID

2️⃣ CONFIGURAR EN KODI:
• Configuración → Addons → MAL Tracker
• Pega tu Client ID
• Client Secret es opcional

3️⃣ AUTENTICAR:
• Vuelve al menú de autenticación
• Selecciona "Iniciar Sesión con MAL"
• Sigue las instrucciones

✅ FUNCIONES SIN AUTENTICACIÓN:
• Búsqueda básica
• Top anime
• Temporadas
• Horarios
• Lista local

🔑 FUNCIONES CON AUTENTICACIÓN:
• Sincronización con MAL
• Lista personal
• Actualizar estado
• Estadísticas personales"""
    
    xbmcgui.Dialog().textviewer('Ayuda de Autenticación', help_text)

def show_sync_help():
    """Mostrar ayuda de sincronización"""
    help_text = """🔄 AYUDA DE SINCRONIZACIÓN

La sincronización conecta tu lista local con MyAnimeList.

📊 TIPOS DE SINCRONIZACIÓN:
• Manual: Sincroniza cuando lo solicites
• Automática: Sincroniza al abrir el addon
• Híbrida: Combina datos locales y remotos

⚙️ CONFIGURACIÓN:
• Intervalo de sincronización
• Resolución de conflictos
• Backup automático

🔧 COMPATIBILIDAD:
• Estados compatibles se sincronizan
• Estados locales únicos se preservan
• Conflictos se resuelven automáticamente

❓ PROBLEMAS COMUNES:
• Verifica tu conexión a internet
• Confirma que estás autenticado
• Revisa los logs para errores"""
    
    xbmcgui.Dialog().textviewer('Ayuda de Sincronización', help_text)

def show_system_info():
    """Mostrar información del sistema"""
    addon = xbmcaddon.Addon()
    
    info = f"""ℹ️ INFORMACIÓN DEL SISTEMA

📱 ADDON:
• Nombre: {addon.getAddonInfo('name')}
• Versión: {addon.getAddonInfo('version')}
• ID: {addon.getAddonInfo('id')}
• Autor: {addon.getAddonInfo('author')}

🔧 CONFIGURACIÓN:
• Perfil: {addon.getAddonInfo('profile')}
• Ruta: {addon.getAddonInfo('path')}

🌐 APIS DISPONIBLES:
• Jikan API: ✅ Activa
• MyAnimeList API: {'✅ Configurada' if addon.getSetting('client_id') else '❌ No configurada'}

📊 FUNCIONES:
• Búsqueda: ✅ Disponible
• Lista local: ✅ Disponible
• Sincronización: {'✅ Disponible' if addon.getSetting('client_id') else '❌ Requiere configuración'}
• Traducción: ✅ Disponible"""
    
    xbmcgui.Dialog().textviewer('Información del Sistema', info)

def logout_user():
    """Cerrar sesión del usuario"""
    if xbmcgui.Dialog().yesno('Cerrar Sesión', '¿Estás seguro de que quieres cerrar sesión?\n\nEsto eliminará tu token de acceso.'):
        from .config import TOKEN_FILE
        import os
        try:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            xbmcgui.Dialog().notification('MAL Tracker', 'Sesión cerrada correctamente')
        except Exception as e:
            xbmcgui.Dialog().notification('MAL Tracker', f'Error: {str(e)}')