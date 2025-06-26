import xbmc
import xbmcaddon
import xbmcgui
import urllib.parse

def check_addon_installed(addon_id):
    """Verificar si un addon está instalado"""
    try:
        addon = xbmcaddon.Addon(addon_id)
        return True
    except:
        return False

def get_available_streaming_addons():
    """Obtener addons de streaming disponibles"""
    addons = []
    
    # Verificar Alfa
    if check_addon_installed('plugin.video.alfa'):
        addons.append({
            'id': 'plugin.video.alfa',
            'name': 'Alfa',
            'icon': 'special://home/addons/plugin.video.alfa/icon.png'
        })
    
    # Verificar Balandro
    if check_addon_installed('plugin.video.balandro'):
        addons.append({
            'id': 'plugin.video.balandro', 
            'name': 'Balandro',
            'icon': 'special://home/addons/plugin.video.balandro/icon.png'
        })
    
    return addons

def search_in_alfa(query):
    """Buscar en Alfa addon"""
    try:
        # URL de búsqueda en Alfa
        search_url = f"plugin://plugin.video.alfa/?action=search&text={urllib.parse.quote(query)}"
        xbmc.executebuiltin(f'Container.Update({search_url})')
        return True
    except Exception as e:
        xbmc.log(f'MAL Tracker: Error searching in Alfa - {str(e)}', xbmc.LOGERROR)
        return False

def search_in_balandro(query):
    """Buscar en Balandro addon"""
    try:
        # URL de búsqueda en Balandro
        search_url = f"plugin://plugin.video.balandro/?action=search&text={urllib.parse.quote(query)}"
        xbmc.executebuiltin(f'Container.Update({search_url})')
        return True
    except Exception as e:
        xbmc.log(f'MAL Tracker: Error searching in Balandro - {str(e)}', xbmc.LOGERROR)
        return False

def show_streaming_options(anime_title):
    """Mostrar opciones de streaming para un anime"""
    available_addons = get_available_streaming_addons()
    
    if not available_addons:
        xbmcgui.Dialog().notification('MAL Tracker', 'No hay addons de streaming instalados')
        return False
    
    # Crear lista de opciones
    options = []
    for addon in available_addons:
        options.append(f"Buscar en {addon['name']}")
    
    # Agregar opción de instalar addons faltantes
    options.append("Instalar addons de streaming")
    
    # Mostrar diálogo de selección
    selected = xbmcgui.Dialog().select(f'Ver "{anime_title}" en:', options)
    
    if selected == -1:  # Cancelado
        return False
    
    if selected == len(options) - 1:  # Instalar addons
        show_install_addons_info()
        return False
    
    # Buscar en el addon seleccionado
    selected_addon = available_addons[selected]
    
    if selected_addon['id'] == 'plugin.video.alfa':
        return search_in_alfa(anime_title)
    elif selected_addon['id'] == 'plugin.video.balandro':
        return search_in_balandro(anime_title)
    
    return False

def show_install_addons_info():
    """Mostrar información sobre cómo instalar addons"""
    message = """Para ver anime necesitas instalar:

• Alfa: Repositorio Alfa
• Balandro: Repositorio Balandro

¿Quieres abrir el gestor de addons?"""
    
    if xbmcgui.Dialog().yesno('Instalar Addons de Streaming', message):
        xbmc.executebuiltin('ActivateWindow(AddonBrowser)')

def create_watch_button(anime_title, anime_id):
    """Crear botón de reproducción estilo Netflix"""
    available_addons = get_available_streaming_addons()
    
    if available_addons:
        return {
            'title': f'▶ Ver "{anime_title}"',
            'action': 'watch_anime',
            'anime_title': anime_title,
            'anime_id': anime_id,
            'available': True
        }
    else:
        return {
            'title': f'📥 Instalar para ver "{anime_title}"',
            'action': 'install_streaming',
            'anime_title': anime_title,
            'anime_id': anime_id,
            'available': False
        }

def show_streaming_menu():
    """Mostrar menú de estado de streaming"""
    available_addons = get_available_streaming_addons()
    
    info = "Estado de Addons de Streaming:\n\n"
    
    # Verificar Alfa
    if check_addon_installed('plugin.video.alfa'):
        info += "✅ Alfa - Instalado\n"
    else:
        info += "❌ Alfa - No instalado\n"
    
    # Verificar Balandro  
    if check_addon_installed('plugin.video.balandro'):
        info += "✅ Balandro - Instalado\n"
    else:
        info += "❌ Balandro - No instalado\n"
    
    info += f"\nTotal disponibles: {len(available_addons)}/2"
    
    if len(available_addons) == 0:
        info += "\n\n⚠️ Instala al menos un addon para ver anime"
    
    xbmcgui.Dialog().textviewer('Estado de Streaming', info)