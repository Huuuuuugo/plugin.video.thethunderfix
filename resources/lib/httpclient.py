# -*- coding: utf-8 -*-
#from thunderlib.plugin.functions import log
from resources.lib.utils import get_current_date, get_dates, years_tvshows
from resources.lib.autotranslate import AutoTranslate
from kodi_helper import requests
import re


API_KEY1 = '92c1507cc18d85290e7a0b96abb37316' #zoreu
API_KEY2 = '7461cdca6387c3a5e6be0d5a8ef7ad2b'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def request_api(url1,url2):
    try:
        r = requests.get(url1,headers={'User-Agent': USER_AGENT})
        if r.status_code == 200:
            return r.json()
        else:
            r = requests.get(url2,headers={'User-Agent': USER_AGENT})
            if r.status_code == 200:
                return r.json()
            else:
                return {}
    except:
        try:
            r = requests.get(url2,headers={'User-Agent': USER_AGENT})
            if r.status_code == 200:
                return r.json()
            else:
                return {}
        except:
            return {}

def open_movie_api(id):
    url1 = 'https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=external_ids&language='.format(str(id),API_KEY1) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=external_ids&language='.format(str(id),API_KEY2) + AutoTranslate.language('lang-api')
    src = request_api(url1,url2)
    return src


def movies_api(page,t):
    url1 = {'premiere': 'https://api.themoviedb.org/3/movie/now_playing?api_key={0}&append_to_response=external_ids&page={1}&language='.format(API_KEY1,str(page)) + AutoTranslate.language('lang-api'),
           'trending': 'https://api.themoviedb.org/3/movie/popular?api_key={0}&append_to_response=external_ids&page={1}&language='.format(API_KEY1,str(page)) + AutoTranslate.language('lang-api')
           }.get(t, '')
    url2 = {'premiere': 'https://api.themoviedb.org/3/movie/now_playing?api_key={0}&append_to_response=external_ids&page={1}&language='.format(API_KEY2,str(page)) + AutoTranslate.language('lang-api'),
           'trending': 'https://api.themoviedb.org/3/movie/popular?api_key={0}&append_to_response=external_ids&page={1}&language='.format(API_KEY2,str(page)) + AutoTranslate.language('lang-api')
           }.get(t, '')    
    if url1:
        try:
            src = request_api(url1,url2)
            total_pages = src.get('total_pages', 0)
            results = src.get('results', False)
            return total_pages,results
        except:
            return 0,False
    else:
        return 0,False
    
def search_movies_api(search,page):
    url1 = 'https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}&append_to_response=origin_country&page={2}&language='.format(API_KEY1,str(search),str(page)) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}&append_to_response=origin_country&page={2}&language='.format(API_KEY2,str(search),str(page)) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        total_pages = src.get('total_pages', 0)
        results = src.get('results', False)
        return total_pages,results
    except:
        return 0,False

def get_date():
    api_time = 'http://worldtimeapi.org/api/timezone/America/New_York'
    try:
        r = requests.get(api_time,headers={'User-Agent': USER_AGENT})
        src = r.json()
    except:
        src = {}     
    datetime = src.get('datetime', '')
    if datetime:
        last_year = datetime.split('-')[0]
        fulldate = datetime.split('T')[0]
        fulldate = str(fulldate)
    else:
        from datetime import date
        date_today = date.today()
        last_year = date_today.year
        fulldate = str(date_today)
    return last_year, fulldate

def tv_shows_premiere_api(page):
    year_datetime, date = get_date()
    url1 = 'https://api.themoviedb.org/3/discover/tv?api_key={0}&sort_by=popularity.desc&first_air_date_year={1}&timezone=America%2FNew_York&include_null_first_air_ates=false&page={2}&language='.format(API_KEY1,str(year_datetime),str(page)) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/discover/tv?api_key={0}&sort_by=popularity.desc&first_air_date_year={1}&timezone=America%2FNew_York&include_null_first_air_ates=false&page={2}&language='.format(API_KEY2,str(year_datetime),str(page)) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        total_pages = src.get('total_pages', 0)
        results = src.get('results', False)
        return total_pages,results
    except:
        return 0,False

def tv_shows_trending_api(page):
    url1 = 'https://api.themoviedb.org/3/tv/popular?api_key={0}&page={1}&language='.format(API_KEY1,str(page)) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/tv/popular?api_key={0}&page={1}&language='.format(API_KEY2,str(page)) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        total_pages = src.get('total_pages', 0)
        results = src.get('results', False)
        return total_pages,results
    except:
        return 0,False 

def open_season_api(id):
    url1 = 'https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=external_ids&language='.format(str(id),API_KEY1) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=external_ids&language='.format(str(id),API_KEY2) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        return src
    except:
        return {}

def show_episode_api(id,season):
    url1 = 'https://api.themoviedb.org/3/tv/{0}/season/{1}?api_key={2}&append_to_response=external_ids&language='.format(str(id),str(season),API_KEY1) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/tv/{0}/season/{1}?api_key={2}&append_to_response=external_ids&language='.format(str(id),str(season),API_KEY2) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        return src
    except:
        return {}

def open_episode_api(id,season,episode):
    url1 = 'https://api.themoviedb.org/3/tv/{0}/season/{1}/episode/{2}?api_key={3}&append_to_response=external_ids&language='.format(str(id),str(season),str(episode),API_KEY1) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/tv/{0}/season/{1}/episode/{2}?api_key={3}&append_to_response=external_ids&language='.format(str(id),str(season),str(episode),API_KEY2) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        return src
    except:
        return {}

def find_tv_show_api(imdb):
    url1 = 'https://api.themoviedb.org/3/find/{0}?api_key={1}&external_source=imdb_id&language='.format(str(imdb),API_KEY1) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/find/{0}?api_key={1}&external_source=imdb_id&language='.format(str(imdb),API_KEY2) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        return src
    except:
        return {}

def lastest_episodes_api(date):
    url = 'https://api.tvmaze.com/schedule?date={0}'.format(str(date))
    try:
        r = requests.get(url,headers={'User-Agent': USER_AGENT})
        src = r.json()
    except:
        src = []
    return src

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def search_tv_shows_api(search,page):
    url1 = 'https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}&page={2}&language='.format(API_KEY1,str(search),str(page)) + AutoTranslate.language('lang-api')
    url2 = 'https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}&page={2}&language='.format(API_KEY2,str(search),str(page)) + AutoTranslate.language('lang-api')
    try:
        src = request_api(url1,url2)
        total_pages = src.get('total_pages', 0)
        results = src.get('results', False)
        return total_pages,results
    except:
        return 0,False 
