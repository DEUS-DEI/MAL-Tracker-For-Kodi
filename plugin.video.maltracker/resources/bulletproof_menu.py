import xbmcgui
from .bulletproof_system import show_bulletproof_status
from .system_monitor import show_system_monitor_menu

def show_bulletproof_menu():
    """Mostrar menú del sistema bulletproof"""
    options = [
        '🛡️ Estado del sistema',
        '📊 Monitor del sistema',
        '🔧 Reparación automática'
    ]
    
    selected = xbmcgui.Dialog().select('🛡️ Sistema Bulletproof:', options)
    
    if selected == 0:
        show_bulletproof_status()
    elif selected == 1:
        show_system_monitor_menu()
    elif selected == 2:
        xbmcgui.Dialog().notification('Bulletproof', '✅ Reparación iniciada')