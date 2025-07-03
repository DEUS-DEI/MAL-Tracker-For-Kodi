"""
Scraper simple sin dependencias externas
Solo usando regex y requests (incluido en Kodi)
"""

import requests
import re
import json
import xbmc
import xbmcgui

class SimpleScraper:
    
    @staticmethod
    def scrape_animeflv(anime_title):
        """Scraper AnimeFLV usando solo regex"""
        try:
            # Buscar anime
            search_url = f"https://www3.animeflv.net/browse?q={anime_title}"
            response = requests.get(search_url, timeout=10)
            html = response.text
            
            # Extraer primer resultado con regex
            anime_pattern = r'<article[^>]*class="[^"]*Anime[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>'
            anime_match = re.search(anime_pattern, html, re.DOTALL)
            
            if not anime_match:
                return None
            
            anime_url = "https://www3.animeflv.net" + anime_match.group(1)
            
            # Obtener página del anime
            response = requests.get(anime_url, timeout=10)
            html = response.text
            
            # Extraer episodios con regex
            episodes = []
            episode_pattern = r'<li[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            episode_matches = re.findall(episode_pattern, html)
            
            for ep_url, ep_title in episode_matches:
                if '/ver/' in ep_url:  # Solo episodios
                    episodes.append({
                        'title': ep_title.strip(),
                        'url': "https://www3.animeflv.net" + ep_url
                    })
            
            return episodes[::-1]  # Invertir orden
            
        except Exception as e:
            xbmc.log(f'SimpleScraper AnimeFLV Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def scrape_jkanime(anime_title):
        """Scraper JKanime usando solo regex"""
        try:
            search_url = f"https://jkanime.net/buscar/{anime_title}/"
            response = requests.get(search_url, timeout=10)
            html = response.text
            
            # Extraer primer anime
            anime_pattern = r'<div[^>]*class="[^"]*anime__item[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"'
            anime_match = re.search(anime_pattern, html, re.DOTALL)
            
            if not anime_match:
                return None
            
            anime_url = anime_match.group(1)
            
            # Obtener episodios
            response = requests.get(anime_url, timeout=10)
            html = response.text
            
            episodes = []
            episode_pattern = r'<a[^>]*href="([^"]+)"[^>]*>.*?Episodio\s*(\d+)'
            episode_matches = re.findall(episode_pattern, html)
            
            for ep_url, ep_num in episode_matches:
                episodes.append({
                    'title': f'Episodio {ep_num}',
                    'url': ep_url if ep_url.startswith('http') else f'https://jkanime.net{ep_url}'
                })
            
            return episodes
            
        except Exception as e:
            xbmc.log(f'SimpleScraper JKanime Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def extract_video_url(episode_url, site='animeflv'):
        """Extraer URL de video usando regex"""
        try:
            response = requests.get(episode_url, timeout=10)
            html = response.text
            
            if site == 'animeflv':
                # Buscar enlaces de video
                video_patterns = [
                    r'video\[1\]\s*=\s*["\']([^"\']+)["\']',
                    r'<iframe[^>]*src=["\']([^"\']*(?:fembed|streamtape|mega)[^"\']*)["\']',
                    r'file:\s*["\']([^"\']+\.mp4[^"\']*)["\']'
                ]
                
                for pattern in video_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        return match.group(1)
            
            elif site == 'jkanime':
                # Buscar iframe o video directo
                iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\']'
                match = re.search(iframe_pattern, html)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            xbmc.log(f'SimpleScraper Extract Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def scrape_tioanime(anime_title):
        """Scraper TioAnime usando regex"""
        try:
            search_url = f"https://tioanime.com/directorio?q={anime_title}"
            response = requests.get(search_url, timeout=10)
            html = response.text
            
            # Extraer primer resultado
            anime_pattern = r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>'
            anime_match = re.search(anime_pattern, html, re.DOTALL)
            
            if not anime_match:
                return None
            
            anime_url = "https://tioanime.com" + anime_match.group(1)
            
            # Obtener episodios
            response = requests.get(anime_url, timeout=10)
            html = response.text
            
            episodes = []
            episode_pattern = r'<a[^>]*href="([^"]*ver/[^"]*)"[^>]*>.*?(\d+)</a>'
            episode_matches = re.findall(episode_pattern, html)
            
            for ep_url, ep_num in episode_matches:
                episodes.append({
                    'title': f'Episodio {ep_num}',
                    'url': f"https://tioanime.com{ep_url}"
                })
            
            return episodes
            
        except Exception as e:
            xbmc.log(f'SimpleScraper TioAnime Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def show_episodes_menu(anime_title, site='animeflv'):
        """Mostrar menú de episodios con auto-reproducción"""
        scrapers = {
            'animeflv': SimpleScraper.scrape_animeflv,
            'jkanime': SimpleScraper.scrape_jkanime,
            'tioanime': SimpleScraper.scrape_tioanime
        }
        
        scraper_func = scrapers.get(site)
        if not scraper_func:
            xbmcgui.Dialog().notification('Error', f'Scraper {site} no disponible')
            return
        
        episodes = scraper_func(anime_title)
        
        if not episodes:
            xbmcgui.Dialog().notification('Scraper', 'No se encontraron episodios')
            return
        
        # Opciones de reproducción
        options = [
            '▶️ Reproducir desde episodio...',
            '🔄 Reproducir todo (auto-siguiente)',
            '⚙️ Configurar auto-reproducción'
        ]
        
        mode = xbmcgui.Dialog().select(f'{anime_title} - Opciones:', options)
        
        if mode == 0:  # Episodio específico
            episode_titles = [ep['title'] for ep in episodes]
            selected = xbmcgui.Dialog().select(f'Episodios - {anime_title}:', episode_titles)
            
            if selected != -1:
                SimpleScraper.start_auto_playback(episodes, anime_title, site, selected)
                
        elif mode == 1:  # Reproducir todo
            SimpleScraper.start_auto_playback(episodes, anime_title, site, 0)
            
        elif mode == 2:  # Configuración
            SimpleScraper.show_playback_settings()
    
    @staticmethod
    def start_auto_playback(episodes, anime_title, site, start_index=0):
        """Iniciar reproducción automática"""
        from . import auto_player
        
        # Configurar reproductor
        auto_player.auto_player.set_playlist(episodes, anime_title, site, start_index)
        
        # Iniciar reproducción
        if auto_player.auto_player.play_current_episode():
            xbmcgui.Dialog().notification('Auto-Player', f'Iniciando {anime_title}')
        else:
            xbmcgui.Dialog().notification('Error', 'No se pudo iniciar reproducción')
    
    @staticmethod
    def show_playback_settings():
        """Mostrar configuración de reproducción"""
        from . import auto_player
        
        player_info = auto_player.auto_player.get_playback_info()
        
        if player_info:
            info = f"REPRODUCCIÓN ACTUAL:\n\n"
            info += f"Anime: {player_info['anime']}\n"
            info += f"Episodio: {player_info['current_episode']}\n"
            info += f"Progreso: {player_info['progress']}\n"
            info += f"Auto-siguiente: {'Sí' if player_info['auto_next'] else 'No'}\n"
            info += f"Episodios restantes: {player_info['remaining']}"
        else:
            info = "No hay reproducción activa"
        
        options = [
            '🔄 Alternar auto-reproducción',
            '📋 Ver lista de episodios',
            '⏹️ Detener reproducción'
        ]
        
        xbmcgui.Dialog().textviewer('Estado del Reproductor', info)
        
        selected = xbmcgui.Dialog().select('Opciones:', options)
        
        if selected == 0:  # Toggle auto
            auto_player.auto_player.toggle_auto_next()
        elif selected == 1:  # Lista episodios
            auto_player.auto_player.show_episode_menu()
        elif selected == 2:  # Detener
            auto_player.auto_player.stop()
    
    @staticmethod
    def play_episode(episode_url, site):
        """Reproducir episodio en Kodi"""
        video_url = SimpleScraper.extract_video_url(episode_url, site)
        
        if video_url:
            # Reproducir en Kodi
            import xbmc
            xbmc.Player().play(video_url)
            xbmcgui.Dialog().notification('Reproduciendo', 'Episodio iniciado')
        else:
            # Fallback: abrir en navegador
            import webbrowser
            try:
                webbrowser.open(episode_url)
                xbmcgui.Dialog().notification('Navegador', 'Episodio abierto en navegador')
            except:
                xbmcgui.Dialog().notification('Error', 'No se pudo reproducir ni abrir')
    
    @staticmethod
    def get_available_scrapers():
        """Scrapers disponibles sin dependencias"""
        return {
            'animeflv': {
                'name': '🇪🇸 AnimeFLV',
                'scraper': SimpleScraper.scrape_animeflv,
                'supported': True
            },
            'jkanime': {
                'name': '🇯🇵 JKanime',
                'scraper': SimpleScraper.scrape_jkanime,
                'supported': True
            },
            'tioanime': {
                'name': '👨 Tio Anime',
                'scraper': SimpleScraper.scrape_tioanime,
                'supported': True
            }
        }