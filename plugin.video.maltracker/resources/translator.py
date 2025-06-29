import re

class SimpleTranslator:
    # Diccionario de traducciones comunes
    TRANSLATIONS = {
        # Estados
        'Currently Airing': 'En emisión',
        'Finished Airing': 'Finalizado',
        'Not yet aired': 'Próximamente',
        'Completed': 'Completado',
        'Ongoing': 'En curso',
        'Hiatus': 'En pausa',
        'Discontinued': 'Descontinuado',
        
        # Tipos
        'TV': 'TV',
        'Movie': 'Película',
        'OVA': 'OVA',
        'ONA': 'ONA',
        'Special': 'Especial',
        'Music': 'Musical',
        
        # Géneros comunes
        'Action': 'Acción',
        'Adventure': 'Aventura',
        'Comedy': 'Comedia',
        'Drama': 'Drama',
        'Fantasy': 'Fantasía',
        'Horror': 'Terror',
        'Mystery': 'Misterio',
        'Romance': 'Romance',
        'Sci-Fi': 'Ciencia Ficción',
        'Slice of Life': 'Recuentos de la vida',
        'Sports': 'Deportes',
        'Supernatural': 'Sobrenatural',
        'Thriller': 'Suspenso',
        'Psychological': 'Psicológico',
        'Historical': 'Histórico',
        'Military': 'Militar',
        'School': 'Escolar',
        'Shounen': 'Shounen',
        'Shoujo': 'Shoujo',
        'Seinen': 'Seinen',
        'Josei': 'Josei',
        'Kids': 'Infantil',
        'Mecha': 'Mecha',
        'Magic': 'Magia',
        'Martial Arts': 'Artes Marciales',
        'Music': 'Música',
        'Parody': 'Parodia',
        'Police': 'Policíaco',
        'Space': 'Espacial',
        'Vampire': 'Vampiros',
        'Demons': 'Demonios',
        'Game': 'Videojuegos',
        'Harem': 'Harem',
        'Ecchi': 'Ecchi',
        'Yaoi': 'Yaoi',
        'Yuri': 'Yuri',
        
        # Días de la semana
        'Monday': 'Lunes',
        'Tuesday': 'Martes', 
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo',
        
        # Temporadas
        'Spring': 'Primavera',
        'Summer': 'Verano',
        'Fall': 'Otoño',
        'Winter': 'Invierno',
        
        # Ratings
        'G - All Ages': 'G - Todas las edades',
        'PG - Children': 'PG - Niños',
        'PG-13 - Teens 13 or older': 'PG-13 - Adolescentes 13+',
        'R - 17+ (violence & profanity)': 'R - 17+ (violencia)',
        'R+ - Mild Nudity': 'R+ - Desnudez leve',
        'Rx - Hentai': 'Rx - Hentai',
        
        # Términos comunes
        'Score': 'Puntuación',
        'Rank': 'Ranking',
        'Popularity': 'Popularidad',
        'Members': 'Miembros',
        'Favorites': 'Favoritos',
        'Episodes': 'Episodios',
        'Duration': 'Duración',
        'Aired': 'Emitido',
        'Premiered': 'Estrenado',
        'Broadcast': 'Transmisión',
        'Producers': 'Productores',
        'Licensors': 'Licenciatarios',
        'Studios': 'Estudios',
        'Source': 'Fuente',
        'Genres': 'Géneros',
        'Themes': 'Temas',
        'Demographics': 'Demografía',
        'Synopsis': 'Sinopsis',
        'Background': 'Trasfondo',
        'Related': 'Relacionado',
        'Characters': 'Personajes',
        'Staff': 'Personal',
        'Reviews': 'Reseñas',
        'Recommendations': 'Recomendaciones',
        'Statistics': 'Estadísticas',
        'More Info': 'Más información',
        'External Links': 'Enlaces externos',
        'Streaming': 'Streaming',
        
        # Fuentes
        'Manga': 'Manga',
        'Light novel': 'Novela ligera',
        'Visual novel': 'Novela visual',
        'Video game': 'Videojuego',
        'Original': 'Original',
        'Web manga': 'Web manga',
        '4-koma manga': 'Manga 4-koma',
        'Novel': 'Novela',
        'Picture book': 'Libro ilustrado',
        'Radio': 'Radio',
        'Music': 'Música',
        
        # Relaciones
        'Sequel': 'Secuela',
        'Prequel': 'Precuela',
        'Alternative setting': 'Configuración alternativa',
        'Alternative version': 'Versión alternativa',
        'Side story': 'Historia paralela',
        'Parent story': 'Historia principal',
        'Summary': 'Resumen',
        'Full story': 'Historia completa',
        'Spin-off': 'Derivada',
        'Adaptation': 'Adaptación',
        'Character': 'Personaje',
        'Other': 'Otro'
    }
    
    @staticmethod
    def translate_text(text):
        """Traducir texto usando el diccionario"""
        if not text or not isinstance(text, str):
            return text
            
        # Traducción directa
        if text in SimpleTranslator.TRANSLATIONS:
            return SimpleTranslator.TRANSLATIONS[text]
        
        # Traducción parcial para frases
        translated = text
        for english, spanish in SimpleTranslator.TRANSLATIONS.items():
            translated = re.sub(r'\b' + re.escape(english) + r'\b', spanish, translated, flags=re.IGNORECASE)
        
        return translated
    
    @staticmethod
    def translate_list(items):
        """Traducir lista de elementos"""
        if not items:
            return items
        return [SimpleTranslator.translate_text(item) for item in items]
    
    @staticmethod
    def translate_genres(genres_list):
        """Traducir lista de géneros"""
        if not genres_list:
            return []
        
        translated = []
        for genre in genres_list:
            if isinstance(genre, dict):
                name = genre.get('name', '')
                translated.append(SimpleTranslator.translate_text(name))
            else:
                translated.append(SimpleTranslator.translate_text(str(genre)))
        
        return translated
    
    @staticmethod
    def translate_anime_data(anime_data):
        """Traducir datos completos de anime"""
        if not anime_data:
            return anime_data
        
        # Crear copia para no modificar original
        translated = anime_data.copy()
        
        # Traducir campos específicos
        if 'status' in translated:
            translated['status'] = SimpleTranslator.translate_text(translated['status'])
        
        if 'type' in translated:
            translated['type'] = SimpleTranslator.translate_text(translated['type'])
        
        if 'rating' in translated:
            translated['rating'] = SimpleTranslator.translate_text(translated['rating'])
        
        if 'source' in translated:
            translated['source'] = SimpleTranslator.translate_text(translated['source'])
        
        if 'genres' in translated:
            translated['genres_es'] = SimpleTranslator.translate_genres(translated['genres'])
        
        if 'themes' in translated:
            translated['themes_es'] = SimpleTranslator.translate_genres(translated['themes'])
        
        if 'demographics' in translated:
            translated['demographics_es'] = SimpleTranslator.translate_genres(translated['demographics'])
        
        return translated