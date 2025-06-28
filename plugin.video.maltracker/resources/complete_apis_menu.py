import xbmcgui
from .api_analysis import show_api_coverage_report, show_complete_endpoint_list
from .complete_api_implementation import integrate_all_api_functions, show_complete_api_demo

def show_complete_apis_menu():
    """Mostrar menú de APIs completas"""
    options = [
        '📈 Ver cobertura actual',
        '🚀 Activar todas las APIs',
        '🎲 Demo de funciones',
        '📄 Lista de endpoints'
    ]
    
    selected = xbmcgui.Dialog().select('📡 APIs Completas:', options)
    
    if selected == 0:
        show_api_coverage_report()
    elif selected == 1:
        if integrate_all_api_functions():
            xbmcgui.Dialog().notification('APIs', '✅ Todas las APIs activadas (24/24)')
        else:
            xbmcgui.Dialog().notification('APIs', '❌ Error activando APIs')
    elif selected == 2:
        show_complete_api_demo()
    elif selected == 3:
        show_complete_endpoint_list()