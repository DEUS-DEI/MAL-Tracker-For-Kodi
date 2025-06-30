"""
Scrapers de video para sitios de streaming
Extrae enlaces directos para reproducir en Kodi
"""

import requests
import re
import json
import base64
import xbmc
import xbmcgui

try:
    from bs4 import BeautifulSoup
    SCRAPING_ENABLED = True
except ImportError:
    BeautifulSoup = None
    SCRAPING_ENABLED = False

class VideoScrapers:
    
    @staticmethod
    def scrape_animeflv(anime_title):
        """Scraper para AnimeFLV"""
        if not SCRAPING_ENABLED:
            xbmcgui.Dialog().notification('Scraper', 'BeautifulSoup no disponible')
            return None
            
        try:
            # Buscar anime
            search_url = f"https://www3.animeflv.net/browse?q={anime_title}"
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar primer resultado
            anime_link = soup.find('article', class_='Anime alt B')
            if not anime_link:
                return None
            
            anime_url = "https://www3.animeflv.net" + anime_link.find('a')['href']
            
            # Obtener lista de episodios
            response = requests.get(anime_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            episodes = []
            episode_list = soup.find('ul', class_='ListCaps')
            if episode_list:
                for ep in episode_list.find_all('li'):
                    ep_link = ep.find('a')
                    if ep_link:
                        episodes.append({
                            'title': ep_link.text.strip(),
                            'url': "https://www3.animeflv.net" + ep_link['href']
                        })
            
            return episodes
            
        except Exception as e:
            xbmc.log(f'AnimeFLV Scraper Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def scrape_jkanime(anime_title):
        """Scraper para JKanime"""
        if not SCRAPING_ENABLED:
            xbmcgui.Dialog().notification('Scraper', 'BeautifulSoup no disponible')
            return None
            
        try:
            search_url = f"https://jkanime.net/buscar/{anime_title}/"
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar primer anime
            anime_link = soup.find('div', class_='anime__item')
            if not anime_link:
                return None
            
            anime_url = anime_link.find('a')['href']
            
            # Obtener episodios
            response = requests.get(anime_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            episodes = []
            episode_list = soup.find('div', class_='anime__episodes')
            if episode_list:
                for ep in episode_list.find_all('a'):
                    episodes.append({
                        'title': ep.text.strip(),
                        'url': ep['href']
                    })
            
            return episodes
            
        except Exception as e:
            xbmc.log(f'JKanime Scraper Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def extract_video_url(episode_url, site='animeflv'):
        """Extraer URL de video directo"""
        if not SCRAPING_ENABLED:
            return None
            
        try:
            response = requests.get(episode_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if site == 'animeflv':
                # Buscar script con enlaces
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'video[1]' in script.string:
                        # Extraer URL del script
                        match = re.search(r'video\[1\]\s*=\s*["\']([^"\']+)["\']', script.string)
                        if match:
                            return match.group(1)
            
            elif site == 'jkanime':
                # Buscar iframe o video
                iframe = soup.find('iframe')
                if iframe and iframe.get('src'):
                    return iframe['src']
            
            return None
            
        except Exception as e:
            xbmc.log(f'Video Extract Error: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def show_episodes_menu(anime_title, site='animeflv'):
        """Mostrar menú de episodios"""
        if site == 'animeflv':
            episodes = VideoScrapers.scrape_animeflv(anime_title)
        elif site == 'jkanime':
            episodes = VideoScrapers.scrape_jkanime(anime_title)
        else:
            episodes = None
        
        if not episodes:
            xbmcgui.Dialog().notification('Scraper', 'No se encontraron episodios')
            return
        
        # Mostrar lista de episodios
        episode_titles = [ep['title'] for ep in episodes]
        selected = xbmcgui.Dialog().select(f'Episodios - {anime_title}:', episode_titles)
        
        if selected != -1:
            episode = episodes[selected]
            VideoScrapers.play_episode(episode['url'], site)
    
    @staticmethod
    def play_episode(episode_url, site):
        """Reproducir episodio en Kodi"""
        video_url = VideoScrapers.extract_video_url(episode_url, site)
        
        if video_url:
            # Reproducir en Kodi
            import xbmc
            xbmc.Player().play(video_url)
            xbmcgui.Dialog().notification('Reproduciendo', 'Episodio iniciado')
        else:
            xbmcgui.Dialog().notification('Error', 'No se pudo extraer video')
    
    @staticmethod
    def get_available_scrapers():
        """Obtener scrapers disponibles"""
        return {
            'animeflv': {
                'name': '🇪🇸 AnimeFLV',
                'scraper': VideoScrapers.scrape_animeflv,
                'supported': SCRAPING_ENABLED
            },
            'jkanime': {
                'name': '🇯🇵 JKanime', 
                'scraper': VideoScrapers.scrape_jkanime,
                'supported': SCRAPING_ENABLED
            },
            'tioanime': {
                'name': '👨 Tio Anime',
                'scraper': None,
                'supported': False  # Requiere implementación
            }
        }