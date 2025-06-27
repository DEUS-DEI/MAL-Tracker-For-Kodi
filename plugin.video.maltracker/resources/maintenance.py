import os
import sqlite3
import json
import time
import xbmc
import xbmcgui
from . import local_database
from .config import TOKEN_PATH

def show_maintenance_menu():
    """Mostrar menú de mantenimiento"""
    options = [
        '🔧 Reparar base de datos',
        '🧹 Limpiar datos huérfanos',
        '📊 Verificar integridad',
        '🗑️ Limpiar caché',
        '📈 Optimizar rendimiento',
        '🔄 Reconstruir índices',
        '📋 Generar reporte de salud'
    ]
    
    selected = xbmcgui.Dialog().select('Herramientas de Mantenimiento:', options)
    
    if selected == 0:
        repair_database()
    elif selected == 1:
        clean_orphaned_data()
    elif selected == 2:
        verify_integrity()
    elif selected == 3:
        clean_cache()
    elif selected == 4:
        optimize_performance()
    elif selected == 5:
        rebuild_indexes()
    elif selected == 6:
        generate_health_report()

def repair_database():
    """Reparar base de datos"""
    try:
        progress = xbmcgui.DialogProgress()
        progress.create('Reparando Base de Datos', 'Verificando estructura...')
        
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Verificar y reparar estructura
        progress.update(25, 'Verificando tablas...')
        
        # Verificar tabla principal
        cursor.execute("PRAGMA table_info(anime_list)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['mal_id', 'title', 'status', 'episodes_watched', 'synced']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            progress.update(50, 'Agregando columnas faltantes...')
            for col in missing_columns:
                if col == 'synced':
                    cursor.execute('ALTER TABLE anime_list ADD COLUMN synced INTEGER DEFAULT 0')
        
        # Limpiar datos corruptos
        progress.update(75, 'Limpiando datos corruptos...')
        cursor.execute('DELETE FROM anime_list WHERE mal_id IS NULL OR title IS NULL')
        
        # Verificar integridad
        progress.update(90, 'Verificando integridad...')
        cursor.execute('PRAGMA integrity_check')
        integrity_result = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        progress.update(100, 'Reparación completada')
        progress.close()
        
        if integrity_result == 'ok':
            xbmcgui.Dialog().notification('Mantenimiento', 'Base de datos reparada exitosamente')
        else:
            xbmcgui.Dialog().notification('Mantenimiento', f'Advertencia: {integrity_result}')
        
    except Exception as e:
        if 'progress' in locals():
            progress.close()
        xbmc.log(f'Maintenance: Repair database error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def clean_orphaned_data():
    """Limpiar datos huérfanos"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Limpiar registros duplicados
        cursor.execute('''
            DELETE FROM anime_list 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) 
                FROM anime_list 
                GROUP BY mal_id
            )
        ''')
        duplicates_removed = cursor.rowcount
        
        # Limpiar registros con datos inválidos
        cursor.execute('DELETE FROM anime_list WHERE episodes_watched < 0')
        invalid_episodes = cursor.rowcount
        
        cursor.execute('DELETE FROM anime_list WHERE score < 0 OR score > 10')
        invalid_scores = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        message = f'Limpieza completada:\n'
        message += f'• Duplicados: {duplicates_removed}\n'
        message += f'• Episodios inválidos: {invalid_episodes}\n'
        message += f'• Puntuaciones inválidas: {invalid_scores}'
        
        xbmcgui.Dialog().ok('Limpieza de Datos', message)
        
    except Exception as e:
        xbmc.log(f'Maintenance: Clean orphaned data error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def verify_integrity():
    """Verificar integridad de datos"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        issues = []
        
        # Verificar IDs únicos
        cursor.execute('SELECT mal_id, COUNT(*) FROM anime_list GROUP BY mal_id HAVING COUNT(*) > 1')
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f'IDs duplicados: {len(duplicates)}')
        
        # Verificar datos faltantes
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE title IS NULL OR title = ""')
        missing_titles = cursor.fetchone()[0]
        if missing_titles:
            issues.append(f'Títulos faltantes: {missing_titles}')
        
        # Verificar rangos válidos
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE score < 0 OR score > 10')
        invalid_scores = cursor.fetchone()[0]
        if invalid_scores:
            issues.append(f'Puntuaciones inválidas: {invalid_scores}')
        
        conn.close()
        
        if issues:
            message = 'Problemas encontrados:\n' + '\n'.join(f'• {issue}' for issue in issues)
            message += '\n\n¿Ejecutar reparación automática?'
            
            if xbmcgui.Dialog().yesno('Verificación de Integridad', message):
                repair_database()
        else:
            xbmcgui.Dialog().notification('Verificación', 'Base de datos íntegra')
        
    except Exception as e:
        xbmc.log(f'Maintenance: Verify integrity error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def clean_cache():
    """Limpiar archivos de caché"""
    try:
        cache_files = ['notifications.json', 'themes.json', 'layout.json']
        cleaned = 0
        
        for cache_file in cache_files:
            cache_path = os.path.join(TOKEN_PATH, f'{cache_file}.cache')
            if os.path.exists(cache_path):
                os.remove(cache_path)
                cleaned += 1
        
        xbmcgui.Dialog().notification('Mantenimiento', f'Caché limpiado: {cleaned} archivos')
        
    except Exception as e:
        xbmc.log(f'Maintenance: Clean cache error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def optimize_performance():
    """Optimizar rendimiento de la base de datos"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # VACUUM para compactar
        cursor.execute('VACUUM')
        
        # ANALYZE para optimizar consultas
        cursor.execute('ANALYZE')
        
        conn.close()
        
        xbmcgui.Dialog().notification('Mantenimiento', 'Rendimiento optimizado')
        
    except Exception as e:
        xbmc.log(f'Maintenance: Optimize performance error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def rebuild_indexes():
    """Reconstruir índices de base de datos"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Crear índices para mejorar rendimiento
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_mal_id ON anime_list(mal_id)',
            'CREATE INDEX IF NOT EXISTS idx_status ON anime_list(status)',
            'CREATE INDEX IF NOT EXISTS idx_score ON anime_list(score)',
            'CREATE INDEX IF NOT EXISTS idx_updated ON anime_list(updated_date)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        xbmcgui.Dialog().notification('Mantenimiento', 'Índices reconstruidos')
        
    except Exception as e:
        xbmc.log(f'Maintenance: Rebuild indexes error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')

def generate_health_report():
    """Generar reporte de salud del sistema"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Estadísticas de la base de datos
        cursor.execute('SELECT COUNT(*) FROM anime_list')
        total_anime = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM anime_list WHERE synced = 1')
        synced_anime = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT status) FROM anime_list')
        unique_statuses = cursor.fetchone()[0]
        
        # Tamaño de archivos
        db_size = os.path.getsize(local_database.DB_PATH) / 1024  # KB
        
        # Archivos de configuración
        config_files = ['token.json', 'notifications.json', 'themes.json']
        config_status = []
        
        for config_file in config_files:
            config_path = os.path.join(TOKEN_PATH, config_file)
            exists = os.path.exists(config_path)
            config_status.append(f"{config_file}: {'✓' if exists else '✗'}")
        
        conn.close()
        
        # Generar reporte
        report = "🏥 REPORTE DE SALUD DEL SISTEMA\n\n"
        report += f"📊 ESTADÍSTICAS:\n"
        report += f"• Total de anime: {total_anime}\n"
        report += f"• Anime sincronizado: {synced_anime}\n"
        report += f"• Estados únicos: {unique_statuses}\n"
        report += f"• Tamaño BD: {db_size:.1f} KB\n\n"
        
        report += f"⚙️ ARCHIVOS DE CONFIGURACIÓN:\n"
        for status in config_status:
            report += f"• {status}\n"
        
        report += f"\n🕐 Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        xbmcgui.Dialog().textviewer('Reporte de Salud', report)
        
    except Exception as e:
        xbmc.log(f'Maintenance: Health report error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Mantenimiento', f'Error: {str(e)}')