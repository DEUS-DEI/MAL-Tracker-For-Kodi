"""
Utilidades regex para scraping sin dependencias
"""

import re

class RegexUtils:
    
    @staticmethod
    def extract_links(html, pattern):
        """Extraer enlaces usando patrón regex"""
        return re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
    
    @staticmethod
    def clean_text(text):
        """Limpiar texto HTML"""
        # Remover tags HTML
        text = re.sub(r'<[^>]+>', '', text)
        # Limpiar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        # Decodificar entidades HTML básicas
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text
    
    @staticmethod
    def extract_json_from_script(html, var_name):
        """Extraer JSON de variable JavaScript"""
        pattern = rf'{var_name}\s*=\s*(\{{[^}}]+\}})'
        match = re.search(pattern, html)
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def find_video_sources(html):
        """Encontrar fuentes de video comunes"""
        patterns = [
            r'file:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'src:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'<source[^>]*src=["\']([^"\']+)["\']',
            r'<iframe[^>]*src=["\']([^"\']*(?:embed|player)[^"\']*)["\']',
            r'video\[\d+\]\s*=\s*["\']([^"\']+)["\']'
        ]
        
        sources = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            sources.extend(matches)
        
        return list(set(sources))  # Remover duplicados
    
    @staticmethod
    def extract_episode_list(html, site='generic'):
        """Extraer lista de episodios según el sitio"""
        if site == 'animeflv':
            pattern = r'<li[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        elif site == 'jkanime':
            pattern = r'<a[^>]*href="([^"]+)"[^>]*>.*?Episodio\s*(\d+)'
        elif site == 'tioanime':
            pattern = r'<a[^>]*href="([^"]*ver/[^"]*)"[^>]*>.*?(\d+)</a>'
        else:
            pattern = r'<a[^>]*href="([^"]+)"[^>]*>.*?(?:episodio|episode|ep).*?(\d+)'
        
        return re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
    
    @staticmethod
    def is_valid_video_url(url):
        """Verificar si URL es de video válida"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.m3u8', '.ts']
        video_domains = ['fembed', 'streamtape', 'mega', 'drive.google']
        
        url_lower = url.lower()
        
        # Verificar extensiones
        for ext in video_extensions:
            if ext in url_lower:
                return True
        
        # Verificar dominios conocidos
        for domain in video_domains:
            if domain in url_lower:
                return True
        
        return False