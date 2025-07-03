import json
import time
import os
from . import local_database, public_api
from .config import TOKEN_PATH
import xbmc
import xbmcgui

REMINDERS_FILE = os.path.join(TOKEN_PATH, 'smart_reminders.json')

def init_smart_reminders():
    """Inicializar recordatorios inteligentes"""
    try:
        if not os.path.exists(REMINDERS_FILE):
            default_config = {
                'episode_reminders': True,
                'completion_reminders': True,
                'seasonal_reminders': True,
                'binge_suggestions': True,
                'reminder_frequency': 'daily',
                'quiet_hours': {'start': 22, 'end': 8}
            }
            save_reminders_config(default_config)
        return True
    except Exception as e:
        xbmc.log(f'Smart Reminders: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def save_reminders_config(config):
    """Guardar configuración de recordatorios"""
    try:
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        xbmc.log(f'Smart Reminders: Save config error - {str(e)}', xbmc.LOGERROR)

def load_reminders_config():
    """Cargar configuración de recordatorios"""
    try:
        with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def check_smart_reminders():
    """Verificar y mostrar recordatorios inteligentes"""
    config = load_reminders_config()
    
    # Verificar horas silenciosas
    current_hour = time.localtime().tm_hour
    quiet_start = config.get('quiet_hours', {}).get('start', 22)
    quiet_end = config.get('quiet_hours', {}).get('end', 8)
    
    if quiet_start <= current_hour or current_hour <= quiet_end:
        return  # Horas silenciosas
    
    reminders = []
    
    if config.get('episode_reminders', True):
        reminders.extend(get_episode_reminders())
    
    if config.get('completion_reminders', True):
        reminders.extend(get_completion_reminders())
    
    if config.get('binge_suggestions', True):
        reminders.extend(get_binge_suggestions())
    
    # Mostrar recordatorios
    for reminder in reminders[:3]:  # Máximo 3 por vez
        show_smart_reminder(reminder)

def get_episode_reminders():
    """Obtener recordatorios de episodios"""
    reminders = []
    
    try:
        watching_list = local_database.get_local_anime_list('watching')
        
        for anime in watching_list:
            progress_percent = 0
            if anime['total_episodes'] > 0:
                progress_percent = (anime['episodes_watched'] / anime['total_episodes']) * 100
            
            # Recordar anime con poco progreso
            if progress_percent < 20 and anime['episodes_watched'] > 0:
                reminders.append({
                    'type': 'low_progress',
                    'title': 'Anime con poco progreso',
                    'message': f"{anime['title']} - Solo {progress_percent:.0f}% completado",
                    'anime_id': anime['mal_id']
                })
            
            # Recordar anime casi completos
            elif progress_percent > 80:
                reminders.append({
                    'type': 'almost_complete',
                    'title': 'Casi terminas este anime',
                    'message': f"{anime['title']} - {progress_percent:.0f}% completado",
                    'anime_id': anime['mal_id']
                })
    
    except Exception as e:
        xbmc.log(f'Smart Reminders: Episode reminders error - {str(e)}', xbmc.LOGERROR)
    
    return reminders

def get_completion_reminders():
    """Obtener recordatorios de finalización"""
    reminders = []
    
    try:
        on_hold_list = local_database.get_local_anime_list('on_hold')
        
        for anime in on_hold_list:
            # Simular tiempo en pausa (en implementación real usar timestamps)
            days_on_hold = 45  # Placeholder
            
            if days_on_hold > 30:
                reminders.append({
                    'type': 'long_hold',
                    'title': 'Anime en pausa por mucho tiempo',
                    'message': f"{anime['title']} - {days_on_hold} días en pausa",
                    'anime_id': anime['mal_id']
                })
    
    except Exception as e:
        xbmc.log(f'Smart Reminders: Completion reminders error - {str(e)}', xbmc.LOGERROR)
    
    return reminders

def get_binge_suggestions():
    """Obtener sugerencias de maratón"""
    reminders = []
    
    try:
        plan_to_watch = local_database.get_local_anime_list('plan_to_watch')
        
        # Sugerir anime cortos para maratón
        short_anime = [anime for anime in plan_to_watch 
                      if anime['total_episodes'] <= 12 and anime['total_episodes'] > 0]
        
        if short_anime:
            anime = short_anime[0]  # Tomar el primero
            reminders.append({
                'type': 'binge_suggestion',
                'title': 'Perfecto para maratón',
                'message': f"{anime['title']} - Solo {anime['total_episodes']} episodios",
                'anime_id': anime['mal_id']
            })
    
    except Exception as e:
        xbmc.log(f'Smart Reminders: Binge suggestions error - {str(e)}', xbmc.LOGERROR)
    
    return reminders

def show_smart_reminder(reminder):
    """Mostrar recordatorio inteligente"""
    try:
        icon_map = {
            'low_progress': '⏳',
            'almost_complete': '🎯',
            'long_hold': '⏸️',
            'binge_suggestion': '🍿'
        }
        
        icon = icon_map.get(reminder['type'], '💡')
        
        xbmcgui.Dialog().notification(
            f"{icon} {reminder['title']}",
            reminder['message'],
            icon=xbmcgui.NOTIFICATION_INFO,
            time=4000
        )
        
    except Exception as e:
        xbmc.log(f'Smart Reminders: Show reminder error - {str(e)}', xbmc.LOGERROR)

def configure_smart_reminders():
    """Configurar recordatorios inteligentes"""
    config = load_reminders_config()
    
    options = [
        f"Recordatorios de episodios: {'✓' if config.get('episode_reminders', True) else '✗'}",
        f"Recordatorios de finalización: {'✓' if config.get('completion_reminders', True) else '✗'}",
        f"Sugerencias de maratón: {'✓' if config.get('binge_suggestions', True) else '✗'}",
        f"Frecuencia: {config.get('reminder_frequency', 'daily')}",
        "Configurar horas silenciosas"
    ]
    
    selected = xbmcgui.Dialog().select('Recordatorios Inteligentes:', options)
    
    if selected == 0:
        config['episode_reminders'] = not config.get('episode_reminders', True)
        save_reminders_config(config)
        
    elif selected == 1:
        config['completion_reminders'] = not config.get('completion_reminders', True)
        save_reminders_config(config)
        
    elif selected == 2:
        config['binge_suggestions'] = not config.get('binge_suggestions', True)
        save_reminders_config(config)
        
    elif selected == 3:
        frequencies = ['hourly', 'daily', 'weekly']
        freq_idx = xbmcgui.Dialog().select('Frecuencia:', frequencies)
        if freq_idx != -1:
            config['reminder_frequency'] = frequencies[freq_idx]
            save_reminders_config(config)
            
    elif selected == 4:
        configure_quiet_hours(config)