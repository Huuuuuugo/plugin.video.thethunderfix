# -*- coding: utf-8 -*-
import os
from kodi_helper import requests, myAddon
import sys
import re
addonId = re.search('plugin\://(.+?)/',str(sys.argv[0])).group(1)
addon = myAddon(addonId)
profile = addon.profile

if not addon.exists(profile):
    try:
        addon.mkdir(profile)
    except:
        pass
cache_country = os.path.join(profile,'country.txt')
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

def get_country():
    if addon.exists(cache_country):
        country = ''
        with open(cache_country, 'r') as f:
            country = f.read()
    else:
        try:
            ip = requests.get('https://api.ipify.org/',headers={'User-Agent': USER_AGENT}).text
            country = requests.get('https://ipinfo.io/widget/demo/{0}'.format(ip),headers={'User-Agent': USER_AGENT, 'Referer': 'https://ipinfo.io/'}).json().get('data', {}).get('country', '')
            if country:
                with open(cache_country, 'w') as f:
                    f.write(country)
            else:
                country = 'unknow'
        except:
            country = 'unknow'
    return country

class AutoTranslate:
    country = get_country()

    @classmethod
    def language(cls,key):
        #BR - BRASIL
        #AR - ARGENTINA
        #GB - REINO UNIDO
        #US - ESTADOS UNIDOS
        #ES - ESPANHA
        #MX - MEXICO
        #UY - URUGUAI
        #PY - PARAGUAI
        #CL - CHILE
        #PT - PORTUGAL
        #https://api.themoviedb.org/3/movie/now_playing?api_key=92c1507cc18d85290e7a0b96abb37316&append_to_response=external_ids&language=pt-PT&page=1
        if cls.country == 'BR':
            return {
                'lang-api': 'pt-BR',
                'Movies': 'Filmes',
                'Tv shows': 'Séries',
                'Animes': 'Animes',
                'New animes': 'Novos animes',
                'New movies': 'Novos filmes',
                'Trending': 'Em alta',
                'Popular': 'Populares',
                'Popular recent': 'Populares recente',
                'Airing': 'Em exibição',
                'Search': 'Pesquisar',
                'New tv shows': 'Novas séries',
                'New episodes': 'Novos episódios',
                'Page': 'Pagina ',
                'of': ' de ',
                'Portuguese': 'DUBLADO',
                'Portuguese2': 'Dublado',
                'English': 'LEGENDADO',
                'English2': 'Legendado',
                'select_option': 'SELECIONE UMA OPÇÃO ABAIXO:',
                'direct': 'Direto',
                'select_player': 'SELECIONE UM REPRODUTOR:',
                'load_torrent': 'carregando torrent...',
                'select_torrent': 'SELECIONE UM TORRENT ABAIXO:',
                'preparing': 'preparando reproducao...',
                'ready': 'Pronto pra reproducao',
                'wait': 'Por favor aguarde...',
                'find_source': 'Procurando nas fontes',
                'donation': 'Doação'
            }.get(key, 'Unknow')
        elif cls.country == 'PT':
            return {
                'lang-api': 'pt-PT',
                'Movies': 'Filmes',
                'Tv shows': 'Séries',
                'Animes': 'Animes',
                'New animes': 'Novos animes',
                'New movies': 'Novos filmes',
                'Trending': 'Em alta',
                'Popular': 'Populares',
                'Popular recent': 'Populares recente',
                'Airing': 'Em exibição',
                'Search': 'Pesquisar',
                'New tv shows': 'Novas séries',
                'New episodes': 'Novos episódios',
                'Page': 'Pagina ',
                'of': ' de ',
                'Portuguese': 'DUBLADO',
                'Portuguese2': 'Dublado',
                'English': 'LEGENDADO',
                'English2': 'Legendado',
                'select_option': 'SELECIONE UMA OPÇÃO ABAIXO:',
                'direct': 'Direto',
                'select_player': 'SELECIONE UM REPRODUTOR:',
                'load_torrent': 'carregando torrent...',
                'select_torrent': 'SELECIONE UM TORRENT ABAIXO:',
                'preparing': 'preparando reproducao...',
                'ready': 'Pronto pra reproducao',
                'wait': 'Por favor aguarde...',
                'find_source': 'Procurando nas fontes',
                'donation': 'Doação'
            }.get(key, 'Unknow')        
        else:
            return {
                'lang-api': 'en-US',
                'Movies': 'Movies',
                'Tv shows': 'Tv shows',
                'Animes': 'Animes',
                'New animes': 'New animes',
                'New movies': 'New movies',
                'Trending': 'Trending',
                'Popular': 'Popular',
                'Popular recent': 'Popular recent',
                'Airing': 'Airing',
                'Search': 'Search',
                'New tv shows': 'New tv shows',
                'New episodes': 'New episodes',
                'Page': 'Page ',
                'of': ' of ',
                'Portuguese': 'PORTUGUESE',
                'Portuguese2': 'Portuguese',
                'English': 'ENGLISH',
                'English2': 'English',
                'select_option': 'SELECT AN OPTION BELOW:',
                'direct': 'Direct',
                'select_player': 'SELECT A PLAYER:',
                'load_torrent': 'loading torrent...',
                'select_torrent': 'SELECT A TORRENT BELOW:',
                'preparing': 'preparing reproduction...',
                'ready': 'Ready for reproduction',
                'wait': 'Please wait...',
                'find_source': 'Searching the sources',
                'donation': 'Donation'                
            }.get(key, 'Unknow')
          

    
    
