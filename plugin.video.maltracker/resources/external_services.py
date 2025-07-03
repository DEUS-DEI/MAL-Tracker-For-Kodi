import requests
import json
import xbmc
import xbmcgui
from .config import USER_AGENT, rate_limit

class ExternalServices:
    
    @staticmethod
    def search_kitsu(anime_title):
        """Buscar en Kitsu API"""
        try:
            rate_limit()
            url = f"https://kitsu.io/api/edge/anime"
            params = {'filter[text]': anime_title, 'page[limit]': 5}
            headers = {'Accept': 'application/vnd.api+json', 'User-Agent': USER_AGENT}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            xbmc.log(f'External Services: Kitsu search error - {str(e)}', xbmc.LOGERROR)
        return None
    
    @staticmethod
    def get_anidb_info(anime_title):
        """Obtener información de AniDB"""
        try:
            # AniDB requiere autenticación, usar búsqueda básica
            rate_limit()
            # Placeholder para implementación real
            return {'status': 'not_implemented'}
            
        except Exception as e:
            xbmc.log(f'External Services: AniDB error - {str(e)}', xbmc.LOGERROR)
        return None
    
    @staticmethod
    def search_trakt(anime_title):
        """Buscar en Trakt.tv"""
        try:
            rate_limit()
            url = f"https://api.trakt.tv/search/show"
            params = {'query': anime_title, 'limit': 5}
            headers = {
                'Content-Type': 'application/json',
                'trakt-api-version': '2',
                'trakt-api-key': 'your_trakt_key',  # Requiere API key
                'User-Agent': USER_AGENT
            }
            
            # Placeholder - requiere configuración de API key
            return {'status': 'requires_api_key'}
            
        except Exception as e:
            xbmc.log(f'External Services: Trakt search error - {str(e)}', xbmc.LOGERROR)
        return None
    
    @staticmethod
    def get_tmdb_info(anime_title):
        """Obtener información de TMDB"""
        try:
            rate_limit()
            # TMDB tiene algunos anime, especialmente películas
            url = f"https://api.themoviedb.org/3/search/tv"
            params = {
                'api_key': 'your_tmdb_key',  # Requiere API key
                'query': anime_title,
                'language': 'es-ES'
            }
            
            # Placeholder - requiere configuración de API key
            return {'status': 'requires_api_key'}
            
        except Exception as e:
            xbmc.log(f'External Services: TMDB error - {str(e)}', xbmc.LOGERROR)
        return None
    
    @staticmethod
    def cross_reference_anime(anime_title):
        """Referencias cruzadas entre servicios"""
        results = {
            'mal': {'title': anime_title, 'source': 'local'},
            'kitsu': ExternalServices.search_kitsu(anime_title),
            'anidb': ExternalServices.get_anidb_info(anime_title),
            'trakt': ExternalServices.search_trakt(anime_title),
            'tmdb': ExternalServices.get_tmdb_info(anime_title)
        }
        
        return results
    
    @staticmethod
    def show_cross_reference_info(anime_title):
        """Mostrar información de referencias cruzadas"""
        results = ExternalServices.cross_reference_anime(anime_title)
        
        info = f"🔗 REFERENCIAS CRUZADAS - {anime_title}\n\n"
        
        for service, data in results.items():
            service_names = {
                'mal': 'MyAnimeList',
                'kitsu': 'Kitsu',
                'anidb': 'AniDB', 
                'trakt': 'Trakt.tv',
                'tmdb': 'TMDB'
            }
            
            service_name = service_names.get(service, service)
            
            if data and data.get('status') != 'not_implemented':
                if service == 'kitsu' and data.get('data'):
                    kitsu_title = data['data'][0]['attributes']['canonicalTitle']
                    info += f"✅ {service_name}: {kitsu_title}\n"
                else:
                    info += f"✅ {service_name}: Encontrado\n"
            else:
                info += f"❌ {service_name}: No disponible\n"
        
        xbmcgui.Dialog().textviewer('Referencias Cruzadas', info)

def setup_external_apis():
    """Configurar APIs externas"""
    options = [
        'Configurar Trakt.tv API',
        'Configurar TMDB API', 
        'Configurar AniDB',
        'Probar conexiones',
        'Ver estado de APIs'
    ]
    
    selected = xbmcgui.Dialog().select('APIs Externas:', options)
    
    if selected == 0:
        setup_trakt_api()
    elif selected == 1:
        setup_tmdb_api()
    elif selected == 2:
        setup_anidb()
    elif selected == 3:
        test_api_connections()
    elif selected == 4:
        show_api_status()

def setup_trakt_api():
    """Configurar Trakt.tv API"""
    info = "CONFIGURAR TRAKT.TV:\n\n"
    info += "1. Visita https://trakt.tv/oauth/applications\n"
    info += "2. Crea una nueva aplicación\n"
    info += "3. Copia el Client ID\n"
    info += "4. Pégalo en el siguiente campo"
    
    xbmcgui.Dialog().textviewer('Configurar Trakt', info)
    
    client_id = xbmcgui.Dialog().input('Trakt Client ID:')
    if client_id:
        # Guardar configuración
        save_api_config('trakt', {'client_id': client_id})
        xbmcgui.Dialog().notification('APIs Externas', 'Trakt configurado')

def setup_tmdb_api():
    """Configurar TMDB API"""
    info = "CONFIGURAR TMDB:\n\n"
    info += "1. Visita https://www.themoviedb.org/settings/api\n"
    info += "2. Solicita una API key\n"
    info += "3. Copia la API key\n"
    info += "4. Pégala en el siguiente campo"
    
    xbmcgui.Dialog().textviewer('Configurar TMDB', info)
    
    api_key = xbmcgui.Dialog().input('TMDB API Key:')
    if api_key:
        save_api_config('tmdb', {'api_key': api_key})
        xbmcgui.Dialog().notification('APIs Externas', 'TMDB configurado')

def save_api_config(service, config):
    """Guardar configuración de API"""
    try:
        from .config import TOKEN_PATH
        import os
        
        config_file = os.path.join(TOKEN_PATH, 'external_apis.json')
        
        # Cargar configuración existente
        existing_config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        
        # Actualizar configuración
        existing_config[service] = config
        
        # Guardar
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2)
            
    except Exception as e:
        xbmc.log(f'External Services: Save config error - {str(e)}', xbmc.LOGERROR)

def load_api_config():
    """Cargar configuración de APIs"""
    try:
        from .config import TOKEN_PATH
        import os
        
        config_file = os.path.join(TOKEN_PATH, 'external_apis.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    except Exception as e:
        xbmc.log(f'External Services: Load config error - {str(e)}', xbmc.LOGERROR)
    
    return {}

def test_api_connections():
    """Probar conexiones a APIs"""
    config = load_api_config()
    
    results = []
    
    # Probar Kitsu (no requiere API key)
    kitsu_result = ExternalServices.search_kitsu("Naruto")
    results.append(('Kitsu', '✅ Conectado' if kitsu_result else '❌ Error'))
    
    # Probar otras APIs si están configuradas
    if 'trakt' in config:
        results.append(('Trakt.tv', '⚙️ Configurado'))
    else:
        results.append(('Trakt.tv', '❌ No configurado'))
    
    if 'tmdb' in config:
        results.append(('TMDB', '⚙️ Configurado'))
    else:
        results.append(('TMDB', '❌ No configurado'))
    
    # Mostrar resultados
    info = "🔗 ESTADO DE CONEXIONES:\n\n"
    for service, status in results:
        info += f"{service}: {status}\n"
    
    xbmcgui.Dialog().textviewer('Test de Conexiones', info)

def show_api_status():
    """Mostrar estado de APIs externas"""
    config = load_api_config()
    
    info = "🌐 ESTADO DE APIs EXTERNAS:\n\n"
    
    services = {
        'Kitsu': 'Gratis - Información de anime',
        'Trakt.tv': 'Gratis - Tracking y estadísticas',
        'TMDB': 'Gratis - Metadatos y imágenes',
        'AniDB': 'Gratis - Base de datos completa'
    }
    
    for service, description in services.items():
        service_key = service.lower().replace('.', '').replace(' ', '')
        configured = '✅' if service_key in config else '❌'
        info += f"{configured} {service}\n   {description}\n\n"
    
    xbmcgui.Dialog().textviewer('Estado de APIs', info)