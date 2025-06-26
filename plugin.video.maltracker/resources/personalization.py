import json
import os
import xbmc
import xbmcgui
from .config import TOKEN_PATH

THEMES_FILE = os.path.join(TOKEN_PATH, 'themes.json')
LAYOUT_FILE = os.path.join(TOKEN_PATH, 'layout.json')

# Temas disponibles
AVAILABLE_THEMES = {
    'default': {
        'name': 'Predeterminado',
        'primary_color': '#FF6B35',
        'secondary_color': '#004E89',
        'background': 'fanart',
        'icon_style': 'default'
    },
    'dark': {
        'name': 'Oscuro',
        'primary_color': '#BB86FC',
        'secondary_color': '#03DAC6',
        'background': 'dark',
        'icon_style': 'minimal'
    },
    'anime': {
        'name': 'Anime Style',
        'primary_color': '#FF69B4',
        'secondary_color': '#00CED1',
        'background': 'anime_art',
        'icon_style': 'kawaii'
    },
    'minimal': {
        'name': 'Minimalista',
        'primary_color': '#2196F3',
        'secondary_color': '#FFC107',
        'background': 'solid',
        'icon_style': 'clean'
    }
}

# Layouts disponibles
AVAILABLE_LAYOUTS = {
    'list': {
        'name': 'Lista',
        'description': 'Vista de lista tradicional',
        'columns': 1,
        'show_thumbnails': True,
        'show_details': True
    },
    'grid': {
        'name': 'Cuadrícula',
        'description': 'Vista en cuadrícula tipo Netflix',
        'columns': 3,
        'show_thumbnails': True,
        'show_details': False
    },
    'compact': {
        'name': 'Compacto',
        'description': 'Vista compacta con información mínima',
        'columns': 1,
        'show_thumbnails': False,
        'show_details': False
    },
    'detailed': {
        'name': 'Detallado',
        'description': 'Vista con máxima información',
        'columns': 1,
        'show_thumbnails': True,
        'show_details': True
    }
}

def init_personalization():
    """Inicializar sistema de personalización"""
    try:
        # Crear archivos de configuración si no existen
        if not os.path.exists(THEMES_FILE):
            save_theme_config('default')
        
        if not os.path.exists(LAYOUT_FILE):
            save_layout_config('list')
        
        return True
        
    except Exception as e:
        xbmc.log(f'Personalization: Init error - {str(e)}', xbmc.LOGERROR)
        return False

def save_theme_config(theme_id):
    """Guardar configuración de tema"""
    try:
        config = {
            'current_theme': theme_id,
            'custom_settings': {},
            'last_updated': int(time.time()) if 'time' in globals() else 0
        }
        
        with open(THEMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
    except Exception as e:
        xbmc.log(f'Personalization: Save theme error - {str(e)}', xbmc.LOGERROR)

def load_theme_config():
    """Cargar configuración de tema"""
    try:
        with open(THEMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'current_theme': 'default', 'custom_settings': {}}

def save_layout_config(layout_id):
    """Guardar configuración de layout"""
    try:
        config = {
            'current_layout': layout_id,
            'custom_settings': {},
            'last_updated': int(time.time()) if 'time' in globals() else 0
        }
        
        with open(LAYOUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
    except Exception as e:
        xbmc.log(f'Personalization: Save layout error - {str(e)}', xbmc.LOGERROR)

def load_layout_config():
    """Cargar configuración de layout"""
    try:
        with open(LAYOUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'current_layout': 'list', 'custom_settings': {}}

def show_personalization_menu():
    """Mostrar menú de personalización"""
    options = [
        '🎨 Cambiar tema',
        '📱 Cambiar layout',
        '🖼️ Configurar fondos',
        '⚙️ Configuración avanzada',
        '🔄 Restaurar predeterminado'
    ]
    
    selected = xbmcgui.Dialog().select('Personalización:', options)
    
    if selected == 0:
        change_theme()
    elif selected == 1:
        change_layout()
    elif selected == 2:
        configure_backgrounds()
    elif selected == 3:
        advanced_settings()
    elif selected == 4:
        reset_to_default()

def change_theme():
    """Cambiar tema visual"""
    current_theme = load_theme_config()['current_theme']
    
    theme_options = []
    theme_ids = []
    
    for theme_id, theme_data in AVAILABLE_THEMES.items():
        current_marker = ' ✓' if theme_id == current_theme else ''
        theme_options.append(f"{theme_data['name']}{current_marker}")
        theme_ids.append(theme_id)
    
    selected = xbmcgui.Dialog().select('Seleccionar Tema:', theme_options)
    
    if selected != -1:
        new_theme = theme_ids[selected]
        save_theme_config(new_theme)
        
        theme_name = AVAILABLE_THEMES[new_theme]['name']
        xbmcgui.Dialog().notification('MAL Tracker', f'Tema cambiado a: {theme_name}')
        
        # Refrescar interfaz
        xbmc.executebuiltin('Container.Refresh')

def change_layout():
    """Cambiar layout de vista"""
    current_layout = load_layout_config()['current_layout']
    
    layout_options = []
    layout_ids = []
    
    for layout_id, layout_data in AVAILABLE_LAYOUTS.items():
        current_marker = ' ✓' if layout_id == current_layout else ''
        layout_options.append(f"{layout_data['name']}{current_marker} - {layout_data['description']}")
        layout_ids.append(layout_id)
    
    selected = xbmcgui.Dialog().select('Seleccionar Layout:', layout_options)
    
    if selected != -1:
        new_layout = layout_ids[selected]
        save_layout_config(new_layout)
        
        layout_name = AVAILABLE_LAYOUTS[new_layout]['name']
        xbmcgui.Dialog().notification('MAL Tracker', f'Layout cambiado a: {layout_name}')
        
        # Refrescar interfaz
        xbmc.executebuiltin('Container.Refresh')

def configure_backgrounds():
    """Configurar fondos dinámicos"""
    bg_options = [
        'Fanart del anime actual',
        'Fondo sólido',
        'Artwork aleatorio',
        'Fondo personalizado',
        'Sin fondo'
    ]
    
    selected = xbmcgui.Dialog().select('Configurar Fondos:', bg_options)
    
    if selected != -1:
        bg_types = ['fanart', 'solid', 'random_art', 'custom', 'none']
        selected_bg = bg_types[selected]
        
        # Guardar configuración de fondo
        theme_config = load_theme_config()
        theme_config['custom_settings']['background'] = selected_bg
        
        with open(THEMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(theme_config, f, indent=2)
        
        xbmcgui.Dialog().notification('MAL Tracker', f'Fondo configurado: {bg_options[selected]}')

def advanced_settings():
    """Configuración avanzada de personalización"""
    options = [
        'Mostrar puntuaciones',
        'Mostrar progreso',
        'Mostrar géneros',
        'Mostrar año',
        'Animaciones de transición',
        'Iconos de estado personalizados'
    ]
    
    # Cargar configuración actual
    theme_config = load_theme_config()
    current_settings = theme_config.get('custom_settings', {})
    
    # Crear opciones con estado actual
    display_options = []
    for option in options:
        setting_key = option.lower().replace(' ', '_')
        current_state = current_settings.get(setting_key, True)
        state_icon = '✓' if current_state else '✗'
        display_options.append(f"{state_icon} {option}")
    
    selected = xbmcgui.Dialog().select('Configuración Avanzada:', display_options)
    
    if selected != -1:
        setting_key = options[selected].lower().replace(' ', '_')
        current_value = current_settings.get(setting_key, True)
        new_value = not current_value
        
        # Actualizar configuración
        current_settings[setting_key] = new_value
        theme_config['custom_settings'] = current_settings
        
        with open(THEMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(theme_config, f, indent=2)
        
        state_text = 'Activado' if new_value else 'Desactivado'
        xbmcgui.Dialog().notification('MAL Tracker', f'{options[selected]}: {state_text}')

def reset_to_default():
    """Restaurar configuración predeterminada"""
    if xbmcgui.Dialog().yesno('Confirmar', '¿Restaurar toda la personalización a valores predeterminados?'):
        save_theme_config('default')
        save_layout_config('list')
        
        xbmcgui.Dialog().notification('MAL Tracker', 'Configuración restaurada')
        xbmc.executebuiltin('Container.Refresh')

def get_current_theme():
    """Obtener tema actual"""
    config = load_theme_config()
    theme_id = config['current_theme']
    return AVAILABLE_THEMES.get(theme_id, AVAILABLE_THEMES['default'])

def get_current_layout():
    """Obtener layout actual"""
    config = load_layout_config()
    layout_id = config['current_layout']
    return AVAILABLE_LAYOUTS.get(layout_id, AVAILABLE_LAYOUTS['list'])

def apply_theme_to_listitem(listitem, anime_data):
    """Aplicar tema a un ListItem"""
    try:
        theme = get_current_theme()
        layout = get_current_layout()
        
        # Aplicar configuraciones de tema
        if layout['show_thumbnails'] and anime_data.get('image_url'):
            listitem.setArt({
                'thumb': anime_data['image_url'],
                'poster': anime_data['image_url']
            })
        
        # Configurar información según layout
        if layout['show_details']:
            plot_parts = []
            
            theme_settings = load_theme_config().get('custom_settings', {})
            
            if theme_settings.get('mostrar_puntuaciones', True) and anime_data.get('score'):
                plot_parts.append(f"Puntuación: {anime_data['score']}/10")
            
            if theme_settings.get('mostrar_progreso', True) and anime_data.get('episodes_watched'):
                total = anime_data.get('total_episodes', '?')
                plot_parts.append(f"Progreso: {anime_data['episodes_watched']}/{total}")
            
            if theme_settings.get('mostrar_géneros', True) and anime_data.get('genres'):
                genres = ', '.join(anime_data['genres'][:3])  # Máximo 3 géneros
                plot_parts.append(f"Géneros: {genres}")
            
            if theme_settings.get('mostrar_año', True) and anime_data.get('year'):
                plot_parts.append(f"Año: {anime_data['year']}")
            
            plot = '\n'.join(plot_parts)
            
            listitem.setInfo('video', {
                'title': anime_data.get('title', 'Sin título'),
                'plot': plot,
                'rating': float(anime_data.get('score', 0)),
                'year': anime_data.get('year', 0),
                'mediatype': 'tvshow'
            })
        
        return listitem
        
    except Exception as e:
        xbmc.log(f'Personalization: Apply theme error - {str(e)}', xbmc.LOGERROR)
        return listitem

def get_personalization_status():
    """Obtener estado de personalización"""
    theme_config = load_theme_config()
    layout_config = load_layout_config()
    
    current_theme = AVAILABLE_THEMES[theme_config['current_theme']]['name']
    current_layout = AVAILABLE_LAYOUTS[layout_config['current_layout']]['name']
    
    return {
        'theme': current_theme,
        'layout': current_layout,
        'customized': len(theme_config.get('custom_settings', {})) > 0
    }