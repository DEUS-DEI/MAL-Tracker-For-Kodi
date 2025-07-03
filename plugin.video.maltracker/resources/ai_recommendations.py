import json
import math
from collections import Counter
from . import local_database, public_api
import xbmc

def get_user_preferences():
    """Analizar preferencias del usuario basado en historial"""
    try:
        completed_anime = local_database.get_local_anime_list('completed')
        high_rated = [a for a in completed_anime if a['score'] >= 8]
        
        # Análisis de géneros favoritos
        all_genres = []
        for anime in high_rated:
            if anime['genres']:
                all_genres.extend(anime['genres'])
        
        genre_counts = Counter(all_genres)
        favorite_genres = [genre for genre, count in genre_counts.most_common(5)]
        
        # Análisis de estudios favoritos
        all_studios = []
        for anime in high_rated:
            if anime['studios']:
                all_studios.extend(anime['studios'])
        
        studio_counts = Counter(all_studios)
        favorite_studios = [studio for studio, count in studio_counts.most_common(3)]
        
        # Análisis de años favoritos
        years = [anime['year'] for anime in high_rated if anime['year']]
        year_counts = Counter(years)
        favorite_years = [year for year, count in year_counts.most_common(3)]
        
        return {
            'favorite_genres': favorite_genres,
            'favorite_studios': favorite_studios,
            'favorite_years': favorite_years,
            'avg_score': sum(a['score'] for a in high_rated) / len(high_rated) if high_rated else 7.0,
            'total_completed': len(completed_anime)
        }
        
    except Exception as e:
        xbmc.log(f'AI Recommendations: Preferences error - {str(e)}', xbmc.LOGERROR)
        return {}

def generate_recommendations(limit=20):
    """Generar recomendaciones basadas en IA local"""
    preferences = get_user_preferences()
    if not preferences:
        return []
    
    recommendations = []
    my_list_ids = [anime['mal_id'] for anime in local_database.get_local_anime_list()]
    
    try:
        # Recomendaciones por género favorito
        for genre in preferences['favorite_genres'][:3]:
            genre_recs = search_by_genre_ai(genre, my_list_ids, 5)
            recommendations.extend(genre_recs)
        
        # Recomendaciones por estudio favorito
        for studio in preferences['favorite_studios'][:2]:
            studio_recs = search_by_studio_ai(studio, my_list_ids, 3)
            recommendations.extend(studio_recs)
        
        # Recomendaciones por año favorito
        if preferences['favorite_years']:
            year_recs = search_by_year_ai(preferences['favorite_years'][0], my_list_ids, 5)
            recommendations.extend(year_recs)
        
        # Calcular puntuaciones de recomendación
        scored_recs = []
        for rec in recommendations:
            score = calculate_recommendation_score(rec, preferences)
            scored_recs.append((rec, score))
        
        # Ordenar por puntuación y eliminar duplicados
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        unique_recs = []
        seen_ids = set()
        
        for rec, score in scored_recs:
            if rec.get('mal_id') not in seen_ids:
                rec['recommendation_score'] = score
                unique_recs.append(rec)
                seen_ids.add(rec.get('mal_id'))
                
                if len(unique_recs) >= limit:
                    break
        
        return unique_recs
        
    except Exception as e:
        xbmc.log(f'AI Recommendations: Generate error - {str(e)}', xbmc.LOGERROR)
        return []

def search_by_genre_ai(genre, exclude_ids, limit):
    """Buscar anime por género para IA"""
    try:
        results = public_api.search_anime_public(genre, limit * 2)
        if results and 'data' in results:
            filtered = [anime for anime in results['data'] 
                       if anime.get('mal_id') not in exclude_ids]
            return filtered[:limit]
    except:
        pass
    return []

def search_by_studio_ai(studio, exclude_ids, limit):
    """Buscar anime por estudio para IA"""
    try:
        results = public_api.search_anime_public(studio, limit * 2)
        if results and 'data' in results:
            filtered = [anime for anime in results['data'] 
                       if anime.get('mal_id') not in exclude_ids]
            return filtered[:limit]
    except:
        pass
    return []

def search_by_year_ai(year, exclude_ids, limit):
    """Buscar anime por año para IA"""
    try:
        # Usar API de temporada
        seasonal = public_api.get_seasonal_anime_public()
        if seasonal and 'data' in seasonal:
            filtered = [anime for anime in seasonal['data'] 
                       if anime.get('mal_id') not in exclude_ids]
            return filtered[:limit]
    except:
        pass
    return []

def calculate_recommendation_score(anime, preferences):
    """Calcular puntuación de recomendación"""
    score = 0.0
    
    # Puntuación base del anime
    base_score = anime.get('score', 0)
    if base_score:
        score += base_score * 0.3
    
    # Bonus por géneros favoritos
    anime_genres = [g.get('name', '') for g in anime.get('genres', [])]
    genre_matches = len(set(anime_genres) & set(preferences['favorite_genres']))
    score += genre_matches * 2.0
    
    # Bonus por estudios favoritos
    anime_studios = [s.get('name', '') for s in anime.get('studios', [])]
    studio_matches = len(set(anime_studios) & set(preferences['favorite_studios']))
    score += studio_matches * 1.5
    
    # Bonus por popularidad
    popularity = anime.get('popularity', 0)
    if popularity:
        score += (10000 - popularity) / 1000  # Más popular = mayor score
    
    # Penalty por muy viejo o muy nuevo
    anime_year = anime.get('year', 0)
    if anime_year and preferences['favorite_years']:
        year_diff = min(abs(anime_year - year) for year in preferences['favorite_years'])
        score -= year_diff * 0.1
    
    return round(score, 2)

def get_similar_anime(anime_id, limit=10):
    """Obtener anime similar a uno específico"""
    try:
        # Obtener detalles del anime base
        base_anime = public_api.get_anime_details_public(anime_id)
        if not base_anime:
            return []
        
        base_genres = [g.get('name', '') for g in base_anime.get('genres', [])]
        base_studios = [s.get('name', '') for s in base_anime.get('studios', [])]
        
        # Buscar anime similar por géneros
        similar = []
        my_list_ids = [anime['mal_id'] for anime in local_database.get_local_anime_list()]
        
        for genre in base_genres[:2]:  # Top 2 géneros
            genre_results = search_by_genre_ai(genre, my_list_ids + [anime_id], 5)
            similar.extend(genre_results)
        
        # Calcular similitud
        scored_similar = []
        for anime in similar:
            similarity = calculate_similarity(anime, base_anime)
            scored_similar.append((anime, similarity))
        
        # Ordenar por similitud
        scored_similar.sort(key=lambda x: x[1], reverse=True)
        
        return [anime for anime, score in scored_similar[:limit]]
        
    except Exception as e:
        xbmc.log(f'AI Recommendations: Similar anime error - {str(e)}', xbmc.LOGERROR)
        return []

def calculate_similarity(anime1, anime2):
    """Calcular similitud entre dos anime"""
    similarity = 0.0
    
    # Similitud de géneros
    genres1 = set(g.get('name', '') for g in anime1.get('genres', []))
    genres2 = set(g.get('name', '') for g in anime2.get('genres', []))
    
    if genres1 and genres2:
        genre_similarity = len(genres1 & genres2) / len(genres1 | genres2)
        similarity += genre_similarity * 3.0
    
    # Similitud de estudios
    studios1 = set(s.get('name', '') for s in anime1.get('studios', []))
    studios2 = set(s.get('name', '') for s in anime2.get('studios', []))
    
    if studios1 and studios2:
        studio_similarity = len(studios1 & studios2) / len(studios1 | studios2)
        similarity += studio_similarity * 2.0
    
    # Similitud de puntuación
    score1 = anime1.get('score', 0)
    score2 = anime2.get('score', 0)
    
    if score1 and score2:
        score_diff = abs(score1 - score2)
        score_similarity = max(0, 1 - score_diff / 10)
        similarity += score_similarity * 1.0
    
    return round(similarity, 2)

def get_trending_recommendations():
    """Obtener recomendaciones trending"""
    try:
        # Combinar top anime y anime de temporada
        top_anime = public_api.get_top_anime_public()
        seasonal_anime = public_api.get_seasonal_anime_public()
        
        trending = []
        my_list_ids = [anime['mal_id'] for anime in local_database.get_local_anime_list()]
        
        # Top anime no en mi lista
        if top_anime and 'data' in top_anime:
            for anime in top_anime['data'][:10]:
                if anime.get('mal_id') not in my_list_ids:
                    anime['trend_type'] = 'top_rated'
                    trending.append(anime)
        
        # Anime de temporada no en mi lista
        if seasonal_anime and 'data' in seasonal_anime:
            for anime in seasonal_anime['data'][:10]:
                if anime.get('mal_id') not in my_list_ids:
                    anime['trend_type'] = 'seasonal'
                    trending.append(anime)
        
        return trending[:15]
        
    except Exception as e:
        xbmc.log(f'AI Recommendations: Trending error - {str(e)}', xbmc.LOGERROR)
        return []