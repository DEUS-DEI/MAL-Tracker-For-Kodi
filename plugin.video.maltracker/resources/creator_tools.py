import json
import os
import time
import xbmc
import xbmcgui
from . import local_database
from .config import TOKEN_PATH

def show_creator_tools():
    """Mostrar herramientas de creador"""
    options = [
        '📝 Editor de listas avanzado',
        '🎨 Creador de temas',
        '📊 Generador de reportes',
        '🔌 Exportar API',
        '📋 Plantillas personalizadas',
        '🎯 Configurador de filtros',
        '📈 Análisis personalizado'
    ]
    
    selected = xbmcgui.Dialog().select('Herramientas de Creador:', options)
    
    if selected == 0:
        advanced_list_editor()
    elif selected == 1:
        theme_creator()
    elif selected == 2:
        report_generator()
    elif selected == 3:
        api_exporter()
    elif selected == 4:
        template_manager()
    elif selected == 5:
        filter_configurator()
    elif selected == 6:
        custom_analytics()

def advanced_list_editor():
    """Editor avanzado de listas"""
    editor_options = [
        '✏️ Edición masiva',
        '🔄 Operaciones por lotes',
        '📋 Copiar/Pegar listas',
        '🎯 Filtros personalizados',
        '📊 Vista de tabla'
    ]
    
    selected = xbmcgui.Dialog().select('Editor Avanzado:', editor_options)
    
    if selected == 0:
        mass_edit_anime()
    elif selected == 1:
        batch_operations()
    elif selected == 2:
        copy_paste_lists()
    elif selected == 3:
        create_custom_filters()

def mass_edit_anime():
    """Edición masiva de anime"""
    # Seleccionar criterio de filtro
    filter_options = ['Por estado', 'Por puntuación', 'Por género', 'Por año']
    filter_idx = xbmcgui.Dialog().select('Filtrar por:', filter_options)
    
    if filter_idx == -1:
        return
    
    # Obtener anime según filtro
    if filter_idx == 0:  # Por estado
        statuses = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']
        status_idx = xbmcgui.Dialog().select('Estado:', statuses)
        if status_idx != -1:
            anime_list = local_database.get_local_anime_list(statuses[status_idx])
    else:
        anime_list = local_database.get_local_anime_list()
    
    if not anime_list:
        xbmcgui.Dialog().notification('Editor', 'No hay anime para editar')
        return
    
    # Operaciones masivas
    operations = ['Cambiar estado', 'Cambiar puntuación', 'Agregar tag', 'Eliminar seleccionados']
    op_idx = xbmcgui.Dialog().select('Operación masiva:', operations)
    
    if op_idx == 0:  # Cambiar estado
        new_statuses = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']
        new_status_idx = xbmcgui.Dialog().select('Nuevo estado:', new_statuses)
        
        if new_status_idx != -1:
            count = 0
            for anime in anime_list:
                local_database.update_anime_status(anime['mal_id'], new_statuses[new_status_idx])
                count += 1
            
            xbmcgui.Dialog().notification('Editor', f'{count} anime actualizados')

def theme_creator():
    """Creador visual de temas"""
    theme_options = [
        '🎨 Crear tema nuevo',
        '✏️ Editar tema existente',
        '👁️ Vista previa',
        '💾 Exportar tema',
        '📥 Importar tema'
    ]
    
    selected = xbmcgui.Dialog().select('Creador de Temas:', theme_options)
    
    if selected == 0:
        create_new_theme()
    elif selected == 1:
        edit_existing_theme()
    elif selected == 2:
        preview_theme()

def create_new_theme():
    """Crear nuevo tema personalizado"""
    # Nombre del tema
    theme_name = xbmcgui.Dialog().input('Nombre del tema:')
    if not theme_name:
        return
    
    # Configurar colores
    colors = {}
    color_options = ['Color primario', 'Color secundario', 'Color de fondo', 'Color de texto']
    
    for color_option in color_options:
        color_input = xbmcgui.Dialog().input(f'{color_option} (hex):')
        if color_input:
            colors[color_option.lower().replace(' ', '_')] = color_input
    
    # Configurar iconos
    icon_styles = ['default', 'minimal', 'kawaii', 'professional']
    icon_idx = xbmcgui.Dialog().select('Estilo de iconos:', icon_styles)
    
    # Crear tema
    custom_theme = {
        'name': theme_name,
        'colors': colors,
        'icon_style': icon_styles[icon_idx] if icon_idx != -1 else 'default',
        'created_at': int(time.time()),
        'author': 'Usuario'
    }
    
    # Guardar tema
    save_custom_theme(theme_name, custom_theme)
    xbmcgui.Dialog().notification('Temas', f'Tema creado: {theme_name}')

def report_generator():
    """Generador de reportes personalizados"""
    report_types = [
        '📊 Reporte estadístico',
        '📈 Reporte de progreso',
        '🎯 Reporte de géneros',
        '⭐ Reporte de puntuaciones',
        '📅 Reporte temporal',
        '🏆 Reporte de logros'
    ]
    
    selected = xbmcgui.Dialog().select('Tipo de Reporte:', report_types)
    
    if selected == 0:
        generate_stats_report()
    elif selected == 1:
        generate_progress_report()
    elif selected == 2:
        generate_genre_report()

def generate_stats_report():
    """Generar reporte estadístico personalizado"""
    stats = local_database.get_local_stats()
    
    # Configurar reporte
    include_options = [
        'Estadísticas básicas',
        'Distribución por estado',
        'Análisis de puntuaciones',
        'Tendencias temporales'
    ]
    
    selected_options = xbmcgui.Dialog().multiselect('Incluir en reporte:', include_options)
    
    if not selected_options:
        return
    
    # Generar reporte
    report = f"📊 REPORTE ESTADÍSTICO PERSONALIZADO\n"
    report += f"Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    if 0 in selected_options:  # Estadísticas básicas
        report += "📈 ESTADÍSTICAS BÁSICAS:\n"
        report += f"• Total de anime: {stats.get('total_anime', 0)}\n"
        report += f"• Completados: {stats.get('completed', 0)}\n"
        report += f"• Viendo: {stats.get('watching', 0)}\n"
        report += f"• Promedio: {stats.get('avg_score', 0)}/10\n\n"
    
    if 1 in selected_options:  # Distribución por estado
        report += "📊 DISTRIBUCIÓN POR ESTADO:\n"
        all_anime = local_database.get_local_anime_list()
        status_counts = {}
        
        for anime in all_anime:
            status = anime['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            percentage = (count / len(all_anime) * 100) if all_anime else 0
            report += f"• {status}: {count} ({percentage:.1f}%)\n"
        report += "\n"
    
    # Guardar reporte
    save_report(report, 'estadistico')
    
    # Mostrar reporte
    xbmcgui.Dialog().textviewer('Reporte Estadístico', report)

def api_exporter():
    """Exportador de API personalizada"""
    export_options = [
        '📋 Exportar lista completa',
        '🎯 Exportar por filtros',
        '📊 Exportar estadísticas',
        '🔧 Configurar API endpoints'
    ]
    
    selected = xbmcgui.Dialog().select('Exportar API:', export_options)
    
    if selected == 0:
        export_full_api()
    elif selected == 1:
        export_filtered_api()
    elif selected == 2:
        export_stats_api()

def export_full_api():
    """Exportar API completa"""
    try:
        anime_list = local_database.get_local_anime_list()
        stats = local_database.get_local_stats()
        
        api_data = {
            'api_version': '1.0',
            'generated_at': int(time.time()),
            'user_stats': stats,
            'anime_list': anime_list,
            'total_count': len(anime_list)
        }
        
        # Guardar API
        api_file = os.path.join(TOKEN_PATH, 'api_export.json')
        with open(api_file, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2, ensure_ascii=False)
        
        xbmcgui.Dialog().notification('API Export', f'API exportada: {api_file}')
        
    except Exception as e:
        xbmc.log(f'Creator Tools: API export error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('API Export', f'Error: {str(e)}')

def save_custom_theme(theme_name, theme_data):
    """Guardar tema personalizado"""
    try:
        themes_file = os.path.join(TOKEN_PATH, 'custom_themes.json')
        
        # Cargar temas existentes
        existing_themes = {}
        if os.path.exists(themes_file):
            with open(themes_file, 'r', encoding='utf-8') as f:
                existing_themes = json.load(f)
        
        # Agregar nuevo tema
        existing_themes[theme_name] = theme_data
        
        # Guardar
        with open(themes_file, 'w', encoding='utf-8') as f:
            json.dump(existing_themes, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        xbmc.log(f'Creator Tools: Save theme error - {str(e)}', xbmc.LOGERROR)

def save_report(report_content, report_type):
    """Guardar reporte generado"""
    try:
        timestamp = int(time.time())
        report_file = os.path.join(TOKEN_PATH, f'reporte_{report_type}_{timestamp}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        xbmc.log(f'Creator Tools: Report saved - {report_file}', xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f'Creator Tools: Save report error - {str(e)}', xbmc.LOGERROR)