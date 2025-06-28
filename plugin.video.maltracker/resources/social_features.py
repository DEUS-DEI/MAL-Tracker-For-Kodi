import json
import os
import time
import xbmc
import xbmcgui
from . import local_database
from .config import TOKEN_PATH

SOCIAL_FILE = os.path.join(TOKEN_PATH, 'social_data.json')

def init_social_features():
    """Inicializar características sociales"""
    try:
        if not os.path.exists(SOCIAL_FILE):
            default_data = {
                'friends': [],
                'groups': [],
                'shared_lists': [],
                'reviews': [],
                'recommendations_given': [],
                'recommendations_received': []
            }
            save_social_data(default_data)
        return True
    except Exception as e:
        xbmc.log(f'Social Features: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def save_social_data(data):
    """Guardar datos sociales"""
    try:
        with open(SOCIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        xbmc.log(f'Social Features: Save error - {str(e)}', xbmc.LOGERROR)

def load_social_data():
    """Cargar datos sociales"""
    try:
        with open(SOCIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'friends': [], 'groups': [], 'reviews': []}

def show_social_menu():
    """Mostrar menú social"""
    options = [
        '👥 Gestionar amigos',
        '📝 Mis reviews',
        '🎯 Recomendaciones',
        '📊 Comparar listas',
        '🏆 Competencias',
        '📢 Compartir logros',
        '💬 Foro de discusión'
    ]
    
    selected = xbmcgui.Dialog().select('Características Sociales:', options)
    
    if selected == 0:
        manage_friends()
    elif selected == 1:
        manage_reviews()
    elif selected == 2:
        manage_recommendations()
    elif selected == 3:
        compare_lists()
    elif selected == 4:
        show_competitions()
    elif selected == 5:
        share_achievements()
    elif selected == 6:
        show_discussion_forum()

def manage_friends():
    """Gestionar lista de amigos"""
    social_data = load_social_data()
    friends = social_data.get('friends', [])
    
    if not friends:
        if xbmcgui.Dialog().yesno('Amigos', '¿Agregar tu primer amigo?'):
            add_friend()
        return
    
    friend_options = [f"{friend['name']} ({friend['platform']})" for friend in friends]
    friend_options.append('➕ Agregar amigo')
    
    selected = xbmcgui.Dialog().select('Mis Amigos:', friend_options)
    
    if selected == len(friend_options) - 1:
        add_friend()
    elif selected != -1:
        show_friend_profile(friends[selected])

def add_friend():
    """Agregar nuevo amigo"""
    platforms = ['MyAnimeList', 'AniList', 'Kitsu', 'Local']
    platform_idx = xbmcgui.Dialog().select('Plataforma del amigo:', platforms)
    
    if platform_idx == -1:
        return
    
    platform = platforms[platform_idx]
    username = xbmcgui.Dialog().input(f'Usuario de {platform}:')
    
    if username:
        social_data = load_social_data()
        
        new_friend = {
            'name': username,
            'platform': platform,
            'added_date': int(time.time()),
            'compatibility_score': 0,
            'shared_anime': 0
        }
        
        social_data['friends'].append(new_friend)
        save_social_data(social_data)
        
        xbmcgui.Dialog().notification('Social', f'Amigo agregado: {username}')

def manage_reviews():
    """Gestionar reviews de anime"""
    social_data = load_social_data()
    reviews = social_data.get('reviews', [])
    
    options = ['✍️ Escribir nueva review']
    options.extend([f"📝 {review['anime_title']} ({review['rating']}/10)" for review in reviews])
    
    selected = xbmcgui.Dialog().select('Mis Reviews:', options)
    
    if selected == 0:
        write_review()
    elif selected > 0:
        show_review(reviews[selected - 1])

def write_review():
    """Escribir nueva review"""
    # Seleccionar anime de la lista completada
    completed_anime = local_database.get_local_anime_list('completed')
    
    if not completed_anime:
        xbmcgui.Dialog().notification('Reviews', 'No tienes anime completado')
        return
    
    anime_titles = [anime['title'] for anime in completed_anime]
    selected = xbmcgui.Dialog().select('Seleccionar anime:', anime_titles)
    
    if selected == -1:
        return
    
    anime = completed_anime[selected]
    
    # Pedir calificación
    rating = xbmcgui.Dialog().input('Calificación (1-10):', str(anime.get('score', 8)))
    if not rating or not rating.isdigit() or not (1 <= int(rating) <= 10):
        return
    
    # Pedir review
    review_text = xbmcgui.Dialog().input('Escribe tu review:', type=xbmcgui.INPUT_ALPHANUM)
    if not review_text:
        return
    
    # Guardar review
    social_data = load_social_data()
    
    new_review = {
        'anime_id': anime['mal_id'],
        'anime_title': anime['title'],
        'rating': int(rating),
        'review_text': review_text,
        'date': int(time.time()),
        'likes': 0,
        'helpful_votes': 0
    }
    
    social_data['reviews'].append(new_review)
    save_social_data(social_data)
    
    xbmcgui.Dialog().notification('Reviews', f'Review publicada: {anime["title"]}')

def compare_lists():
    """Comparar listas con amigos"""
    social_data = load_social_data()
    friends = social_data.get('friends', [])
    
    if not friends:
        xbmcgui.Dialog().notification('Social', 'Agrega amigos para comparar listas')
        return
    
    friend_names = [friend['name'] for friend in friends]
    selected = xbmcgui.Dialog().select('Comparar con:', friend_names)
    
    if selected != -1:
        friend = friends[selected]
        show_list_comparison(friend)

def show_list_comparison(friend):
    """Mostrar comparación de listas"""
    # Simulación de comparación
    my_stats = local_database.get_local_stats()
    
    comparison = f"📊 COMPARACIÓN DE LISTAS\n\n"
    comparison += f"TÚ vs {friend['name']}\n"
    comparison += "─" * 30 + "\n"
    comparison += f"Total anime: {my_stats.get('total_anime', 0)} vs {friend.get('total_anime', 85)}\n"
    comparison += f"Completados: {my_stats.get('completed', 0)} vs {friend.get('completed', 45)}\n"
    comparison += f"Promedio: {my_stats.get('avg_score', 0)} vs {friend.get('avg_score', 7.8)}\n\n"
    
    comparison += "🎯 COMPATIBILIDAD:\n"
    compatibility = calculate_compatibility(friend)
    comparison += f"Puntuación: {compatibility}%\n"
    
    if compatibility >= 80:
        comparison += "¡Excelente compatibilidad! 🎉"
    elif compatibility >= 60:
        comparison += "Buena compatibilidad 👍"
    else:
        comparison += "Gustos diferentes 🤔"
    
    xbmcgui.Dialog().textviewer('Comparación de Listas', comparison)

def calculate_compatibility(friend):
    """Calcular compatibilidad con amigo"""
    # Simulación de cálculo de compatibilidad
    import random
    return random.randint(60, 95)

def show_competitions():
    """Mostrar competencias activas"""
    competitions = [
        {
            'name': 'Maratón de Enero',
            'description': 'Completa 10 anime este mes',
            'participants': 15,
            'your_progress': 7,
            'target': 10,
            'ends_in': '5 días'
        },
        {
            'name': 'Explorador de Géneros',
            'description': 'Ve anime de 5 géneros diferentes',
            'participants': 23,
            'your_progress': 3,
            'target': 5,
            'ends_in': '12 días'
        }
    ]
    
    info = "🏆 COMPETENCIAS ACTIVAS\n\n"
    
    for comp in competitions:
        progress_percent = (comp['your_progress'] / comp['target']) * 100
        progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
        
        info += f"🎯 {comp['name']}\n"
        info += f"   {comp['description']}\n"
        info += f"   Progreso: {comp['your_progress']}/{comp['target']} {progress_bar}\n"
        info += f"   Participantes: {comp['participants']}\n"
        info += f"   Termina en: {comp['ends_in']}\n\n"
    
    xbmcgui.Dialog().textviewer('Competencias', info)

def share_achievements():
    """Compartir logros"""
    from . import gamification
    
    achievements_data = gamification.load_achievements_data()
    
    if not achievements_data:
        xbmcgui.Dialog().notification('Social', 'No tienes logros para compartir')
        return
    
    recent_achievements = list(achievements_data.keys())[-3:]  # Últimos 3 logros
    
    share_options = []
    for achievement_id in recent_achievements:
        achievement = gamification.ACHIEVEMENTS.get(achievement_id, {})
        share_options.append(f"{achievement.get('icon', '🏆')} {achievement.get('name', 'Logro')}")
    
    selected = xbmcgui.Dialog().select('Compartir logro:', share_options)
    
    if selected != -1:
        achievement_id = recent_achievements[selected]
        achievement = gamification.ACHIEVEMENTS.get(achievement_id, {})
        
        message = f"¡Acabo de desbloquear el logro '{achievement.get('name', 'Logro')}' en MAL Tracker! 🎉"
        
        # Simular compartir
        xbmcgui.Dialog().notification('Social', 'Logro compartido en redes sociales')

def show_discussion_forum():
    """Mostrar foro de discusión"""
    topics = [
        {'title': '¿Cuál es tu anime favorito de esta temporada?', 'replies': 23, 'author': 'AnimeUser1'},
        {'title': 'Recomendaciones de anime de acción', 'replies': 15, 'author': 'ActionFan'},
        {'title': 'Debate: ¿Subtítulos o doblaje?', 'replies': 67, 'author': 'DebateMaster'},
        {'title': 'Anime infravalorados que deberías ver', 'replies': 31, 'author': 'HiddenGems'}
    ]
    
    info = "💬 FORO DE DISCUSIÓN\n\n"
    
    for topic in topics:
        info += f"📝 {topic['title']}\n"
        info += f"   Por: {topic['author']} | Respuestas: {topic['replies']}\n\n"
    
    info += "💡 Funcionalidad en desarrollo...\n"
    info += "Próximamente podrás participar en discusiones!"
    
    xbmcgui.Dialog().textviewer('Foro de Discusión', info)