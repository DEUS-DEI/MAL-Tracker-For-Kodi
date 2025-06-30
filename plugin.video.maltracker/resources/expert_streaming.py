"""
Sistema de streaming experto - Sitios alternativos
SOLO para usuarios expertos - Configuración oculta
"""

import xbmcgui
import xbmcaddon
import xbmc
import webbrowser
import urllib.parse

class ExpertStreaming:
    
    # Sitios de streaming alternativos
    STREAMING_SITES = {
        'animeflv': {
            'name': 'AnimeFLV',
            'url': 'https://www3.animeflv.net',
            'search': '/browse?q={}',
            'icon': '🇪🇸'
        },
        'animejl': {
            'name': 'AnimeJL', 
            'url': 'https://animejl.com',
            'search': '/search?q={}',
            'icon': '🇲🇽'
        },
        'hacktorrent': {
            'name': 'Hacktorrent',
            'url': 'https://hacktorrent.com',
            'search': '/search?q={}',
            'icon': '🏴‍☠️'
        },
        'henaojara': {
            'name': 'HenaoJara',
            'url': 'https://henaojara.com',
            'search': '/search?q={}',
            'icon': '🎬'
        },
        'jkanime': {
            'name': 'JKanime',
            'url': 'https://jkanime.net',
            'search': '/buscar/{}/',
            'icon': '🇯🇵'
        },
        'latanime': {
            'name': 'Latanime',
            'url': 'https://latanime.org',
            'search': '/search?q={}',
            'icon': '🌎'
        },
        'mundodonghua': {
            'name': 'Mundo Donghua',
            'url': 'https://mundodonghua.com',
            'search': '/search?q={}',
            'icon': '🇨🇳'
        },
        'pelispanda': {
            'name': 'Pelispanda',
            'url': 'https://pelispanda.com',
            'search': '/search?s={}',
            'icon': '🐼'
        },
        'pelisplus': {
            'name': 'PelisPlus',
            'url': 'https://pelisplus.lat',
            'search': '/search?s={}',
            'icon': '➕'
        },
        'playdede': {
            'name': 'Playdede',
            'url': 'https://playdede.nu',
            'search': '/search?q={}',
            'icon': '▶️'
        },
        'sololatino': {
            'name': 'SoloLatino',
            'url': 'https://sololatino.net',
            'search': '/search?q={}',
            'icon': '🇱🇦'
        },
        'tioanime': {
            'name': 'Tio Anime',
            'url': 'https://tioanime.com',
            'search': '/directorio?q={}',
            'icon': '👨'
        },
        'tiodonghua': {
            'name': 'TioDonghua',
            'url': 'https://tiodonghua.com',
            'search': '/search?q={}',
            'icon': '🧓'
        },
        'veranime': {
            'name': 'VerAnime',
            'url': 'https://veranime.net',
            'search': '/search?q={}',
            'icon': '👁️'
        },
        'veranimeassistant': {
            'name': 'VerAnime Assistant',
            'url': 'https://veranime.org',
            'search': '/search?q={}',
            'icon': '🤖'
        },
        'veronline': {
            'name': 'Veronline',
            'url': 'https://veronline.net',
            'search': '/search?q={}',
            'icon': '🌐'
        },
        'yaske': {
            'name': 'Yaske',
            'url': 'https://yaske.to',
            'search': '/search?q={}',
            'icon': '🔍'
        }
    }
    
    @staticmethod
    def is_expert_mode_enabled():
        """Verificar si el modo experto está activado"""
        try:
            addon = xbmcaddon.Addon()
            return addon.getSetting('expert_streaming') == 'true'
        except:
            return False
    
    @staticmethod
    def show_expert_streaming_menu():
        """Mostrar menú de streaming experto"""
        if not ExpertStreaming.is_expert_mode_enabled():
            xbmcgui.Dialog().ok('Acceso Denegado', 
                'Esta función requiere activar:\n\n'
                'Configuración → Experto → Streaming Alternativo\n\n'
                '⚠️ ADVERTENCIA: Solo para usuarios expertos')
            return
        
        options = [
            '🔍 Buscar en sitios alternativos',
            '📋 Ver todos los sitios disponibles', 
            '⚙️ Configurar sitios favoritos',
            '❓ Información y advertencias'
        ]
        
        selected = xbmcgui.Dialog().select('🔓 Streaming Experto:', options)
        
        if selected == 0:
            ExpertStreaming.search_alternative_sites()
        elif selected == 1:
            ExpertStreaming.show_available_sites()
        elif selected == 2:
            ExpertStreaming.configure_favorite_sites()
        elif selected == 3:
            ExpertStreaming.show_expert_info()
    
    @staticmethod
    def search_alternative_sites():
        """Buscar anime en sitios alternativos"""
        query = xbmcgui.Dialog().input('Buscar anime:')
        if not query:
            return
        
        # Seleccionar sitios
        site_names = [f"{site['icon']} {site['name']}" for site in ExpertStreaming.STREAMING_SITES.values()]
        site_names.append('🌍 Buscar en todos')
        
        selected = xbmcgui.Dialog().select('Seleccionar sitio:', site_names)
        if selected == -1:
            return
        
        if selected == len(site_names) - 1:  # Todos los sitios
            ExpertStreaming.search_all_sites(query)
        else:
            site_key = list(ExpertStreaming.STREAMING_SITES.keys())[selected]
            ExpertStreaming.open_site_search(site_key, query)
    
    @staticmethod
    def search_all_sites(query):
        """Abrir búsqueda en múltiples sitios"""
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno('Búsqueda Masiva',
            f'Se abrirán {len(ExpertStreaming.STREAMING_SITES)} sitios\n'
            f'buscando: "{query}"\n\n'
            '⚠️ Esto puede abrir muchas pestañas\n'
            '¿Continuar?'):
            
            opened = 0
            for site_key in ExpertStreaming.STREAMING_SITES.keys():
                try:
                    ExpertStreaming.open_site_search(site_key, query, silent=True)
                    opened += 1
                except:
                    pass
            
            dialog.notification('Búsqueda Masiva', f'{opened} sitios abiertos')
    
    @staticmethod
    def open_site_search(site_key, query, silent=False):
        """Abrir búsqueda en sitio específico"""
        site = ExpertStreaming.STREAMING_SITES.get(site_key)
        if not site:
            return
        
        search_url = site['url'] + site['search'].format(urllib.parse.quote(query))
        
        try:
            webbrowser.open(search_url)
            if not silent:
                xbmcgui.Dialog().notification('Sitio Abierto', f"{site['icon']} {site['name']}")
        except Exception as e:
            if not silent:
                xbmcgui.Dialog().notification('Error', f'No se pudo abrir {site["name"]}')
    
    @staticmethod
    def show_available_sites():
        """Mostrar todos los sitios disponibles"""
        sites_info = "🔓 SITIOS DE STREAMING ALTERNATIVOS:\n\n"
        
        for site in ExpertStreaming.STREAMING_SITES.values():
            sites_info += f"{site['icon']} {site['name']}\n"
            sites_info += f"   {site['url']}\n\n"
        
        sites_info += "⚠️ ADVERTENCIA:\n"
        sites_info += "• Usa bajo tu propia responsabilidad\n"
        sites_info += "• Verifica la legalidad en tu país\n"
        sites_info += "• Usa VPN si es necesario\n"
        sites_info += "• Ten cuidado con anuncios/malware"
        
        xbmcgui.Dialog().textviewer('Sitios Alternativos', sites_info)
    
    @staticmethod
    def configure_favorite_sites():
        """Configurar sitios favoritos"""
        dialog = xbmcgui.Dialog()
        
        # Selección múltiple de sitios favoritos
        site_names = [f"{site['icon']} {site['name']}" for site in ExpertStreaming.STREAMING_SITES.values()]
        
        selected = dialog.multiselect('Seleccionar favoritos:', site_names)
        if not selected:
            return
        
        favorites = [list(ExpertStreaming.STREAMING_SITES.keys())[i] for i in selected]
        
        # Guardar favoritos (simplificado)
        try:
            addon = xbmcaddon.Addon()
            addon.setSetting('expert_favorites', ','.join(favorites))
            dialog.notification('Favoritos', f'{len(favorites)} sitios guardados')
        except:
            dialog.notification('Error', 'No se pudieron guardar favoritos')
    
    @staticmethod
    def show_expert_info():
        """Mostrar información y advertencias"""
        info = """🔓 STREAMING EXPERTO - INFORMACIÓN

⚠️ ADVERTENCIAS IMPORTANTES:
• Esta función es SOLO para usuarios expertos
• Los sitios pueden no ser legales en tu país
• Usa bajo tu propia responsabilidad
• Verifica las leyes locales antes de usar
• Recomendamos usar VPN para privacidad

🛡️ SEGURIDAD:
• Ten cuidado con anuncios maliciosos
• No descargues archivos sospechosos
• Usa bloqueador de anuncios
• Mantén antivirus actualizado

🌍 SITIOS INCLUIDOS:
• 16 sitios de anime/películas en español
• Principalmente contenido latino/español
• Alternativa a Alfa y Balandro
• Búsqueda directa desde Kodi

🔧 CONFIGURACIÓN:
• Activar en: Configuración → Experto
• Nivel de configuración: Experto (2)
• Función oculta por defecto

📝 RESPONSABILIDAD:
El desarrollador NO se hace responsable
del uso de estos sitios. Úsalos bajo
tu propia responsabilidad y riesgo."""
        
        xbmcgui.Dialog().textviewer('Información Experto', info)
    
    @staticmethod
    def get_expert_watch_options(anime_title):
        """Obtener opciones de visualización expertas"""
        if not ExpertStreaming.is_expert_mode_enabled():
            return []
        
        options = []
        
        # Agregar sitios favoritos primero
        try:
            addon = xbmcaddon.Addon()
            favorites = addon.getSetting('expert_favorites').split(',')
            
            for site_key in favorites:
                if site_key in ExpertStreaming.STREAMING_SITES:
                    site = ExpertStreaming.STREAMING_SITES[site_key]
                    options.append({
                        'title': f"🔓 {site['icon']} {site['name']}",
                        'action': 'expert_search',
                        'site': site_key,
                        'query': anime_title
                    })
        except:
            pass
        
        # Opción de búsqueda en todos
        options.append({
            'title': '🔓 🌍 Buscar en sitios alternativos',
            'action': 'expert_search_all',
            'query': anime_title
        })
        
        return options