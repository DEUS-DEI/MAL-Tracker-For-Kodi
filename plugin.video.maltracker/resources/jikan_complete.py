import requests
import xbmc
import time

class JikanComplete:
    BASE_URL = "https://api.jikan.moe/v4"
    
    @staticmethod
    def _request(endpoint, params=None):
        try:
            time.sleep(0.5)  # Rate limit
            url = f"{JikanComplete.BASE_URL}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    # ANIME - Todos los endpoints disponibles
    @staticmethod
    def get_anime_full(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/full")
    
    @staticmethod
    def get_anime_characters(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/characters")
    
    @staticmethod
    def get_anime_staff(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/staff")
    
    @staticmethod
    def get_anime_episodes(anime_id, page=1):
        return JikanComplete._request(f"anime/{anime_id}/episodes", {"page": page})
    
    @staticmethod
    def get_anime_episode(anime_id, episode):
        return JikanComplete._request(f"anime/{anime_id}/episodes/{episode}")
    
    @staticmethod
    def get_anime_news(anime_id, page=1):
        return JikanComplete._request(f"anime/{anime_id}/news", {"page": page})
    
    @staticmethod
    def get_anime_forum(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/forum")
    
    @staticmethod
    def get_anime_videos(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/videos")
    
    @staticmethod
    def get_anime_videos_episodes(anime_id, page=1):
        return JikanComplete._request(f"anime/{anime_id}/videos/episodes", {"page": page})
    
    @staticmethod
    def get_anime_pictures(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/pictures")
    
    @staticmethod
    def get_anime_statistics(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/statistics")
    
    @staticmethod
    def get_anime_moreinfo(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/moreinfo")
    
    @staticmethod
    def get_anime_recommendations(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/recommendations")
    
    @staticmethod
    def get_anime_userupdates(anime_id, page=1):
        return JikanComplete._request(f"anime/{anime_id}/userupdates", {"page": page})
    
    @staticmethod
    def get_anime_reviews(anime_id, page=1):
        return JikanComplete._request(f"anime/{anime_id}/reviews", {"page": page})
    
    @staticmethod
    def get_anime_relations(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/relations")
    
    @staticmethod
    def get_anime_themes(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/themes")
    
    @staticmethod
    def get_anime_external(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/external")
    
    @staticmethod
    def get_anime_streaming(anime_id):
        return JikanComplete._request(f"anime/{anime_id}/streaming")
    
    # CHARACTERS - Completo
    @staticmethod
    def get_character_full(character_id):
        return JikanComplete._request(f"characters/{character_id}/full")
    
    @staticmethod
    def get_character_anime(character_id):
        return JikanComplete._request(f"characters/{character_id}/anime")
    
    @staticmethod
    def get_character_manga(character_id):
        return JikanComplete._request(f"characters/{character_id}/manga")
    
    @staticmethod
    def get_character_voices(character_id):
        return JikanComplete._request(f"characters/{character_id}/voices")
    
    @staticmethod
    def get_character_pictures(character_id):
        return JikanComplete._request(f"characters/{character_id}/pictures")
    
    # CLUBS
    @staticmethod
    def get_clubs(page=1, q=None):
        params = {"page": page}
        if q: params["q"] = q
        return JikanComplete._request("clubs", params)
    
    @staticmethod
    def get_club(club_id):
        return JikanComplete._request(f"clubs/{club_id}")
    
    @staticmethod
    def get_club_members(club_id, page=1):
        return JikanComplete._request(f"clubs/{club_id}/members", {"page": page})
    
    @staticmethod
    def get_club_staff(club_id):
        return JikanComplete._request(f"clubs/{club_id}/staff")
    
    @staticmethod
    def get_club_relations(club_id):
        return JikanComplete._request(f"clubs/{club_id}/relations")
    
    # MAGAZINES
    @staticmethod
    def get_magazines(page=1, q=None):
        params = {"page": page}
        if q: params["q"] = q
        return JikanComplete._request("magazines", params)
    
    # MANGA - Completo
    @staticmethod
    def get_manga_full(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/full")
    
    @staticmethod
    def get_manga_characters(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/characters")
    
    @staticmethod
    def get_manga_news(manga_id, page=1):
        return JikanComplete._request(f"manga/{manga_id}/news", {"page": page})
    
    @staticmethod
    def get_manga_forum(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/forum")
    
    @staticmethod
    def get_manga_pictures(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/pictures")
    
    @staticmethod
    def get_manga_statistics(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/statistics")
    
    @staticmethod
    def get_manga_moreinfo(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/moreinfo")
    
    @staticmethod
    def get_manga_recommendations(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/recommendations")
    
    @staticmethod
    def get_manga_userupdates(manga_id, page=1):
        return JikanComplete._request(f"manga/{manga_id}/userupdates", {"page": page})
    
    @staticmethod
    def get_manga_reviews(manga_id, page=1):
        return JikanComplete._request(f"manga/{manga_id}/reviews", {"page": page})
    
    @staticmethod
    def get_manga_relations(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/relations")
    
    @staticmethod
    def get_manga_external(manga_id):
        return JikanComplete._request(f"manga/{manga_id}/external")
    
    # PEOPLE - Completo
    @staticmethod
    def get_person_full(person_id):
        return JikanComplete._request(f"people/{person_id}/full")
    
    @staticmethod
    def get_person_anime(person_id):
        return JikanComplete._request(f"people/{person_id}/anime")
    
    @staticmethod
    def get_person_voices(person_id):
        return JikanComplete._request(f"people/{person_id}/voices")
    
    @staticmethod
    def get_person_manga(person_id):
        return JikanComplete._request(f"people/{person_id}/manga")
    
    @staticmethod
    def get_person_pictures(person_id):
        return JikanComplete._request(f"people/{person_id}/pictures")
    
    # PRODUCERS
    @staticmethod
    def get_producers(page=1, q=None):
        params = {"page": page}
        if q: params["q"] = q
        return JikanComplete._request("producers", params)
    
    @staticmethod
    def get_producer_full(producer_id):
        return JikanComplete._request(f"producers/{producer_id}/full")
    
    @staticmethod
    def get_producer_external(producer_id):
        return JikanComplete._request(f"producers/{producer_id}/external")
    
    # RANDOM
    @staticmethod
    def get_random_anime():
        return JikanComplete._request("random/anime")
    
    @staticmethod
    def get_random_manga():
        return JikanComplete._request("random/manga")
    
    @staticmethod
    def get_random_characters():
        return JikanComplete._request("random/characters")
    
    @staticmethod
    def get_random_people():
        return JikanComplete._request("random/people")
    
    @staticmethod
    def get_random_users():
        return JikanComplete._request("random/users")
    
    # RECOMMENDATIONS
    @staticmethod
    def get_recent_anime_recommendations(page=1):
        return JikanComplete._request("recommendations/anime", {"page": page})
    
    @staticmethod
    def get_recent_manga_recommendations(page=1):
        return JikanComplete._request("recommendations/manga", {"page": page})
    
    # REVIEWS
    @staticmethod
    def get_recent_anime_reviews(page=1):
        return JikanComplete._request("reviews/anime", {"page": page})
    
    @staticmethod
    def get_recent_manga_reviews(page=1):
        return JikanComplete._request("reviews/manga", {"page": page})
    
    # SCHEDULES
    @staticmethod
    def get_schedules(filter=None, kids=None, sfw=None, unapproved=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if filter: params["filter"] = filter
        if kids is not None: params["kids"] = kids
        if sfw is not None: params["sfw"] = sfw
        if unapproved is not None: params["unapproved"] = unapproved
        return JikanComplete._request("schedules", params)
    
    # SEASONS
    @staticmethod
    def get_seasons_list():
        return JikanComplete._request("seasons")
    
    @staticmethod
    def get_season_now(filter=None, sfw=None, unapproved=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if filter: params["filter"] = filter
        if sfw is not None: params["sfw"] = sfw
        if unapproved is not None: params["unapproved"] = unapproved
        return JikanComplete._request("seasons/now", params)
    
    @staticmethod
    def get_season_upcoming(filter=None, sfw=None, unapproved=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if filter: params["filter"] = filter
        if sfw is not None: params["sfw"] = sfw
        if unapproved is not None: params["unapproved"] = unapproved
        return JikanComplete._request("seasons/upcoming", params)
    
    @staticmethod
    def get_season(year, season, filter=None, sfw=None, unapproved=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if filter: params["filter"] = filter
        if sfw is not None: params["sfw"] = sfw
        if unapproved is not None: params["unapproved"] = unapproved
        return JikanComplete._request(f"seasons/{year}/{season}", params)
    
    # TOP
    @staticmethod
    def get_top_anime(type=None, filter=None, rating=None, sfw=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if type: params["type"] = type
        if filter: params["filter"] = filter
        if rating: params["rating"] = rating
        if sfw is not None: params["sfw"] = sfw
        return JikanComplete._request("top/anime", params)
    
    @staticmethod
    def get_top_manga(type=None, filter=None, sfw=None, page=1, limit=25):
        params = {"page": page, "limit": limit}
        if type: params["type"] = type
        if filter: params["filter"] = filter
        if sfw is not None: params["sfw"] = sfw
        return JikanComplete._request("top/manga", params)
    
    @staticmethod
    def get_top_people(page=1, limit=25):
        return JikanComplete._request("top/people", {"page": page, "limit": limit})
    
    @staticmethod
    def get_top_characters(page=1, limit=25):
        return JikanComplete._request("top/characters", {"page": page, "limit": limit})
    
    @staticmethod
    def get_top_reviews(page=1, limit=25):
        return JikanComplete._request("top/reviews", {"page": page, "limit": limit})
    
    # USERS
    @staticmethod
    def get_user_profile(username):
        return JikanComplete._request(f"users/{username}")
    
    @staticmethod
    def get_user_statistics(username):
        return JikanComplete._request(f"users/{username}/statistics")
    
    @staticmethod
    def get_user_favorites(username):
        return JikanComplete._request(f"users/{username}/favorites")
    
    @staticmethod
    def get_user_updates(username):
        return JikanComplete._request(f"users/{username}/userupdates")
    
    @staticmethod
    def get_user_about(username):
        return JikanComplete._request(f"users/{username}/about")
    
    @staticmethod
    def get_user_history(username, type=None):
        params = {}
        if type: params["type"] = type
        return JikanComplete._request(f"users/{username}/history", params)
    
    @staticmethod
    def get_user_friends(username, page=1):
        return JikanComplete._request(f"users/{username}/friends", {"page": page})
    
    @staticmethod
    def get_user_animelist(username, status=None, page=1):
        params = {"page": page}
        if status: params["status"] = status
        return JikanComplete._request(f"users/{username}/animelist", params)
    
    @staticmethod
    def get_user_mangalist(username, status=None, page=1):
        params = {"page": page}
        if status: params["status"] = status
        return JikanComplete._request(f"users/{username}/mangalist", params)
    
    @staticmethod
    def get_user_reviews(username, page=1):
        return JikanComplete._request(f"users/{username}/reviews", {"page": page})
    
    @staticmethod
    def get_user_recommendations(username, page=1):
        return JikanComplete._request(f"users/{username}/recommendations", {"page": page})
    
    @staticmethod
    def get_user_clubs(username, page=1):
        return JikanComplete._request(f"users/{username}/clubs", {"page": page})
    
    @staticmethod
    def get_user_external(username):
        return JikanComplete._request(f"users/{username}/external")
    
    # WATCH
    @staticmethod
    def get_watch_recent_episodes(page=1, limit=25):
        return JikanComplete._request("watch/episodes", {"page": page, "limit": limit})
    
    @staticmethod
    def get_watch_recent_promos(page=1, limit=25):
        return JikanComplete._request("watch/promos", {"page": page, "limit": limit})
    
    @staticmethod
    def get_watch_popular_episodes(page=1, limit=25):
        return JikanComplete._request("watch/episodes/popular", {"page": page, "limit": limit})
    
    @staticmethod
    def get_watch_popular_promos(page=1, limit=25):
        return JikanComplete._request("watch/promos/popular", {"page": page, "limit": limit})