import sqlite3
import json
import time
import calendar
from collections import Counter
from . import local_database
import xbmc
import xbmcgui

def get_viewing_analytics():
    """Obtener analytics de visualización"""
    try:
        conn = sqlite3.connect(local_database.DB_PATH)
        cursor = conn.cursor()
        
        # Tiempo total viendo anime (estimado)
        cursor.execute('SELECT SUM(episodes_watched * 24) FROM anime_list')
        total_minutes = cursor.fetchone()[0] or 0
        total_hours = round(total_minutes / 60, 1)
        total_days = round(total_hours / 24, 1)
        
        # Anime por década
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN year >= 2020 THEN '2020s'
                    WHEN year >= 2010 THEN '2010s'
                    WHEN year >= 2000 THEN '2000s'
                    WHEN year >= 1990 THEN '1990s'
                    ELSE 'Older'
                END as decade,
                COUNT(*) as count
            FROM anime_list 
            WHERE year > 0
            GROUP BY decade
            ORDER BY decade DESC
        ''')
        decades = dict(cursor.fetchall())
        
        # Top estudios
        cursor.execute('SELECT studios FROM anime_list WHERE studios IS NOT NULL')
        all_studios = []
        for row in cursor.fetchall():
            if row[0]:
                studios = json.loads(row[0])
                all_studios.extend(studios)
        
        top_studios = Counter(all_studios).most_common(5)
        
        # Progreso mensual (simulado)
        monthly_progress = get_monthly_progress()
        
        conn.close()
        
        return {
            'total_hours': total_hours,
            'total_days': total_days,
            'decades': decades,
            'top_studios': top_studios,
            'monthly_progress': monthly_progress
        }
        
    except Exception as e:
        xbmc.log(f'Analytics: Error - {str(e)}', xbmc.LOGERROR)
        return {}

def get_monthly_progress():
    """Obtener progreso mensual"""
    # Simulación de datos mensuales
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    progress = [5, 8, 12, 7, 15, 10]  # Anime completados por mes
    
    return dict(zip(months, progress))

def show_analytics_dashboard():
    """Mostrar dashboard de analytics"""
    analytics = get_viewing_analytics()
    
    info = "📊 DASHBOARD DE ANALYTICS\n\n"
    
    # Tiempo total
    info += f"⏱️ TIEMPO TOTAL VIENDO:\n"
    info += f"• {analytics.get('total_hours', 0)} horas\n"
    info += f"• {analytics.get('total_days', 0)} días\n\n"
    
    # Por década
    info += f"📅 ANIME POR DÉCADA:\n"
    for decade, count in analytics.get('decades', {}).items():
        info += f"• {decade}: {count} anime\n"
    info += "\n"
    
    # Top estudios
    info += f"🏢 TOP ESTUDIOS:\n"
    for studio, count in analytics.get('top_studios', [])[:3]:
        info += f"• {studio}: {count} anime\n"
    info += "\n"
    
    # Progreso mensual
    info += f"📈 PROGRESO MENSUAL:\n"
    for month, count in analytics.get('monthly_progress', {}).items():
        info += f"• {month}: {count} completados\n"
    
    xbmcgui.Dialog().textviewer('Analytics Dashboard', info)