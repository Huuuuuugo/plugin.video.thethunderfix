# -*- coding: utf-8 -*-
import os
from kodi_helper import requests, myAddon
import sys
import re

addonId = re.search('plugin://(.+?)/', str(sys.argv[0])).group(1)
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
            country = requests.get(
                f'https://ipinfo.io/widget/demo/{ip}',
                headers={'User-Agent': USER_AGENT, 'Referer': 'https://ipinfo.io/'}
            ).json().get('data', {}).get('country', '')
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
        # BRASIL
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
                'Page': 'Página ',
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
                'preparing': 'preparando reprodução...',
                'ready': 'Pronto para reprodução',
                'wait': 'Por favor aguarde...',
                'find_source': 'Procurando nas fontes',
                'settings': 'Configurações',
                'donation': 'Doação',
                'Please enter a valid search term': 'Por favor insira um termo de pesquisa válido',
                'No sources available': 'Nenhuma fonte disponível',
                'Stream unavailable': 'Stream indisponível',
                'invalid_params': 'Parâmetros inválidos',
                'IMDb not found': 'IMDb não encontrado',
                'Failed to resolve link': 'Falha ao resolver link',
                'If you like this add-on, support via PIX above': 'Se você gostou deste add-on, apoie via PIX acima',
                'Press BACK to exit': 'Pressione VOLTAR para sair',
                'Error playing': 'Erro ao reproduzir',
                'Error trying to play': 'Erro ao tentar reproduzir',
                'Failed to load details': 'Falha ao carregar detalhes',
                'InputStream Adaptive is required but not installed': 'InputStream Adaptive é necessário mas não está instalado',
                'InputStream FFMpeg Direct is required but not installed': 'InputStream FFMpeg Direct é necessário mas não está instalado',
                'Specials': 'Especiais',
                'Season': 'Temporada',
                'Episode': 'Episódio',
            }.get(key, 'Unknow')

        # PORTUGAL
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
                'Page': 'Página ',
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
                'preparing': 'preparando reprodução...',
                'ready': 'Pronto para reprodução',
                'wait': 'Por favor aguarde...',
                'find_source': 'Procurando nas fontes',
                'settings': 'Configurações',
                'donation': 'Doação',
                'Please enter a valid search term': 'Por favor insira um termo de pesquisa válido',
                'No sources available': 'Nenhuma fonte disponível',
                'Stream unavailable': 'Stream indisponível',
                'invalid_params': 'Parâmetros inválidos',
                'IMDb not found': 'IMDb não encontrado',
                'Failed to resolve link': 'Falha ao resolver link',
                'If you like this add-on, support via PIX above': 'Se você gostou deste add-on, apoie via PIX acima',
                'Press BACK to exit': 'Pressione VOLTAR para sair',
                'Error playing': 'Erro ao reproduzir',
                'Error trying to play': 'Erro ao tentar reproduzir',
                'Failed to load details': 'Falha ao carregar detalhes',
                'InputStream Adaptive is required but not installed': 'InputStream Adaptive é necessário mas não está instalado',
                'InputStream FFMpeg Direct is required but not installed': 'InputStream FFMpeg Direct é necessário mas não está instalado',
                'Specials': 'Especiais',
                'Season': 'Temporada',
                'Episode': 'Episódio',
            }.get(key, 'Unknow')

        # OUTROS PAÍSES → INGLÊS
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
                'preparing': 'preparing playback...',
                'ready': 'Ready for playback',
                'wait': 'Please wait...',
                'find_source': 'Searching the sources',
                'settings': 'Settings',
                'donation': 'Donation',
                'Please enter a valid search term': 'Please enter a valid search term',
                'No sources available': 'No sources available',
                'Stream unavailable': 'Stream unavailable',
                'invalid_params': 'Invalid parameters',
                'IMDb not found': 'IMDb not found',
                'Failed to resolve link': 'Failed to resolve link',
                'If you like this add-on, support via PIX above': 'If you like this add-on, support via PIX above',
                'Press BACK to exit': 'Press BACK to exit',
                'Error playing': 'Error playing',
                'Error trying to play': 'Error trying to play',
                'Failed to load details': 'Failed to load details',
                'InputStream Adaptive is required but not installed': 'InputStream Adaptive is required but not installed',
                'InputStream FFMpeg Direct is required but not installed': 'InputStream FFMpeg Direct is required but not installed',
                'Specials': 'Specials',
                'Season': 'Season',
                'Episode': 'Episode',
            }.get(key, 'Unknow')