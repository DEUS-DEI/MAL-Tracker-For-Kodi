"""
Reproductor automático con avance de episodios
"""

import xbmc
import xbmcgui
import threading
import time

class AutoPlayer(xbmc.Player):
    
    def __init__(self):
        super().__init__()
        self.episodes = []
        self.current_index = 0
        self.anime_title = ""
        self.site = ""
        self.auto_next = True
        
    def set_playlist(self, episodes, anime_title, site, start_index=0):
        """Configurar lista de episodios"""
        self.episodes = episodes
        self.current_index = start_index
        self.anime_title = anime_title
        self.site = site
        
    def play_current_episode(self):
        """Reproducir episodio actual"""
        if not self.episodes or self.current_index >= len(self.episodes):
            return False
            
        episode = self.episodes[self.current_index]
        
        # Determinar método de extracción
        if 'extractor' in episode:
            # Usar extractor avanzado
            video_url = episode['extractor'](episode['url'])
        else:
            # Usar scraper simple
            from . import simple_scraper
            video_url = simple_scraper.SimpleScraper.extract_video_url(episode['url'], self.site)
        
        if video_url:
            # Crear ListItem con información
            listitem = xbmcgui.ListItem(episode['title'])
            listitem.setInfo('video', {
                'title': episode['title'],
                'tvshowtitle': self.anime_title,
                'episode': self.current_index + 1,
                'mediatype': 'episode'
            })
            
            # Reproducir
            self.play(video_url, listitem)
            return True
        else:
            # Fallback: abrir en navegador
            import webbrowser
            webbrowser.open(episode['url'])
            return False
    
    def onPlayBackEnded(self):
        """Cuando termina la reproducción"""
        if self.auto_next and self.current_index < len(self.episodes) - 1:
            # Mostrar notificación de siguiente episodio
            next_episode = self.episodes[self.current_index + 1]
            
            dialog = xbmcgui.Dialog()
            if dialog.yesno('Siguiente Episodio', 
                f'Reproducir siguiente episodio?\n\n{next_episode["title"]}',
                autoclose=10000):  # 10 segundos para decidir
                
                self.current_index += 1
                threading.Thread(target=self.play_current_episode).start()
            else:
                xbmcgui.Dialog().notification('Reproducción', 'Serie finalizada')
        else:
            xbmcgui.Dialog().notification('Reproducción', 'Último episodio completado')
    
    def onPlayBackStopped(self):
        """Cuando se detiene manualmente"""
        # No hacer nada si el usuario para manualmente
        pass
    
    def show_episode_menu(self):
        """Mostrar menú de episodios con opciones"""
        if not self.episodes:
            return
            
        # Crear lista con estado actual
        episode_titles = []
        for i, ep in enumerate(self.episodes):
            prefix = "▶️ " if i == self.current_index else "   "
            episode_titles.append(f"{prefix}{ep['title']}")
        
        selected = xbmcgui.Dialog().select(
            f'{self.anime_title} - Episodios:', 
            episode_titles,
            preselect=self.current_index
        )
        
        if selected != -1:
            self.current_index = selected
            self.play_current_episode()
    
    def toggle_auto_next(self):
        """Alternar reproducción automática"""
        self.auto_next = not self.auto_next
        status = "activada" if self.auto_next else "desactivada"
        xbmcgui.Dialog().notification('Auto-reproducción', f'Reproducción automática {status}')
        
    def get_playback_info(self):
        """Obtener información de reproducción"""
        if self.episodes and self.current_index < len(self.episodes):
            current_ep = self.episodes[self.current_index]
            total_eps = len(self.episodes)
            
            return {
                'anime': self.anime_title,
                'current_episode': current_ep['title'],
                'progress': f"{self.current_index + 1}/{total_eps}",
                'auto_next': self.auto_next,
                'remaining': total_eps - self.current_index - 1
            }
        return None

# Instancia global del reproductor
auto_player = AutoPlayer()