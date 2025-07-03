"""
Scrapers mejorados basados en Alfa addon
Integración de AnimeFLV y JKanime con técnicas avanzadas
"""

import requests
import re
import json
import xbmc
import xbmcgui
from . import regex_utils

class AlfaScrapers:
    
    # Configuración de hosts
    ANIMEFLV_HOST = "https://www3.animeflv.net/"
    JKANIME_HOST = "https://jkanime.net/"
    
    @staticmethod
    def get_source(url, headers=None):
        """Obtener código fuente con manejo de errores"""
        try:
            if not headers:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Limpiar HTML como en Alfa
            data = response.text
            data = re.sub(r"\\n|\\r|\\t|\\s{2}|-\\s", "", data)
            
            return data
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers: Error getting source - {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def scrape_animeflv_advanced(anime_title):
        """Scraper AnimeFLV mejorado basado en Alfa"""
        try:
            # Búsqueda usando API como en Alfa
            search_url = f"{AlfaScrapers.ANIMEFLV_HOST}api/animes/search"
            post_data = f"value={anime_title.replace(' ', '+')}&limit=100"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(search_url, data=post_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                
                if results:
                    # Tomar primer resultado
                    anime = results[0]
                    anime_id = anime.get("last_id", anime.get("id"))
                    slug = anime.get("slug", "")
                    
                    anime_url = f"{AlfaScrapers.ANIMEFLV_HOST}anime/{anime_id}/{slug}"
                    
                    # Obtener episodios
                    return AlfaScrapers._get_animeflv_episodes(anime_url)
            
            # Fallback a scraping HTML
            return AlfaScrapers._scrape_animeflv_html(anime_title)
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers AnimeFLV: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def _get_animeflv_episodes(anime_url):
        """Extraer episodios de AnimeFLV"""
        try:
            data = AlfaScrapers.get_source(anime_url)
            if not data:
                return None
            
            # Extraer info del anime (método Alfa)
            anime_info = re.search(r'anime_info = \[(.*?)\];', data)
            episodes_data = re.search(r'var episodes = (.*?);', data)
            
            if not anime_info or not episodes_data:
                return None
            
            anime_info = eval(anime_info.group(1))
            episodes = eval(episodes_data.group(1))
            
            episode_list = []
            for episode in episodes:
                episode_num = episode[0]
                episode_url = f"{AlfaScrapers.ANIMEFLV_HOST}ver/{anime_info[2]}-{episode_num}"
                
                episode_list.append({
                    'title': f'Episodio {episode_num}',
                    'url': episode_url,
                    'episode': episode_num
                })
            
            return episode_list[::-1]  # Invertir orden
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers Episodes: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def _scrape_animeflv_html(anime_title):
        """Fallback HTML scraping para AnimeFLV"""
        try:
            search_url = f"{AlfaScrapers.ANIMEFLV_HOST}browse?q={anime_title.replace(' ', '+')}"
            data = AlfaScrapers.get_source(search_url)
            
            if not data:
                return None
            
            # Buscar primer resultado
            anime_pattern = r'<article[^>]*class="[^"]*Anime[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"'
            anime_match = re.search(anime_pattern, data, re.DOTALL)
            
            if anime_match:
                anime_url = AlfaScrapers.ANIMEFLV_HOST + anime_match.group(1).lstrip('/')
                return AlfaScrapers._get_animeflv_episodes(anime_url)
            
            return None
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers HTML: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def scrape_jkanime_advanced(anime_title):
        """Scraper JKanime mejorado basado en Alfa"""
        try:
            search_url = f"{AlfaScrapers.JKANIME_HOST}buscar/{anime_title.replace(' ', '+')}/"
            data = AlfaScrapers.get_source(search_url)
            
            if not data:
                return None
            
            # Buscar primer anime (patrón Alfa)
            anime_pattern = r'class="anime__item">\s+?<a\s+href="(.+?)".+?data-setbg="(.+?)".+?class="title".*?>(.+?)</'
            anime_match = re.search(anime_pattern, data, re.DOTALL)
            
            if not anime_match:
                return None
            
            anime_url = anime_match.group(1)
            
            # Obtener episodios
            return AlfaScrapers._get_jkanime_episodes(anime_url)
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers JKanime: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def _get_jkanime_episodes(anime_url):
        """Extraer episodios de JKanime (método Alfa)"""
        try:
            data = AlfaScrapers.get_source(anime_url)
            if not data:
                return None
            
            # Obtener ID de serie
            serie_id = re.search(r'ajax/pagination_episodes/(\d+)/', data)
            if not serie_id:
                return None
            
            serie_id = serie_id.group(1)
            
            # Obtener número de páginas
            pages_match = re.search(r'href="#pag([0-9]+)".*?>([0-9]+) - ([0-9]+)', data)
            if pages_match:
                total_pages = int(pages_match.group(1))
            else:
                total_pages = 1
            
            episodes = []
            
            # Obtener episodios de todas las páginas
            for page in range(1, total_pages + 1):
                episodes_url = f"{AlfaScrapers.JKANIME_HOST}ajax/pagination_episodes/{serie_id}/{page}/"
                
                headers = {'Referer': anime_url}
                episodes_data = AlfaScrapers.get_source(episodes_url, headers)
                
                if episodes_data:
                    # Extraer episodios JSON
                    episode_matches = re.findall(r'"number":"(\d+)","title":"([^"]+)"', episodes_data)
                    
                    for ep_num, ep_title in episode_matches:
                        episode_url = f"{anime_url}{ep_num}"
                        episodes.append({
                            'title': ep_title.strip(),
                            'url': episode_url,
                            'episode': int(ep_num)
                        })
            
            return sorted(episodes, key=lambda x: x['episode'])
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers JKanime Episodes: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def extract_video_url_advanced(episode_url, site='animeflv'):
        """Extracción avanzada de URLs de video"""
        try:
            data = AlfaScrapers.get_source(episode_url)
            if not data:
                return None
            
            if site == 'animeflv':
                return AlfaScrapers._extract_animeflv_video(data, episode_url)
            elif site == 'jkanime':
                return AlfaScrapers._extract_jkanime_video(data, episode_url)
            
            return None
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers Video Extract: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def _extract_animeflv_video(data, episode_url):
        """Extraer video de AnimeFLV (método Alfa)"""
        try:
            # Buscar variable videos
            videos_match = re.search(r'var videos = (.*?);', data)
            if not videos_match:
                return None
            
            videos_json = json.loads(videos_match.group(1))
            
            # Buscar enlaces de video
            for lang, sources in videos_json.items():
                if isinstance(sources, list):
                    for source in sources:
                        if isinstance(source, dict) and 'code' in source:
                            url = source['code']
                            
                            # Procesar URL según tipo
                            if 'redirector' in url:
                                # Seguir redirección
                                redirect_data = AlfaScrapers.get_source(url)
                                if redirect_data:
                                    redirect_match = re.search(r'window.location.href = "([^"]+)"', redirect_data)
                                    if redirect_match:
                                        url = redirect_match.group(1)
                            
                            elif 'animeflv.net/embed' in url or 'gocdn.html' in url:
                                # Procesar embed
                                check_url = url.replace('embed', 'check').replace('gocdn.html#', 'gocdn.php?v=')
                                try:
                                    response = requests.get(check_url, timeout=10)
                                    if response.status_code == 200:
                                        json_data = response.json()
                                        url = json_data.get('file', url)
                                except:
                                    pass
                            
                            # Limpiar URL
                            url = url.replace('embedsito', 'fembed')
                            
                            if regex_utils.RegexUtils.is_valid_video_url(url):
                                return url
            
            return None
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers AnimeFLV Video: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def _extract_jkanime_video(data, episode_url):
        """Extraer video de JKanime (método Alfa)"""
        try:
            # Buscar iframes
            iframe_matches = re.findall(r"'<iframe.*? src=\"([^\"]+)\"", data)
            
            for iframe_url in iframe_matches:
                if AlfaScrapers.JKANIME_HOST in iframe_url:
                    # Procesar iframe interno
                    iframe_data = AlfaScrapers.get_source(iframe_url, {'Referer': episode_url})
                    if iframe_data:
                        # Buscar URL real
                        url_match = re.search(r"url: '([^']+)',", iframe_data)
                        if not url_match:
                            url_match = re.search(r'src="([^"]+)', iframe_data)
                        
                        if url_match:
                            video_url = url_match.group(1)
                            
                            # Seguir redirecciones si es necesario
                            if AlfaScrapers.JKANIME_HOST in video_url:
                                try:
                                    response = requests.head(video_url, allow_redirects=False, timeout=5)
                                    location = response.headers.get('location')
                                    if location:
                                        video_url = location
                                except:
                                    pass
                            
                            if regex_utils.RegexUtils.is_valid_video_url(video_url):
                                return video_url
                else:
                    # URL externa directa
                    if regex_utils.RegexUtils.is_valid_video_url(iframe_url):
                        return iframe_url
            
            return None
            
        except Exception as e:
            xbmc.log(f'AlfaScrapers JKanime Video: {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def get_available_scrapers():
        """Scrapers avanzados disponibles"""
        return {
            'animeflv_advanced': {
                'name': '🇪🇸 AnimeFLV (Avanzado)',
                'scraper': AlfaScrapers.scrape_animeflv_advanced,
                'extractor': lambda url: AlfaScrapers.extract_video_url_advanced(url, 'animeflv'),
                'supported': True
            },
            'jkanime_advanced': {
                'name': '🇯🇵 JKanime (Avanzado)',
                'scraper': AlfaScrapers.scrape_jkanime_advanced,
                'extractor': lambda url: AlfaScrapers.extract_video_url_advanced(url, 'jkanime'),
                'supported': True
            }
        }