import xbmc
import xbmcgui
import time
import json
import os
from . import local_database, public_api
from .config import TOKEN_PATH

NOTIFICATIONS_FILE = os.path.join(TOKEN_PATH, 'notifications.json')

def init_notifications():
    """Inicializar sistema de notificaciones"""
    try:
        if not os.path.exists(NOTIFICATIONS_FILE):
            save_notifications_config({
                'new_episodes': True,
                'season_reminders': True,
                'completion_reminders': True,
                'check_interval': 3600,  # 1 hora
                'last_check': 0
            })
        return True
    except Exception as e:
        xbmc.log(f'Notifications: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def save_notifications_config(config):
    """Guardar configuración de notificaciones"""
    try:
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        xbmc.log(f'Notifications: Save config error - {str(e)}', xbmc.LOGERROR)

def load_notifications_config():
    """Cargar configuración de notificaciones"""
    try:
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'new_episodes': True,
            'season_reminders': True,
            'completion_reminders': True,
            'check_interval': 3600,
            'last_check': 0
        }

def check_for_notifications():
    """Verificar y mostrar notificaciones pendientes"""
    config = load_notifications_config()
    current_time = time.time()
    
    # Verificar si es tiempo de chequear
    if current_time - config['last_check'] < config['check_interval']:
        return
    
    notifications = []
    
    if config['new_episodes']:
        notifications.extend(check_new_episodes())
    
    if config['season_reminders']:
        notifications.extend(check_season_reminders())
    
    if config['completion_reminders']:
        notifications.extend(check_completion_reminders())
    
    # Mostrar notificaciones
    for notification in notifications:
        show_notification(notification)
    
    # Actualizar último chequeo
    config['last_check'] = current_time
    save_notifications_config(config)

def check_new_episodes():
    """Verificar nuevos episodios de anime en seguimiento"""
    notifications = []
    
    try:
        # Obtener anime que estoy viendo
        watching_list = local_database.get_local_anime_list('watching')
        
        for anime in watching_list:
            # Verificar si hay nuevos episodios disponibles
            current_info = public_api.get_anime_details_public(anime['mal_id'])
            
            if current_info and current_info.get('episodes'):
                total_episodes = current_info.get('episodes', 0)
                watched_episodes = anime['episodes_watched']
                
                if total_episodes > watched_episodes:
                    notifications.append({
                        'type': 'new_episode',
                        'title': f"Nuevo episodio disponible",
                        'message': f"{anime['title']} - Episodio {watched_episodes + 1}",
                        'anime_id': anime['mal_id']
                    })
    
    except Exception as e:
        xbmc.log(f'Notifications: New episodes check error - {str(e)}', xbmc.LOGERROR)
    
    return notifications

def check_season_reminders():
    """Verificar recordatorios de temporada"""
    notifications = []
    
    try:
        # Obtener anime de temporada actual
        seasonal_anime = public_api.get_seasonal_anime_public()
        
        if seasonal_anime and 'data' in seasonal_anime:
            # Verificar si hay anime popular que no está en mi lista
            my_list_ids = [anime['mal_id'] for anime in local_database.get_local_anime_list()]
            
            for anime in seasonal_anime['data'][:5]:  # Top 5
                if anime.get('mal_id') not in my_list_ids:
                    score = anime.get('score', 0)
                    if score and score > 7.5:  # Solo anime bien puntuado
                        notifications.append({
                            'type': 'season_reminder',
                            'title': f"Anime popular de temporada",
                            'message': f"{anime.get('title')} ({score}/10)",
                            'anime_id': anime.get('mal_id')
                        })
    
    except Exception as e:
        xbmc.log(f'Notifications: Season reminders error - {str(e)}', xbmc.LOGERROR)
    
    return notifications

def check_completion_reminders():
    """Verificar recordatorios de finalización"""
    notifications = []
    
    try:
        # Obtener anime en pausa por más de 30 días
        on_hold_list = local_database.get_local_anime_list('on_hold')
        current_time = time.time()
        
        for anime in on_hold_list:
            # Calcular días desde última actualización (simulado)
            days_on_hold = 35  # Placeholder - implementar cálculo real
            
            if days_on_hold > 30:
                notifications.append({
                    'type': 'completion_reminder',
                    'title': f"Anime en pausa",
                    'message': f"{anime['title']} - {days_on_hold} días en pausa",
                    'anime_id': anime['mal_id']
                })
    
    except Exception as e:
        xbmc.log(f'Notifications: Completion reminders error - {str(e)}', xbmc.LOGERROR)
    
    return notifications

def show_notification(notification):
    """Mostrar notificación en Kodi"""
    try:
        xbmcgui.Dialog().notification(
            notification['title'],
            notification['message'],
            icon=xbmcgui.NOTIFICATION_INFO,
            time=5000
        )
        
        # Log para debugging
        xbmc.log(f"MAL Tracker Notification: {notification['message']}", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f'Notifications: Show notification error - {str(e)}', xbmc.LOGERROR)

def configure_notifications():
    """Configurar notificaciones"""
    config = load_notifications_config()
    
    # Menú de configuración
    options = [
        f"Nuevos episodios: {'✓' if config['new_episodes'] else '✗'}",
        f"Recordatorios de temporada: {'✓' if config['season_reminders'] else '✗'}",
        f"Recordatorios de finalización: {'✓' if config['completion_reminders'] else '✗'}",
        f"Intervalo de verificación: {config['check_interval']//60} min",
        "Probar notificaciones"
    ]
    
    selected = xbmcgui.Dialog().select('Configurar Notificaciones:', options)
    
    if selected == 0:
        config['new_episodes'] = not config['new_episodes']
        save_notifications_config(config)
        xbmcgui.Dialog().notification('MAL Tracker', f"Nuevos episodios: {'Activado' if config['new_episodes'] else 'Desactivado'}")
        
    elif selected == 1:
        config['season_reminders'] = not config['season_reminders']
        save_notifications_config(config)
        xbmcgui.Dialog().notification('MAL Tracker', f"Recordatorios de temporada: {'Activado' if config['season_reminders'] else 'Desactivado'}")
        
    elif selected == 2:
        config['completion_reminders'] = not config['completion_reminders']
        save_notifications_config(config)
        xbmcgui.Dialog().notification('MAL Tracker', f"Recordatorios de finalización: {'Activado' if config['completion_reminders'] else 'Desactivado'}")
        
    elif selected == 3:
        intervals = ['15 min', '30 min', '1 hora', '2 horas', '6 horas']
        interval_values = [900, 1800, 3600, 7200, 21600]
        
        interval_idx = xbmcgui.Dialog().select('Intervalo de verificación:', intervals)
        if interval_idx != -1:
            config['check_interval'] = interval_values[interval_idx]
            save_notifications_config(config)
            xbmcgui.Dialog().notification('MAL Tracker', f"Intervalo: {intervals[interval_idx]}")
            
    elif selected == 4:
        # Probar notificaciones
        test_notifications = [
            {
                'type': 'test',
                'title': 'Prueba de Notificación',
                'message': 'Las notificaciones están funcionando correctamente'
            }
        ]
        
        for notification in test_notifications:
            show_notification(notification)

def get_notifications_status():
    """Obtener estado de notificaciones para mostrar en menú"""
    config = load_notifications_config()
    
    active_count = sum([
        config['new_episodes'],
        config['season_reminders'], 
        config['completion_reminders']
    ])
    
    return {
        'active_count': active_count,
        'total_count': 3,
        'last_check': config['last_check'],
        'next_check': config['last_check'] + config['check_interval']
    }