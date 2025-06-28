import json
import math
from collections import defaultdict
from . import local_database
import xbmc

def predict_drop_probability(anime_id):
    """Predecir probabilidad de abandonar un anime"""
    try:
        anime_data = get_anime_by_id(anime_id)
        if not anime_data:
            return 0
        
        # Factores de predicción
        factors = {
            'low_progress': 0.3 if anime_data['episodes_watched'] < 3 else 0,
            'low_score': 0.4 if anime_data['score'] < 6 and anime_data['score'] > 0 else 0,
            'long_series': 0.2 if anime_data['total_episodes'] > 50 else 0,
            'genre_mismatch': calculate_genre_mismatch(anime_data),
            'time_stagnant': 0.3  # Placeholder para tiempo sin actualizar
        }
        
        drop_probability = min(sum(factors.values()), 1.0)
        return round(drop_probability * 100, 1)
        
    except Exception as e:
        xbmc.log(f'AI Advanced: Drop prediction error - {str(e)}', xbmc.LOGERROR)
        return 0

def predict_completion_time(anime_id):
    """Predecir tiempo para completar anime"""
    try:
        anime_data = get_anime_by_id(anime_id)
        if not anime_data:
            return "N/A"
        
        remaining_eps = anime_data['total_episodes'] - anime_data['episodes_watched']
        if remaining_eps <= 0:
            return "Completado"
        
        # Calcular velocidad promedio del usuario
        user_speed = calculate_user_watching_speed()
        
        # Estimar días para completar
        days_to_complete = remaining_eps / user_speed if user_speed > 0 else 30
        
        if days_to_complete < 7:
            return f"{int(days_to_complete)} días"
        elif days_to_complete < 30:
            return f"{int(days_to_complete/7)} semanas"
        else:
            return f"{int(days_to_complete/30)} meses"
            
    except Exception as e:
        xbmc.log(f'AI Advanced: Completion prediction error - {str(e)}', xbmc.LOGERROR)
        return "N/A"

def generate_mood_recommendations(mood):
    """Generar recomendaciones basadas en estado de ánimo"""
    mood_mappings = {
        'happy': ['Comedy', 'Slice of Life', 'Romance'],
        'sad': ['Drama', 'Romance', 'Music'],
        'excited': ['Action', 'Adventure', 'Sports'],
        'relaxed': ['Slice of Life', 'Iyashikei', 'Nature'],
        'thoughtful': ['Psychological', 'Mystery', 'Philosophical']
    }
    
    preferred_genres = mood_mappings.get(mood, ['Comedy'])
    
    # Buscar anime en lista local que coincida con el mood
    recommendations = []
    plan_to_watch = local_database.get_local_anime_list('plan_to_watch')
    
    for anime in plan_to_watch:
        if anime.get('genres'):
            anime_genres = anime['genres']
            if any(genre in anime_genres for genre in preferred_genres):
                recommendations.append({
                    'anime': anime,
                    'mood_match': calculate_mood_match(anime_genres, preferred_genres)
                })
    
    # Ordenar por coincidencia de mood
    recommendations.sort(key=lambda x: x['mood_match'], reverse=True)
    return recommendations[:5]

def calculate_optimal_binge_order():
    """Calcular orden óptimo para maratón"""
    try:
        plan_to_watch = local_database.get_local_anime_list('plan_to_watch')
        
        # Factores para orden óptimo
        scored_anime = []
        for anime in plan_to_watch:
            score = 0
            
            # Priorizar anime cortos
            if anime['total_episodes'] <= 12:
                score += 3
            elif anime['total_episodes'] <= 24:
                score += 2
            
            # Priorizar alta puntuación
            if anime.get('rating', 0) >= 8:
                score += 2
            
            # Priorizar géneros favoritos del usuario
            user_prefs = get_user_genre_preferences()
            if anime.get('genres'):
                genre_bonus = sum(1 for genre in anime['genres'] if genre in user_prefs)
                score += genre_bonus
            
            scored_anime.append((anime, score))
        
        # Ordenar por puntuación
        scored_anime.sort(key=lambda x: x[1], reverse=True)
        return [anime for anime, score in scored_anime[:10]]
        
    except Exception as e:
        xbmc.log(f'AI Advanced: Binge order error - {str(e)}', xbmc.LOGERROR)
        return []

def detect_viewing_patterns():
    """Detectar patrones de visualización del usuario"""
    try:
        activity_log = local_database.get_activity_log(100)
        
        patterns = {
            'most_active_day': detect_most_active_day(activity_log),
            'preferred_episode_length': detect_preferred_length(),
            'completion_rate': calculate_completion_rate(),
            'genre_evolution': detect_genre_evolution(),
            'binge_tendency': calculate_binge_tendency()
        }
        
        return patterns
        
    except Exception as e:
        xbmc.log(f'AI Advanced: Pattern detection error - {str(e)}', xbmc.LOGERROR)
        return {}

def smart_notification_timing():
    """Determinar mejor momento para notificaciones"""
    patterns = detect_viewing_patterns()
    
    # Basado en patrones de actividad
    optimal_times = []
    
    if patterns.get('most_active_day') == 'weekend':
        optimal_times.extend([19, 20, 21])  # Viernes-Domingo noche
    else:
        optimal_times.extend([18, 19])  # Después del trabajo
    
    return optimal_times

# Funciones auxiliares
def get_anime_by_id(anime_id):
    """Obtener anime por ID"""
    anime_list = local_database.get_local_anime_list()
    return next((anime for anime in anime_list if anime['mal_id'] == anime_id), None)

def calculate_genre_mismatch(anime_data):
    """Calcular desajuste de géneros"""
    user_prefs = get_user_genre_preferences()
    anime_genres = anime_data.get('genres', [])
    
    if not anime_genres or not user_prefs:
        return 0.1
    
    matches = sum(1 for genre in anime_genres if genre in user_prefs)
    mismatch = 1 - (matches / len(anime_genres))
    return mismatch * 0.2

def calculate_user_watching_speed():
    """Calcular velocidad de visualización del usuario"""
    # Placeholder - en implementación real usar timestamps
    return 2.5  # episodios por día promedio

def calculate_mood_match(anime_genres, preferred_genres):
    """Calcular coincidencia de mood"""
    matches = sum(1 for genre in anime_genres if genre in preferred_genres)
    return matches / len(preferred_genres) if preferred_genres else 0

def get_user_genre_preferences():
    """Obtener géneros preferidos del usuario"""
    completed = local_database.get_local_anime_list('completed')
    high_rated = [anime for anime in completed if anime.get('score', 0) >= 8]
    
    all_genres = []
    for anime in high_rated:
        if anime.get('genres'):
            all_genres.extend(anime['genres'])
    
    from collections import Counter
    return [genre for genre, count in Counter(all_genres).most_common(5)]

def detect_most_active_day(activity_log):
    """Detectar día más activo"""
    # Placeholder - implementar análisis real de timestamps
    return 'weekend'

def detect_preferred_length():
    """Detectar duración preferida de episodios"""
    completed = local_database.get_local_anime_list('completed')
    lengths = [anime['total_episodes'] for anime in completed if anime['total_episodes'] > 0]
    
    if not lengths:
        return 'unknown'
    
    avg_length = sum(lengths) / len(lengths)
    
    if avg_length <= 12:
        return 'short'
    elif avg_length <= 26:
        return 'standard'
    else:
        return 'long'

def calculate_completion_rate():
    """Calcular tasa de finalización"""
    stats = local_database.get_local_stats()
    total = stats.get('total_anime', 0)
    completed = stats.get('completed', 0)
    
    return round((completed / total * 100) if total > 0 else 0, 1)

def detect_genre_evolution():
    """Detectar evolución de géneros favoritos"""
    # Placeholder - implementar análisis temporal
    return 'stable'

def calculate_binge_tendency():
    """Calcular tendencia a hacer maratones"""
    # Placeholder - analizar patrones de episodios por día
    return 'moderate'