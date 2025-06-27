import xbmc
import xbmcgui
from . import local_database, public_api, ai_recommendations

def create_dashboard_widgets():
    """Crear widgets para dashboard"""
    widgets = []
    
    # Widget de progreso actual
    widgets.append(create_progress_widget())
    
    # Widget de recomendaciones
    widgets.append(create_recommendations_widget())
    
    # Widget de estadísticas rápidas
    widgets.append(create_stats_widget())
    
    # Widget de actividad reciente
    widgets.append(create_activity_widget())
    
    return widgets

def create_progress_widget():
    """Widget de progreso actual"""
    try:
        watching_list = local_database.get_local_anime_list('watching')
        
        widget_data = {
            'title': '▶️ Viendo Actualmente',
            'type': 'progress',
            'items': []
        }
        
        for anime in watching_list[:5]:  # Top 5
            progress = 0
            if anime['total_episodes'] > 0:
                progress = (anime['episodes_watched'] / anime['total_episodes']) * 100
            
            widget_data['items'].append({
                'title': anime['title'],
                'progress': f"{anime['episodes_watched']}/{anime['total_episodes']}",
                'progress_percent': progress,
                'anime_id': anime['mal_id']
            })
        
        return widget_data
        
    except Exception as e:
        xbmc.log(f'Widgets: Progress widget error - {str(e)}', xbmc.LOGERROR)
        return {'title': 'Error', 'type': 'error', 'items': []}

def create_recommendations_widget():
    """Widget de recomendaciones"""
    try:
        recommendations = ai_recommendations.generate_recommendations(5)
        
        widget_data = {
            'title': '🤖 Recomendaciones IA',
            'type': 'recommendations',
            'items': []
        }
        
        for rec in recommendations:
            widget_data['items'].append({
                'title': rec.get('title', 'Sin título'),
                'score': rec.get('score', 0),
                'recommendation_score': rec.get('recommendation_score', 0),
                'anime_id': rec.get('mal_id')
            })
        
        return widget_data
        
    except Exception as e:
        xbmc.log(f'Widgets: Recommendations widget error - {str(e)}', xbmc.LOGERROR)
        return {'title': 'Recomendaciones', 'type': 'recommendations', 'items': []}

def create_stats_widget():
    """Widget de estadísticas rápidas"""
    try:
        stats = local_database.get_local_stats()
        
        widget_data = {
            'title': '📊 Estadísticas',
            'type': 'stats',
            'items': [
                {'label': 'Total', 'value': stats.get('total_anime', 0)},
                {'label': 'Completados', 'value': stats.get('completed', 0)},
                {'label': 'Viendo', 'value': stats.get('watching', 0)},
                {'label': 'Promedio', 'value': f"{stats.get('avg_score', 0)}/10"}
            ]
        }
        
        return widget_data
        
    except Exception as e:
        xbmc.log(f'Widgets: Stats widget error - {str(e)}', xbmc.LOGERROR)
        return {'title': 'Estadísticas', 'type': 'stats', 'items': []}

def create_activity_widget():
    """Widget de actividad reciente"""
    try:
        activity = local_database.get_activity_log(5)
        
        widget_data = {
            'title': '📝 Actividad Reciente',
            'type': 'activity',
            'items': []
        }
        
        for act in activity:
            action_icons = {
                'add_anime': '➕',
                'update_status': '🔄',
                'update_episodes': '📺',
                'update_score': '⭐',
                'remove_anime': '❌'
            }
            
            icon = action_icons.get(act[0], '📝')
            widget_data['items'].append({
                'icon': icon,
                'action': act[0],
                'anime_title': act[1] or 'Anime',
                'timestamp': act[4]
            })
        
        return widget_data
        
    except Exception as e:
        xbmc.log(f'Widgets: Activity widget error - {str(e)}', xbmc.LOGERROR)
        return {'title': 'Actividad', 'type': 'activity', 'items': []}

def show_dashboard():
    """Mostrar dashboard con widgets"""
    widgets = create_dashboard_widgets()
    
    dashboard_info = "🏠 DASHBOARD MAL TRACKER\n\n"
    
    for widget in widgets:
        dashboard_info += f"{widget['title']}\n"
        dashboard_info += "─" * 30 + "\n"
        
        if widget['type'] == 'progress':
            for item in widget['items']:
                progress_bar = create_progress_bar(item['progress_percent'])
                dashboard_info += f"• {item['title']}\n"
                dashboard_info += f"  {item['progress']} {progress_bar}\n"
        
        elif widget['type'] == 'recommendations':
            for item in widget['items']:
                dashboard_info += f"• {item['title']} ({item['score']}/10)\n"
        
        elif widget['type'] == 'stats':
            for item in widget['items']:
                dashboard_info += f"• {item['label']}: {item['value']}\n"
        
        elif widget['type'] == 'activity':
            for item in widget['items']:
                dashboard_info += f"{item['icon']} {item['anime_title']}\n"
        
        dashboard_info += "\n"
    
    xbmcgui.Dialog().textviewer('Dashboard', dashboard_info)

def create_progress_bar(percent):
    """Crear barra de progreso visual"""
    filled = int(percent / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty + f" {percent:.0f}%"

def show_quick_actions():
    """Mostrar acciones rápidas"""
    actions = [
        '⚡ Actualizar anime viendo',
        '🔍 Búsqueda rápida',
        '📊 Ver estadísticas',
        '🎯 Marcar episodio visto',
        '⭐ Puntuar anime'
    ]
    
    selected = xbmcgui.Dialog().select('Acciones Rápidas:', actions)
    
    if selected == 0:
        show_quick_update()
    elif selected == 1:
        show_quick_search()
    elif selected == 2:
        from . import analytics
        analytics.show_analytics_dashboard()

def show_quick_update():
    """Actualización rápida de anime viendo"""
    watching_list = local_database.get_local_anime_list('watching')
    
    if not watching_list:
        xbmcgui.Dialog().notification('MAL Tracker', 'No tienes anime viendo')
        return
    
    anime_titles = [anime['title'] for anime in watching_list]
    selected = xbmcgui.Dialog().select('Actualizar anime:', anime_titles)
    
    if selected != -1:
        anime = watching_list[selected]
        current_ep = anime['episodes_watched']
        new_ep = xbmcgui.Dialog().input(f'Episodios vistos ({current_ep}):', str(current_ep + 1))
        
        if new_ep and new_ep.isdigit():
            local_database.update_anime_status(anime['mal_id'], None, int(new_ep))
            xbmcgui.Dialog().notification('MAL Tracker', f'Actualizado: {anime["title"]}')

def show_quick_search():
    """Búsqueda rápida"""
    query = xbmcgui.Dialog().input('Buscar anime:')
    if query:
        # Implementar búsqueda rápida
        xbmcgui.Dialog().notification('MAL Tracker', f'Buscando: {query}')