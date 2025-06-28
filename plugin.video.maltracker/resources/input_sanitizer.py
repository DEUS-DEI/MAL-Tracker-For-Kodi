import re
import html
import xbmc

class InputSanitizer:
    
    @staticmethod
    def sanitize_search_query(query):
        """Sanitizar query de búsqueda"""
        if not isinstance(query, str):
            return ""
        
        # Remover caracteres peligrosos
        query = re.sub(r'[<>"\';()&|`]', '', query)
        
        # Limitar longitud
        query = query[:100]
        
        # Escapar HTML
        query = html.escape(query)
        
        return query.strip()
    
    @staticmethod
    def validate_mal_id(mal_id):
        """Validar ID de MyAnimeList"""
        try:
            mal_id = int(mal_id)
            if mal_id <= 0 or mal_id > 999999:
                return None
            return mal_id
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_score(score):
        """Validar puntuación"""
        try:
            score = int(score)
            if 0 <= score <= 10:
                return score
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_episodes(episodes):
        """Validar número de episodios"""
        try:
            episodes = int(episodes)
            if 0 <= episodes <= 9999:
                return episodes
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitizar nombre de archivo"""
        if not isinstance(filename, str):
            return ""
        
        # Remover caracteres peligrosos para archivos
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Limitar longitud
        filename = filename[:255]
        
        return filename.strip()
    
    @staticmethod
    def validate_url(url):
        """Validar URL"""
        if not isinstance(url, str):
            return False
        
        # Verificar que sea HTTPS para APIs externas
        if url.startswith('http://'):
            xbmc.log(f'Security Warning: Insecure HTTP URL - {url}', xbmc.LOGWARNING)
            return False
        
        # Verificar dominios permitidos
        allowed_domains = [
            'api.myanimelist.net',
            'api.jikan.moe', 
            'kitsu.io',
            'api.trakt.tv',
            'api.themoviedb.org'
        ]
        
        for domain in allowed_domains:
            if domain in url:
                return True
        
        return False