import xbmcgui
import xbmcaddon
import re

def import_config_from_text():
    addon = xbmcaddon.Addon()
    dialog = xbmcgui.Dialog()
    
    text = dialog.input('Pega la configuración:', type=xbmcgui.INPUT_ALPHANUM)
    if not text:
        return False
    
    try:
        # Extraer MAL
        mal_id = re.search(r'MyAnimeList:.*?ClientId\s*([a-f0-9]+)', text, re.DOTALL | re.IGNORECASE)
        mal_secret = re.search(r'ClientSecret\s*([a-f0-9]+)', text, re.DOTALL | re.IGNORECASE)
        
        # Extraer AniList
        ani_id = re.search(r'AniList:.*?ID\s*(\d+)', text, re.DOTALL | re.IGNORECASE)
        ani_secret = re.search(r'Secret\s*([a-zA-Z0-9]+)', text, re.DOTALL | re.IGNORECASE)
        
        # Configurar MAL
        if mal_id and mal_secret:
            addon.setSetting('client_id', mal_id.group(1))
            addon.setSetting('client_secret', mal_secret.group(1))
        
        # Configurar AniList
        if ani_id and ani_secret:
            addon.setSetting('anilist_client_id', ani_id.group(1))
            addon.setSetting('anilist_client_secret', ani_secret.group(1))
        
        dialog.notification('Config Import', 'Configuración importada')
        return True
    except Exception as e:
        dialog.notification('Config Import', f'Error: {str(e)}')
        return False