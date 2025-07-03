import requests
import xbmc
import time

class JikanAPI:
    BASE_URL = "https://api.jikan.moe/v4"
    
    @staticmethod
    def _request(endpoint, params=None):
        """Hacer petición a Jikan API con rate limiting"""
        try:
            time.sleep(0.5)  # Rate limit: 2 requests per second
            url = f"{JikanAPI.BASE_URL}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                xbmc.log(f'Jikan API Error: {response.status_code}', xbmc.LOGERROR)
                return None
        except Exception as e:
            xbmc.log(f'Jikan API Exception: {str(e)}', xbmc.LOGERROR)
            return None
    
    # ANIME ENDPOINTS
    @staticmethod
    def search_anime(query, limit=25):
        """Buscar anime"""
        return JikanAPI._request("anime", {"q": query, "limit": limit})
    
    @staticmethod
    def get_anime_by_id(anime_id):
        """Obtener anime por ID"""
        return JikanAPI._request(f"anime/{anime_id}")
    
    @staticmethod
    def get_anime_full(anime_id):
        """Obtener anime completo con toda la información"""
        return JikanAPI._request(f"anime/{anime_id}/full")
    
    @staticmethod
    def get_anime_characters(anime_id):
        """Obtener personajes del anime"""
        return JikanAPI._request(f"anime/{anime_id}/characters")
    
    @staticmethod
    def get_anime_staff(anime_id):
        """Obtener staff del anime"""
        return JikanAPI._request(f"anime/{anime_id}/staff")
    
    @staticmethod
    def get_anime_episodes(anime_id, page=1):
        """Obtener episodios del anime"""
        return JikanAPI._request(f"anime/{anime_id}/episodes", {"page": page})
    
    @staticmethod
    def get_anime_news(anime_id):
        """Obtener noticias del anime"""
        return JikanAPI._request(f"anime/{anime_id}/news")
    
    @staticmethod
    def get_anime_reviews(anime_id):
        """Obtener reviews del anime"""
        return JikanAPI._request(f"anime/{anime_id}/reviews")
    
    @staticmethod
    def get_anime_recommendations(anime_id):
        """Obtener recomendaciones del anime"""
        return JikanAPI._request(f"anime/{anime_id}/recommendations")
    
    @staticmethod
    def get_anime_statistics(anime_id):
        """Obtener estadísticas del anime"""
        return JikanAPI._request(f"anime/{anime_id}/statistics")
    
    # TOP ANIME
    @staticmethod
    def get_top_anime(type="all", filter="all", page=1):
        """Obtener top anime"""
        params = {"type": type, "filter": filter, "page": page}
        return JikanAPI._request("top/anime", params)
    
    # SEASONAL ANIME
    @staticmethod
    def get_current_season():
        """Obtener anime de temporada actual"""
        return JikanAPI._request("seasons/now")
    
    @staticmethod
    def get_season(year, season):
        """Obtener anime de temporada específica"""
        return JikanAPI._request(f"seasons/{year}/{season}")
    
    @staticmethod
    def get_upcoming_season():
        """Obtener próxima temporada"""
        return JikanAPI._request("seasons/upcoming")
    
    # SCHEDULES
    @staticmethod
    def get_schedules(day=None):
        """Obtener horarios de anime"""
        if day:
            return JikanAPI._request(f"schedules/{day}")
        return JikanAPI._request("schedules")
    
    # GENRES
    @staticmethod
    def get_anime_genres():
        """Obtener géneros de anime"""
        return JikanAPI._request("genres/anime")
    
    # PRODUCERS/STUDIOS
    @staticmethod
    def get_producers():
        """Obtener productores"""
        return JikanAPI._request("producers")
    
    # RANDOM
    @staticmethod
    def get_random_anime():
        """Obtener anime aleatorio"""
        return JikanAPI._request("random/anime")
    
    # MANGA ENDPOINTS
    @staticmethod
    def search_manga(query, limit=25):
        """Buscar manga"""
        return JikanAPI._request("manga", {"q": query, "limit": limit})
    
    @staticmethod
    def get_manga_by_id(manga_id):
        """Obtener manga por ID"""
        return JikanAPI._request(f"manga/{manga_id}")
    
    @staticmethod
    def get_top_manga(type="all", filter="all", page=1):
        """Obtener top manga"""
        params = {"type": type, "filter": filter, "page": page}
        return JikanAPI._request("top/manga", params)
    
    # CHARACTERS
    @staticmethod
    def search_characters(query, limit=25):
        """Buscar personajes"""
        return JikanAPI._request("characters", {"q": query, "limit": limit})
    
    @staticmethod
    def get_character_by_id(character_id):
        """Obtener personaje por ID"""
        return JikanAPI._request(f"characters/{character_id}")
    
    @staticmethod
    def get_top_characters(page=1):
        """Obtener top personajes"""
        return JikanAPI._request("top/characters", {"page": page})
    
    # PEOPLE
    @staticmethod
    def search_people(query, limit=25):
        """Buscar personas"""
        return JikanAPI._request("people", {"q": query, "limit": limit})
    
    @staticmethod
    def get_person_by_id(person_id):
        """Obtener persona por ID"""
        return JikanAPI._request(f"people/{person_id}")
    
    @staticmethod
    def get_top_people(page=1):
        """Obtener top personas"""
        return JikanAPI._request("top/people", {"page": page})