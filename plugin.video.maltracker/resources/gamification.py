import json
import os
import time
import xbmc
import xbmcgui
from . import local_database
from .config import TOKEN_PATH

ACHIEVEMENTS_FILE = os.path.join(TOKEN_PATH, 'achievements.json')
STATS_FILE = os.path.join(TOKEN_PATH, 'gamification_stats.json')

# Definición de logros
ACHIEVEMENTS = {
    'first_anime': {
        'name': 'Primer Paso',
        'description': 'Agrega tu primer anime a la lista',
        'icon': '🎬',
        'points': 10
    },
    'completionist_10': {
        'name': 'Completista Novato',
        'description': 'Completa 10 anime',
        'icon': '🏆',
        'points': 50
    },
    'completionist_50': {
        'name': 'Completista Experto',
        'description': 'Completa 50 anime',
        'icon': '🥇',
        'points': 200
    },
    'completionist_100': {
        'name': 'Completista Maestro',
        'description': 'Completa 100 anime',
        'icon': '👑',
        'points': 500
    },
    'genre_explorer': {
        'name': 'Explorador de Géneros',
        'description': 'Ve anime de 10 géneros diferentes',
        'icon': '🗺️',
        'points': 100
    },
    'binge_watcher': {
        'name': 'Maratonista',
        'description': 'Ve 100 episodios en una semana',
        'icon': '⚡',
        'points': 75
    },
    'critic': {
        'name': 'Crítico',
        'description': 'Puntúa 25 anime',
        'icon': '⭐',
        'points': 30
    },
    'perfectionist': {
        'name': 'Perfeccionista',
        'description': 'Da puntuación 10/10 a 5 anime',
        'icon': '💯',
        'points': 40
    },
    'streak_7': {
        'name': 'Racha Semanal',
        'description': 'Ve anime 7 días seguidos',
        'icon': '🔥',
        'points': 25
    },
    'streak_30': {
        'name': 'Racha Mensual',
        'description': 'Ve anime 30 días seguidos',
        'icon': '🌟',
        'points': 100
    },
    'early_bird': {
        'name': 'Madrugador',
        'description': 'Ve anime de temporada actual',
        'icon': '🌅',
        'points': 20
    },
    'vintage_lover': {
        'name': 'Amante Vintage',
        'description': 'Ve 10 anime de antes del 2000',
        'icon': '📼',
        'points': 60
    }
}

# Challenges mensuales
MONTHLY_CHALLENGES = {
    'january': {
        'name': 'Nuevo Año, Nuevos Anime',
        'description': 'Completa 5 anime este mes',
        'target': 5,
        'reward_points': 150
    },
    'february': {
        'name': 'Romance de San Valentín',
        'description': 'Ve 3 anime de romance',
        'target': 3,
        'reward_points': 100
    },
    'march': {
        'name': 'Primavera de Acción',
        'description': 'Ve 4 anime de acción',
        'target': 4,
        'reward_points': 120
    }
}

def init_gamification():
    """Inicializar sistema de gamificación"""
    try:
        if not os.path.exists(ACHIEVEMENTS_FILE):
            save_achievements_data({})
        
        if not os.path.exists(STATS_FILE):
            save_gamification_stats({
                'total_points': 0,
                'level': 1,
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity': 0,
                'monthly_progress': {}
            })
        
        return True
        
    except Exception as e:
        xbmc.log(f'Gamification: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def save_achievements_data(data):
    """Guardar datos de logros"""
    try:
        with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        xbmc.log(f'Gamification: Save achievements error - {str(e)}', xbmc.LOGERROR)

def load_achievements_data():
    """Cargar datos de logros"""
    try:
        with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_gamification_stats(stats):
    """Guardar estadísticas de gamificación"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        xbmc.log(f'Gamification: Save stats error - {str(e)}', xbmc.LOGERROR)

def load_gamification_stats():
    """Cargar estadísticas de gamificación"""
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'total_points': 0,
            'level': 1,
            'current_streak': 0,
            'longest_streak': 0,
            'last_activity': 0,
            'monthly_progress': {}
        }

def check_achievements():
    """Verificar y desbloquear logros"""
    try:
        achievements_data = load_achievements_data()
        stats = load_gamification_stats()
        local_stats = local_database.get_local_stats()
        
        new_achievements = []
        
        # Verificar cada logro
        if 'first_anime' not in achievements_data and local_stats.get('total_anime', 0) >= 1:
            unlock_achievement('first_anime', achievements_data, stats)
            new_achievements.append('first_anime')
        
        if 'completionist_10' not in achievements_data and local_stats.get('completed', 0) >= 10:
            unlock_achievement('completionist_10', achievements_data, stats)
            new_achievements.append('completionist_10')
        
        if 'completionist_50' not in achievements_data and local_stats.get('completed', 0) >= 50:
            unlock_achievement('completionist_50', achievements_data, stats)
            new_achievements.append('completionist_50')
        
        if 'completionist_100' not in achievements_data and local_stats.get('completed', 0) >= 100:
            unlock_achievement('completionist_100', achievements_data, stats)
            new_achievements.append('completionist_100')
        
        # Verificar explorador de géneros
        if 'genre_explorer' not in achievements_data:
            unique_genres = count_unique_genres()
            if unique_genres >= 10:
                unlock_achievement('genre_explorer', achievements_data, stats)
                new_achievements.append('genre_explorer')
        
        # Verificar crítico
        if 'critic' not in achievements_data:
            scored_anime = count_scored_anime()
            if scored_anime >= 25:
                unlock_achievement('critic', achievements_data, stats)
                new_achievements.append('critic')
        
        # Verificar perfeccionista
        if 'perfectionist' not in achievements_data:
            perfect_scores = count_perfect_scores()
            if perfect_scores >= 5:
                unlock_achievement('perfectionist', achievements_data, stats)
                new_achievements.append('perfectionist')
        
        # Mostrar notificaciones de nuevos logros
        for achievement_id in new_achievements:
            show_achievement_notification(achievement_id)
        
        # Actualizar nivel
        update_user_level(stats)
        
        return new_achievements
        
    except Exception as e:
        xbmc.log(f'Gamification: Check achievements error - {str(e)}', xbmc.LOGERROR)
        return []

def unlock_achievement(achievement_id, achievements_data, stats):
    """Desbloquear un logro"""
    try:
        achievement = ACHIEVEMENTS[achievement_id]
        
        achievements_data[achievement_id] = {
            'unlocked_at': int(time.time()),
            'points': achievement['points']
        }
        
        stats['total_points'] += achievement['points']
        
        save_achievements_data(achievements_data)
        save_gamification_stats(stats)
        
        xbmc.log(f'Gamification: Achievement unlocked - {achievement_id}', xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f'Gamification: Unlock achievement error - {str(e)}', xbmc.LOGERROR)

def show_achievement_notification(achievement_id):
    """Mostrar notificación de logro desbloqueado"""
    try:
        achievement = ACHIEVEMENTS[achievement_id]
        
        xbmcgui.Dialog().notification(
            f"{achievement['icon']} ¡Logro Desbloqueado!",
            f"{achievement['name']} (+{achievement['points']} pts)",
            icon=xbmcgui.NOTIFICATION_INFO,
            time=5000
        )
        
    except Exception as e:
        xbmc.log(f'Gamification: Show notification error - {str(e)}', xbmc.LOGERROR)

def count_unique_genres():
    """Contar géneros únicos en la lista"""
    try:
        anime_list = local_database.get_local_anime_list()
        all_genres = set()
        
        for anime in anime_list:
            if anime.get('genres'):
                all_genres.update(anime['genres'])
        
        return len(all_genres)
        
    except:
        return 0

def count_scored_anime():
    """Contar anime con puntuación"""
    try:
        anime_list = local_database.get_local_anime_list()
        return len([anime for anime in anime_list if anime.get('score', 0) > 0])
    except:
        return 0

def count_perfect_scores():
    """Contar anime con puntuación perfecta"""
    try:
        anime_list = local_database.get_local_anime_list()
        return len([anime for anime in anime_list if anime.get('score', 0) == 10])
    except:
        return 0

def update_user_level(stats):
    """Actualizar nivel del usuario"""
    try:
        points = stats['total_points']
        
        # Cálculo de nivel basado en puntos
        new_level = 1 + (points // 100)  # Cada 100 puntos = 1 nivel
        
        if new_level > stats['level']:
            stats['level'] = new_level
            save_gamification_stats(stats)
            
            xbmcgui.Dialog().notification(
                '🎉 ¡Nivel Subido!',
                f'Ahora eres nivel {new_level}',
                icon=xbmcgui.NOTIFICATION_INFO,
                time=4000
            )
        
    except Exception as e:
        xbmc.log(f'Gamification: Update level error - {str(e)}', xbmc.LOGERROR)

def show_achievements_menu():
    """Mostrar menú de logros"""
    try:
        achievements_data = load_achievements_data()
        stats = load_gamification_stats()
        
        info = f"PERFIL DE JUGADOR\n\n"
        info += f"Nivel: {stats['level']}\n"
        info += f"Puntos totales: {stats['total_points']}\n"
        info += f"Racha actual: {stats['current_streak']} días\n"
        info += f"Racha más larga: {stats['longest_streak']} días\n\n"
        
        info += "LOGROS DESBLOQUEADOS:\n"
        unlocked_count = 0
        
        for achievement_id, achievement in ACHIEVEMENTS.items():
            if achievement_id in achievements_data:
                info += f"{achievement['icon']} {achievement['name']} (+{achievement['points']} pts)\n"
                unlocked_count += 1
            else:
                info += f"🔒 {achievement['name']} - {achievement['description']}\n"
        
        info += f"\nProgreso: {unlocked_count}/{len(ACHIEVEMENTS)} logros desbloqueados"
        
        xbmcgui.Dialog().textviewer('Logros y Estadísticas', info)
        
    except Exception as e:
        xbmc.log(f'Gamification: Show achievements error - {str(e)}', xbmc.LOGERROR)

def update_activity_streak():
    """Actualizar racha de actividad"""
    try:
        stats = load_gamification_stats()
        current_time = int(time.time())
        last_activity = stats.get('last_activity', 0)
        
        # Verificar si es un nuevo día
        current_day = current_time // 86400  # Días desde epoch
        last_day = last_activity // 86400
        
        if current_day == last_day + 1:
            # Día consecutivo
            stats['current_streak'] += 1
            if stats['current_streak'] > stats['longest_streak']:
                stats['longest_streak'] = stats['current_streak']
        elif current_day > last_day + 1:
            # Se rompió la racha
            stats['current_streak'] = 1
        
        stats['last_activity'] = current_time
        save_gamification_stats(stats)
        
        # Verificar logros de racha
        check_streak_achievements(stats['current_streak'])
        
    except Exception as e:
        xbmc.log(f'Gamification: Update streak error - {str(e)}', xbmc.LOGERROR)

def check_streak_achievements(current_streak):
    """Verificar logros de racha"""
    try:
        achievements_data = load_achievements_data()
        stats = load_gamification_stats()
        
        if current_streak >= 7 and 'streak_7' not in achievements_data:
            unlock_achievement('streak_7', achievements_data, stats)
            show_achievement_notification('streak_7')
        
        if current_streak >= 30 and 'streak_30' not in achievements_data:
            unlock_achievement('streak_30', achievements_data, stats)
            show_achievement_notification('streak_30')
        
    except Exception as e:
        xbmc.log(f'Gamification: Check streak achievements error - {str(e)}', xbmc.LOGERROR)

def get_gamification_status():
    """Obtener estado de gamificación"""
    try:
        stats = load_gamification_stats()
        achievements_data = load_achievements_data()
        
        return {
            'level': stats['level'],
            'points': stats['total_points'],
            'achievements_unlocked': len(achievements_data),
            'total_achievements': len(ACHIEVEMENTS),
            'current_streak': stats['current_streak']
        }
        
    except:
        return {
            'level': 1,
            'points': 0,
            'achievements_unlocked': 0,
            'total_achievements': len(ACHIEVEMENTS),
            'current_streak': 0
        }