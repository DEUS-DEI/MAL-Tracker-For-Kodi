import requests
import json
import xbmc
import xbmcgui
from .config import USER_AGENT, rate_limit

class APIAnalysis:
    
    @staticmethod
    def analyze_jikan_api_coverage():
        """Analizar cobertura de Jikan API"""
        
        # Funciones IMPLEMENTADAS
        implemented = {
            'basic': [
                'GET /anime/{id}',           # ✅ get_anime_details_public()
                'GET /anime',                # ✅ search_anime_public()
                'GET /top/anime',            # ✅ get_top_anime_public()
                'GET /seasons/now',          # ✅ get_seasonal_anime_public()
                'GET /seasons/upcoming',     # ✅ get_upcoming_anime_public()
                'GET /schedules',            # ✅ get_schedule_public()
            ],
            'intermediate': [
                'GET /schedules/{day}',      # ✅ get_schedule_public(day)
                'GET /seasons/{year}/{season}', # ✅ search_by_year()
                'GET /producers',            # ✅ search_by_studio()
            ],
            'advanced': [
                # ❌ NO IMPLEMENTADAS
            ]
        }
        
        # Funciones NO IMPLEMENTADAS (Oportunidades)
        missing = {
            'basic_missing': [
                'GET /anime/{id}/characters',
                'GET /anime/{id}/staff', 
                'GET /anime/{id}/episodes',
                'GET /anime/{id}/news',
                'GET /anime/{id}/forum',
                'GET /anime/{id}/videos',
                'GET /anime/{id}/pictures',
                'GET /anime/{id}/statistics',
                'GET /anime/{id}/moreinfo',
                'GET /anime/{id}/recommendations',
                'GET /anime/{id}/userupdates',
                'GET /anime/{id}/reviews'
            ],
            'intermediate_missing': [
                'GET /characters/{id}',
                'GET /people/{id}',
                'GET /magazines',
                'GET /genres/anime',
                'GET /producers/{id}',
                'GET /clubs',
                'GET /users/{username}',
                'GET /random/anime'
            ],
            'advanced_missing': [
                'GET /anime/{id}/relations',
                'GET /anime/{id}/themes',
                'GET /anime/{id}/external',
                'GET /anime/{id}/streaming',
                'GET /seasons/{year}',
                'GET /seasons/archive',
                'GET /watch/episodes',
                'GET /watch/promos'
            ]
        }
        
        return {
            'implemented': implemented,
            'missing': missing,
            'coverage_basic': len(implemented['basic']) / (len(implemented['basic']) + len(missing['basic_missing'])) * 100,
            'coverage_intermediate': len(implemented['intermediate']) / (len(implemented['intermediate']) + len(missing['intermediate_missing'])) * 100,
            'coverage_advanced': 0  # No hay funciones avanzadas implementadas
        }
    
    @staticmethod
    def get_missing_api_functions():
        """Obtener funciones de API faltantes más importantes"""
        return [
            {
                'endpoint': '/anime/{id}/characters',
                'description': 'Personajes del anime',
                'priority': 'high',
                'complexity': 'basic'
            },
            {
                'endpoint': '/anime/{id}/staff',
                'description': 'Staff del anime (director, estudio)',
                'priority': 'high', 
                'complexity': 'basic'
            },
            {
                'endpoint': '/anime/{id}/episodes',
                'description': 'Lista de episodios',
                'priority': 'high',
                'complexity': 'intermediate'
            },
            {
                'endpoint': '/anime/{id}/reviews',
                'description': 'Reviews de usuarios',
                'priority': 'medium',
                'complexity': 'intermediate'
            },
            {
                'endpoint': '/anime/{id}/recommendations',
                'description': 'Recomendaciones relacionadas',
                'priority': 'high',
                'complexity': 'intermediate'
            },
            {
                'endpoint': '/anime/{id}/themes',
                'description': 'Temas musicales (OP/ED)',
                'priority': 'medium',
                'complexity': 'advanced'
            },
            {
                'endpoint': '/anime/{id}/streaming',
                'description': 'Plataformas de streaming',
                'priority': 'high',
                'complexity': 'advanced'
            },
            {
                'endpoint': '/random/anime',
                'description': 'Anime aleatorio',
                'priority': 'low',
                'complexity': 'basic'
            }
        ]

def show_api_coverage_report():
    """Mostrar reporte de cobertura de APIs"""
    analysis = APIAnalysis.analyze_jikan_api_coverage()
    
    report = "📊 ANÁLISIS DE COBERTURA DE APIs\n\n"
    
    # Cobertura actual
    report += "📈 COBERTURA ACTUAL:\n"
    report += f"• Funciones Básicas: {analysis['coverage_basic']:.1f}%\n"
    report += f"• Funciones Intermedias: {analysis['coverage_intermediate']:.1f}%\n" 
    report += f"• Funciones Avanzadas: {analysis['coverage_advanced']:.1f}%\n\n"
    
    # Funciones implementadas
    report += "✅ FUNCIONES IMPLEMENTADAS:\n"
    for category, functions in analysis['implemented'].items():
        if functions:
            report += f"\n{category.upper()}:\n"
            for func in functions:
                report += f"  • {func}\n"
    
    # Funciones faltantes críticas
    missing_functions = APIAnalysis.get_missing_api_functions()
    high_priority = [f for f in missing_functions if f['priority'] == 'high']
    
    report += f"\n❌ FUNCIONES FALTANTES CRÍTICAS ({len(high_priority)}):\n"
    for func in high_priority:
        report += f"• {func['endpoint']} - {func['description']}\n"
    
    # Recomendaciones
    report += "\n💡 RECOMENDACIONES:\n"
    report += "1. Implementar funciones de personajes y staff\n"
    report += "2. Agregar lista de episodios detallada\n"
    report += "3. Integrar recomendaciones de la API\n"
    report += "4. Implementar información de streaming\n"
    
    xbmcgui.Dialog().textviewer('Cobertura de APIs', report)

def implement_missing_critical_functions():
    """Implementar funciones críticas faltantes"""
    try:
        progress = xbmcgui.DialogProgress()
        progress.create('Implementando APIs', 'Agregando funciones faltantes...')
        
        # 1. Personajes del anime
        progress.update(20, 'Implementando personajes...')
        implement_characters_api()
        
        # 2. Staff del anime  
        progress.update(40, 'Implementando staff...')
        implement_staff_api()
        
        # 3. Lista de episodios
        progress.update(60, 'Implementando episodios...')
        implement_episodes_api()
        
        # 4. Recomendaciones
        progress.update(80, 'Implementando recomendaciones...')
        implement_recommendations_api()
        
        progress.update(100, 'Completado')
        progress.close()
        
        xbmcgui.Dialog().notification('APIs', '✅ Funciones críticas implementadas')
        
    except Exception as e:
        if 'progress' in locals():
            progress.close()
        xbmc.log(f'API Implementation: Error - {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('APIs', f'❌ Error: {str(e)}')

def implement_characters_api():
    """Implementar API de personajes"""
    def get_anime_characters(anime_id):
        """Obtener personajes de un anime"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/characters"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Characters API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    # Agregar función al módulo public_api
    import sys
    from . import public_api
    public_api.get_anime_characters = get_anime_characters

def implement_staff_api():
    """Implementar API de staff"""
    def get_anime_staff(anime_id):
        """Obtener staff de un anime"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/staff"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Staff API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    from . import public_api
    public_api.get_anime_staff = get_anime_staff

def implement_episodes_api():
    """Implementar API de episodios"""
    def get_anime_episodes(anime_id, page=1):
        """Obtener episodios de un anime"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/episodes"
            params = {'page': page}
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Episodes API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    from . import public_api
    public_api.get_anime_episodes = get_anime_episodes

def implement_recommendations_api():
    """Implementar API de recomendaciones"""
    def get_anime_recommendations(anime_id):
        """Obtener recomendaciones de un anime"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/recommendations"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Recommendations API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    from . import public_api
    public_api.get_anime_recommendations = get_anime_recommendations

def implement_advanced_api_functions():
    """Implementar funciones avanzadas de API"""
    
    def get_anime_themes(anime_id):
        """Obtener temas musicales (OP/ED)"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/themes"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Themes API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def get_anime_streaming(anime_id):
        """Obtener plataformas de streaming"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/streaming"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Streaming API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    def get_random_anime():
        """Obtener anime aleatorio"""
        try:
            rate_limit()
            url = f"https://api.jikan.moe/v4/random/anime"
            headers = {'User-Agent': USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            xbmc.log(f'Random API: Error - {str(e)}', xbmc.LOGERROR)
            return None
    
    # Agregar funciones al módulo
    from . import public_api
    public_api.get_anime_themes = get_anime_themes
    public_api.get_anime_streaming = get_anime_streaming
    public_api.get_random_anime = get_random_anime

def show_api_functions_menu():
    """Mostrar menú de funciones de API"""
    options = [
        '📊 Ver cobertura actual',
        '🔧 Implementar funciones críticas',
        '⚡ Implementar funciones avanzadas',
        '🎲 Probar función aleatoria',
        '📋 Lista completa de endpoints'
    ]
    
    selected = xbmcgui.Dialog().select('Funciones de API:', options)
    
    if selected == 0:
        show_api_coverage_report()
    elif selected == 1:
        implement_missing_critical_functions()
    elif selected == 2:
        implement_advanced_api_functions()
        xbmcgui.Dialog().notification('APIs', '✅ Funciones avanzadas implementadas')
    elif selected == 3:
        test_random_function()
    elif selected == 4:
        show_complete_endpoint_list()

def test_random_function():
    """Probar función aleatoria"""
    try:
        implement_advanced_api_functions()
        from . import public_api
        
        if hasattr(public_api, 'get_random_anime'):
            result = public_api.get_random_anime()
            if result and 'data' in result:
                anime = result['data']
                title = anime.get('title', 'Sin título')
                score = anime.get('score', 'N/A')
                
                xbmcgui.Dialog().notification(
                    'Anime Aleatorio',
                    f'{title} ({score}/10)',
                    time=5000
                )
            else:
                xbmcgui.Dialog().notification('API', 'Error obteniendo anime aleatorio')
        else:
            xbmcgui.Dialog().notification('API', 'Función no implementada')
            
    except Exception as e:
        xbmcgui.Dialog().notification('API', f'Error: {str(e)}')

def show_complete_endpoint_list():
    """Mostrar lista completa de endpoints"""
    endpoints = """📋 ENDPOINTS COMPLETOS DE JIKAN API

✅ IMPLEMENTADOS:
• GET /anime/{id} - Detalles del anime
• GET /anime - Búsqueda de anime  
• GET /top/anime - Top anime
• GET /seasons/now - Temporada actual
• GET /seasons/upcoming - Próximos estrenos
• GET /schedules - Calendario de emisiones
• GET /schedules/{day} - Calendario por día
• GET /producers - Búsqueda de estudios

❌ NO IMPLEMENTADOS:
• GET /anime/{id}/characters - Personajes
• GET /anime/{id}/staff - Staff y crew
• GET /anime/{id}/episodes - Lista de episodios
• GET /anime/{id}/news - Noticias
• GET /anime/{id}/forum - Discusiones
• GET /anime/{id}/videos - Videos y trailers
• GET /anime/{id}/pictures - Imágenes
• GET /anime/{id}/statistics - Estadísticas
• GET /anime/{id}/recommendations - Recomendaciones
• GET /anime/{id}/reviews - Reviews
• GET /anime/{id}/themes - Temas musicales
• GET /anime/{id}/streaming - Plataformas
• GET /random/anime - Anime aleatorio
• GET /characters/{id} - Detalles de personaje
• GET /people/{id} - Detalles de persona
• GET /genres/anime - Lista de géneros

TOTAL: 8/24 endpoints implementados (33%)"""
    
    xbmcgui.Dialog().textviewer('Endpoints Completos', endpoints)