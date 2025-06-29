from .jikan_complete import JikanComplete
from .translator import SimpleTranslator

class JikanTranslated:
    """Wrapper de Jikan con traducción automática"""
    
    @staticmethod
    def search_anime_translated(query, limit=25):
        """Buscar anime con traducción"""
        result = JikanComplete.search_anime(query, limit)
        if result and 'data' in result:
            for anime in result['data']:
                # Traducir campos principales
                if 'status' in anime:
                    anime['status_es'] = SimpleTranslator.translate_text(anime['status'])
                if 'type' in anime:
                    anime['type_es'] = SimpleTranslator.translate_text(anime['type'])
                if 'genres' in anime:
                    anime['genres_es'] = SimpleTranslator.translate_genres(anime['genres'])
        return result
    
    @staticmethod
    def get_anime_full_translated(anime_id):
        """Obtener anime completo con traducción"""
        result = JikanComplete.get_anime_full(anime_id)
        if result and 'data' in result:
            anime = result['data']
            
            # Traducir todos los campos relevantes
            anime['status_es'] = SimpleTranslator.translate_text(anime.get('status', ''))
            anime['type_es'] = SimpleTranslator.translate_text(anime.get('type', ''))
            anime['rating_es'] = SimpleTranslator.translate_text(anime.get('rating', ''))
            anime['source_es'] = SimpleTranslator.translate_text(anime.get('source', ''))
            
            if 'genres' in anime:
                anime['genres_es'] = SimpleTranslator.translate_genres(anime['genres'])
            if 'themes' in anime:
                anime['themes_es'] = SimpleTranslator.translate_genres(anime['themes'])
            if 'demographics' in anime:
                anime['demographics_es'] = SimpleTranslator.translate_genres(anime['demographics'])
            
            # Traducir estudios y productores
            if 'studios' in anime:
                anime['studios_names'] = [s.get('name', '') for s in anime['studios']]
            if 'producers' in anime:
                anime['producers_names'] = [p.get('name', '') for p in anime['producers']]
        
        return result
    
    @staticmethod
    def get_top_anime_translated(type=None, filter=None, page=1, limit=25):
        """Top anime con traducción"""
        result = JikanComplete.get_top_anime(type, filter, None, None, page, limit)
        if result and 'data' in result:
            for anime in result['data']:
                anime['status_es'] = SimpleTranslator.translate_text(anime.get('status', ''))
                anime['type_es'] = SimpleTranslator.translate_text(anime.get('type', ''))
                if 'genres' in anime:
                    anime['genres_es'] = SimpleTranslator.translate_genres(anime['genres'])
        return result
    
    @staticmethod
    def get_season_translated(year=None, season=None):
        """Temporada con traducción"""
        if year and season:
            result = JikanComplete.get_season(year, season)
        else:
            result = JikanComplete.get_season_now()
            
        if result and 'data' in result:
            for anime in result['data']:
                anime['status_es'] = SimpleTranslator.translate_text(anime.get('status', ''))
                anime['type_es'] = SimpleTranslator.translate_text(anime.get('type', ''))
                if 'genres' in anime:
                    anime['genres_es'] = SimpleTranslator.translate_genres(anime['genres'])
        return result
    
    @staticmethod
    def format_anime_info_spanish(anime_data):
        """Formatear información de anime en español"""
        if not anime_data:
            return "Sin información disponible"
        
        info_parts = []
        
        # Título
        title = anime_data.get('title', 'Sin título')
        info_parts.append(f"📺 {title}")
        
        # Información básica
        if anime_data.get('type_es'):
            info_parts.append(f"Tipo: {anime_data['type_es']}")
        
        if anime_data.get('episodes'):
            info_parts.append(f"Episodios: {anime_data['episodes']}")
        
        if anime_data.get('status_es'):
            info_parts.append(f"Estado: {anime_data['status_es']}")
        
        if anime_data.get('score'):
            info_parts.append(f"Puntuación: {anime_data['score']}/10")
        
        if anime_data.get('rank'):
            info_parts.append(f"Ranking: #{anime_data['rank']}")
        
        if anime_data.get('popularity'):
            info_parts.append(f"Popularidad: #{anime_data['popularity']}")
        
        # Fechas
        if anime_data.get('aired', {}).get('string'):
            info_parts.append(f"Emitido: {anime_data['aired']['string']}")
        
        # Géneros traducidos
        if anime_data.get('genres_es'):
            genres_str = ', '.join(anime_data['genres_es'][:5])
            info_parts.append(f"Géneros: {genres_str}")
        
        # Estudios
        if anime_data.get('studios_names'):
            studios_str = ', '.join(anime_data['studios_names'][:3])
            info_parts.append(f"Estudios: {studios_str}")
        
        # Rating traducido
        if anime_data.get('rating_es'):
            info_parts.append(f"Clasificación: {anime_data['rating_es']}")
        
        # Sinopsis
        if anime_data.get('synopsis'):
            synopsis = anime_data['synopsis'][:300] + "..." if len(anime_data['synopsis']) > 300 else anime_data['synopsis']
            info_parts.append(f"\n📖 Sinopsis:\n{synopsis}")
        
        return '\n'.join(info_parts)