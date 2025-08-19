# -*- coding: utf-8 -*-
from resources.lib.utils import get_current_date, get_dates, years_tvshows
from resources.lib.autotranslate import AutoTranslate
from kodi_helper import requests
import xbmcaddon
import xbmcvfs
import os
import time
import hashlib
import json
from urllib.parse import quote

addon = xbmcaddon.Addon()
TRANSLATE = xbmcvfs.translatePath
profile_dir = TRANSLATE(addon.getAddonInfo('profile'))
cache_dir = os.path.join(profile_dir, 'cache')
if not xbmcvfs.exists(cache_dir):
    xbmcvfs.mkdirs(cache_dir)

API_KEY = '92c1507cc18d85290e7a0b96abb37316' #zoreu
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

def get_json(url, ttl=3600):
    # Auto-delete old cache files
    try:
        cache_ttl_days = int(addon.getSetting('cache_ttl_days') or '7')
        files = xbmcvfs.listdir(cache_dir)[1]

        # Caso o usuário configure "0 dias", limpa todo o cache imediatamente
        if cache_ttl_days == 0:
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(cache_dir, file)
                    try:
                        xbmcvfs.delete(file_path)
                    except:
                        pass

        # Caso seja maior que 0, aplica limpeza por tempo de vida
        elif cache_ttl_days > 0:
            cache_ttl_seconds = cache_ttl_days * 86400
            current_time = time.time()
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(cache_dir, file)
                    try:
                        with xbmcvfs.File(file_path, 'r') as f:
                            cached = json.load(f)
                        if current_time - cached['timestamp'] > cache_ttl_seconds:
                            xbmcvfs.delete(file_path)
                    except:
                        xbmcvfs.delete(file_path)  # Delete corrompidos
    except:
        pass

    hash_val = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, hash_val + '.json')
    if xbmcvfs.exists(cache_file):
        try:
            with xbmcvfs.File(cache_file, 'r') as f:
                cached = json.load(f)
            if time.time() - cached['timestamp'] < ttl:
                return cached['data']
        except:
            pass
    try:
        r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=5)
        r.raise_for_status()
        data = r.json()
        with xbmcvfs.File(cache_file, 'w') as f:
            json.dump({'data': data, 'timestamp': time.time()}, f)
        return data
    except:
        return {}

def get_cache_size():
    total_size = 0
    if xbmcvfs.exists(cache_dir):
        files = xbmcvfs.listdir(cache_dir)[1]
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(cache_dir, file)
                try:
                    stat = xbmcvfs.Stat(file_path)
                    total_size += stat.st_size()
                except:
                    pass
    return total_size

def movies_popular_api(page):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def movies_api(page, t):
    url = {
        'premiere': f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}',
        'trending': f'https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    }.get(t, '')
    if url:
        src = get_json(url)
        return src.get('total_pages', 0), src.get('results', [])
    return 0, []

def tv_shows_popular_api(page):
    url = f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def tv_shows_trending_api(page):
    url = f'https://api.themoviedb.org/3/trending/tv/day?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def animes_movies_popular_api(page):
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_keywords=210024&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def search_movies_api(search, page):
    url = f'https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={quote(search)}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def tv_shows_premiere_api(page):
    year, _ = get_date()
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&sort_by=popularity.desc&first_air_date_year={year}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def animes_popular_api(page):
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_keywords=210024&sort_by=popularity.desc&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def animes_premiere_api(page):
    year, _ = get_date()
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_keywords=210024&sort_by=popularity.desc&first_air_date_year={year}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def animes_airing_api(page):
    current_date, future_date = get_dates(7, reverse=False)
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_keywords=210024&air_date.gte={current_date}&air_date.lte={future_date}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def open_movie_api(id):
    url = f'https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def open_season_api(id):
    url = f'https://api.themoviedb.org/3/tv/{id}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def show_episode_api(id, season):
    url = f'https://api.themoviedb.org/3/tv/{id}/season/{season}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def open_episode_api(id, season, episode):
    url = f'https://api.themoviedb.org/3/tv/{id}/season/{season}/episode/{episode}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def find_tv_show_api(imdb):
    url = f'https://api.themoviedb.org/3/find/{imdb}?api_key={API_KEY}&external_source=imdb_id&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def search_tv_by_title(title, year=None):
    try:
        q = quote(title)
        url = f'https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&language={AutoTranslate.language("lang-api")}&query={q}'
        if year:
            url += f'&first_air_date_year={year}'
        return get_json(url)
    except Exception:
        return {}

def search_movie_by_title(title, year=None):
    try:
        q = quote(title)
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language={AutoTranslate.language("lang-api")}&query={q}'
        if year:
            url += f'&year={year}'
        return get_json(url)
    except Exception:
        return {}

def lastest_episodes_api(date):
    url = f'https://api.tvmaze.com/schedule?date={date}'
    return get_json(url)

def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_date():
    api_time = 'http://worldtimeapi.org/api/timezone/America/New_York'
    src = get_json(api_time)
    datetime = src.get('datetime', '')
    if datetime:
        last_year = datetime.split('-')[0]
        fulldate = datetime.split('T')[0]
    else:
        from datetime import date
        date_today = date.today()
        last_year = date_today.year
        fulldate = str(date_today)
    return last_year, fulldate
