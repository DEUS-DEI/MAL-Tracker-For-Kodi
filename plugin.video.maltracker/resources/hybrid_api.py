"""
Sistema híbrido MAL + AniList
AniList como principal, MAL como fallback
"""

import requests
import json
import xbmc
import xbmcgui
from .config import rate_limit, USER_AGENT
from . import anilist_auth, auth as mal_auth

class HybridAPI:
    
    @staticmethod
    def get_primary_service():
        """Determinar servicio principal basado en tokens disponibles"""
        anilist_token = anilist_auth.load_access_token()
        mal_token = mal_auth.load_access_token()
        
        # Prioridad: AniList > MAL
        if anilist_token:
            return 'anilist'
        elif mal_token:
            return 'mal'
        else:
            return None
    
    @staticmethod
    def search_anime(query, limit=20):
        """Búsqueda híbrida con fallback"""
        primary = HybridAPI.get_primary_service()
        
        if primary == 'anilist':
            result = HybridAPI._search_anilist(query, limit)
            if result:
                return result
            # Fallback a MAL
            xbmc.log('Hybrid API: AniList failed, trying MAL', xbmc.LOGINFO)
            return HybridAPI._search_mal(query, limit)
        
        elif primary == 'mal':
            result = HybridAPI._search_mal(query, limit)
            if result:
                return result
            # Fallback a AniList
            xbmc.log('Hybrid API: MAL failed, trying AniList', xbmc.LOGINFO)
            return HybridAPI._search_anilist(query, limit)
        
        else:
            xbmcgui.Dialog().notification('Hybrid API', 'No hay servicios autenticados')
            return None
    
    @staticmethod
    def _search_anilist(query, limit):
        """Búsqueda en AniList usando GraphQL"""
        try:
            token = anilist_auth.load_access_token()
            if not token:
                return None
            
            graphql_query = """
            query ($search: String, $perPage: Int) {
                Page(page: 1, perPage: $perPage) {
                    media(search: $search, type: ANIME) {
                        id
                        title { romaji english native }
                        coverImage { medium large }
                        averageScore
                        episodes
                        status
                        genres
                        description
                        startDate { year month day }
                    }
                }
            }
            """
            
            variables = {'search': query, 'perPage': limit}
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                'https://graphql.anilist.co',
                json={'query': graphql_query, 'variables': variables},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return HybridAPI._normalize_anilist_data(data)
            
        except Exception as e:
            xbmc.log(f'Hybrid API: AniList search error - {str(e)}', xbmc.LOGERROR)
        
        return None
    
    @staticmethod
    def _search_mal(query, limit):
        """Búsqueda en MAL usando REST"""
        try:
            token = mal_auth.load_access_token()
            if not token:
                return None
            
            headers = {
                'Authorization': f'Bearer {token}',
                'User-Agent': USER_AGENT
            }
            
            params = {
                'q': query,
                'limit': limit,
                'fields': 'id,title,main_picture,mean,num_episodes,status,genres'
            }
            
            rate_limit()
            response = requests.get(
                'https://api.myanimelist.net/v2/anime',
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return HybridAPI._normalize_mal_data(data)
                
        except Exception as e:
            xbmc.log(f'Hybrid API: MAL search error - {str(e)}', xbmc.LOGERROR)
        
        return None
    
    @staticmethod
    def _normalize_anilist_data(data):
        """Normalizar datos de AniList al formato común"""
        normalized = {'data': []}
        
        try:
            media_list = data.get('data', {}).get('Page', {}).get('media', [])
            
            for anime in media_list:
                title = anime.get('title', {})
                normalized_anime = {
                    'id': anime.get('id'),
                    'title': title.get('romaji') or title.get('english') or title.get('native', 'Sin título'),
                    'image_url': anime.get('coverImage', {}).get('medium', ''),
                    'score': anime.get('averageScore', 0) / 10 if anime.get('averageScore') else 0,
                    'episodes': anime.get('episodes', 0),
                    'status': anime.get('status', ''),
                    'genres': anime.get('genres', []),
                    'description': anime.get('description', ''),
                    'source': 'anilist'
                }
                normalized['data'].append(normalized_anime)
                
        except Exception as e:
            xbmc.log(f'Hybrid API: AniList normalization error - {str(e)}', xbmc.LOGERROR)
        
        return normalized
    
    @staticmethod
    def _normalize_mal_data(data):
        """Normalizar datos de MAL al formato común"""
        normalized = {'data': []}
        
        try:
            for entry in data.get('data', []):
                anime = entry.get('node', {})
                normalized_anime = {
                    'id': anime.get('id'),
                    'title': anime.get('title', 'Sin título'),
                    'image_url': anime.get('main_picture', {}).get('medium', ''),
                    'score': anime.get('mean', 0),
                    'episodes': anime.get('num_episodes', 0),
                    'status': anime.get('status', ''),
                    'genres': [g.get('name', '') for g in anime.get('genres', [])],
                    'description': '',
                    'source': 'mal'
                }
                normalized['data'].append(normalized_anime)
                
        except Exception as e:
            xbmc.log(f'Hybrid API: MAL normalization error - {str(e)}', xbmc.LOGERROR)
        
        return normalized
    
    @staticmethod
    def get_user_anime_list():
        """Obtener lista de usuario con fallback"""
        primary = HybridAPI.get_primary_service()
        
        if primary == 'anilist':
            result = HybridAPI._get_anilist_list()
            if result:
                return result
            return HybridAPI._get_mal_list()
        
        elif primary == 'mal':
            result = HybridAPI._get_mal_list()
            if result:
                return result
            return HybridAPI._get_anilist_list()
        
        return None
    
    @staticmethod
    def _get_anilist_list():
        """Obtener lista de AniList"""
        try:
            token = anilist_auth.load_access_token()
            if not token:
                return None
            
            graphql_query = """
            query {
                Viewer {
                    mediaListOptions { scoreFormat }
                }
                MediaListCollection(userId: null, type: ANIME) {
                    lists {
                        name
                        entries {
                            id
                            status
                            score
                            progress
                            media {
                                id
                                title { romaji english }
                                coverImage { medium }
                                episodes
                                averageScore
                            }
                        }
                    }
                }
            }
            """
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://graphql.anilist.co',
                json={'query': graphql_query},
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            xbmc.log(f'Hybrid API: AniList list error - {str(e)}', xbmc.LOGERROR)
        
        return None
    
    @staticmethod
    def _get_mal_list():
        """Obtener lista de MAL"""
        try:
            from . import mal_api
            return mal_api.get_user_anime_list()
        except Exception as e:
            xbmc.log(f'Hybrid API: MAL list error - {str(e)}', xbmc.LOGERROR)
            return None
    
    @staticmethod
    def show_service_status():
        """Mostrar estado de servicios"""
        anilist_token = anilist_auth.load_access_token()
        mal_token = mal_auth.load_access_token()
        primary = HybridAPI.get_primary_service()
        
        status = f"""ESTADO DE SERVICIOS:

🔵 AniList: {'✅ Conectado' if anilist_token else '❌ No autenticado'}
🔴 MyAnimeList: {'✅ Conectado' if mal_token else '❌ No autenticado'}

📡 Servicio principal: {primary.upper() if primary else 'Ninguno'}

CONFIGURACIÓN RECOMENDADA:
• AniList como principal (API superior)
• MAL como backup (mayor base de datos)
• Sincronización cruzada activada

VENTAJAS ACTUALES:
• Búsqueda con fallback automático
• Lista híbrida combinada
• Mayor disponibilidad del servicio"""
        
        xbmcgui.Dialog().textviewer('Estado de Servicios', status)