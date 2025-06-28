import xbmc
import xbmcgui
import json
import re
from . import local_database, public_api

class AutoDetection:
    
    @staticmethod
    def monitor_kodi_playback():
        """Monitorear reproducción en Kodi para auto-actualizar"""
        try:
            # Obtener información del reproductor actual
            player = xbmc.Player()
            
            if player.isPlaying():
                # Obtener información del archivo
                playing_file = player.getPlayingFile()
                video_info = player.getVideoInfoTag()
                
                # Extraer título del anime
                title = video_info.getTitle() or extract_title_from_filename(playing_file)
                
                if title:
                    anime_match = find_anime_in_database(title)
                    if anime_match:
                        # Auto-actualizar progreso
                        episode_num = extract_episode_number(playing_file, title)
                        if episode_num:
                            auto_update_progress(anime_match['mal_id'], episode_num)
                            
        except Exception as e:
            xbmc.log(f'Auto Detection: Monitor error - {str(e)}', xbmc.LOGERROR)
    
    @staticmethod
    def setup_auto_detection():
        """Configurar detección automática"""
        options = [
            'Activar detección automática',
            'Configurar patrones de archivos',
            'Probar detección',
            'Ver historial de detecciones'
        ]
        
        selected = xbmcgui.Dialog().select('Auto-Detección:', options)
        
        if selected == 0:
            toggle_auto_detection()
        elif selected == 1:
            configure_file_patterns()
        elif selected == 2:
            test_detection()
        elif selected == 3:
            show_detection_history()

def extract_title_from_filename(filename):
    """Extraer título de anime del nombre de archivo"""
    try:
        # Patrones comunes de archivos de anime
        patterns = [
            r'\[.*?\]\s*(.+?)\s*-\s*\d+',  # [Grupo] Titulo - 01
            r'(.+?)\s*-\s*\d+',            # Titulo - 01
            r'(.+?)\s*EP?\d+',             # Titulo EP01
            r'(.+?)\s*Episode\s*\d+',      # Titulo Episode 01
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Limpiar caracteres especiales
                title = re.sub(r'[^\w\s-]', '', title).strip()
                return title
                
    except Exception as e:
        xbmc.log(f'Auto Detection: Extract title error - {str(e)}', xbmc.LOGERROR)
    
    return None

def find_anime_in_database(title):
    """Buscar anime en base de datos local"""
    try:
        anime_list = local_database.get_local_anime_list()
        
        # Búsqueda exacta
        for anime in anime_list:
            if anime['title'].lower() == title.lower():
                return anime
        
        # Búsqueda parcial
        for anime in anime_list:
            if title.lower() in anime['title'].lower() or anime['title'].lower() in title.lower():
                return anime
                
    except Exception as e:
        xbmc.log(f'Auto Detection: Find anime error - {str(e)}', xbmc.LOGERROR)
    
    return None

def extract_episode_number(filename, title):
    """Extraer número de episodio"""
    try:
        # Remover título para buscar número
        filename_clean = filename.replace(title, '')
        
        patterns = [
            r'(?:EP?|Episode)\s*(\d+)',
            r'-\s*(\d+)',
            r'\s(\d+)\s',
            r'_(\d+)_'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename_clean, re.IGNORECASE)
            if match:
                return int(match.group(1))
                
    except Exception as e:
        xbmc.log(f'Auto Detection: Extract episode error - {str(e)}', xbmc.LOGERROR)
    
    return None

def auto_update_progress(anime_id, episode_num):
    """Auto-actualizar progreso de anime"""
    try:
        # Verificar si debe actualizarse
        anime_data = get_anime_by_id(anime_id)
        if not anime_data:
            return
        
        current_episodes = anime_data['episodes_watched']
        
        # Solo actualizar si es progreso hacia adelante
        if episode_num > current_episodes:
            local_database.update_anime_status(anime_id, None, episode_num)
            
            # Notificar al usuario
            xbmcgui.Dialog().notification(
                'Auto-Actualizado',
                f"{anime_data['title']} - Episodio {episode_num}",
                time=3000
            )
            
            xbmc.log(f'Auto Detection: Updated {anime_data["title"]} to episode {episode_num}', xbmc.LOGINFO)
            
    except Exception as e:
        xbmc.log(f'Auto Detection: Update progress error - {str(e)}', xbmc.LOGERROR)

def get_anime_by_id(anime_id):
    """Obtener anime por ID"""
    anime_list = local_database.get_local_anime_list()
    return next((anime for anime in anime_list if anime['mal_id'] == anime_id), None)