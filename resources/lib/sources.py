# -*- coding: utf-8 -*-
import os
import sys
import re
try:
    from resources.lib.autotranslate import AutoTranslate
except:
    pass
try:
    from kodi_helper import myAddon
    addonId = re.search('plugin://(.+?)/',str(sys.argv[0])).group(1)
    addon = myAddon(addonId)
    scrapers = addon.translate('special://home/addons/plugin.video.thethunder/resources/lib/scrapers/')
    progress = addon.progress_six
except:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    scrapers = os.path.join(dir_path, "scrapers")

# Importar xbmcaddon para acessar configurações diretamente
try:
    import xbmcaddon
    addon_instance = xbmcaddon.Addon(id=addonId)
except:
    addon_instance = None

def import_scripts(pasta):
    scripts = [f[:-3] for f in os.listdir(pasta) if f.endswith(".py") and f != "__init__.py"]
    modulos = []
    sys.path.append(pasta)  # Adiciona a pasta ao caminho de busca de módulos

    for script in scripts:
        # Verificar se a fonte está ativada nas configurações
        source_enabled = True
        if addon_instance:
            if script == 'warez' and addon_instance.getSetting('source_warezcdn') != 'true':
                source_enabled = False
            elif script == 'overflix' and addon_instance.getSetting('source_overflix') != 'true':
                source_enabled = False

        if source_enabled:
            if sys.version_info.major == 3:
                import importlib
                modulo = importlib.import_module(script)  # Importa o módulo pelo seu nome simples
            else:
                # Python 2
                modulo = __import__(script)
            modulos.append(modulo)

    return modulos

modules_import = import_scripts(scrapers)
total_sites = len(modules_import)

def search_movies(imdb, year):
    try:
        dp = progress()
        dp.create(AutoTranslate.language('wait'), AutoTranslate.language('find_source'))
    except:
        pass    
    stream_movies = []
    for n, modulo in enumerate(modules_import):
        count = n + 1
        update = int(count / total_sites * 100)
        stream_movies.append(modulo.source.search_movies(imdb, year))
        # FUNC UPDATE KODI      
        try:
            dp.update(update, str(modulo.WEBSITE))
        except:
            pass        
    streams_final = []
    if stream_movies:
        for streams in stream_movies:
            if streams:
                for s in streams:
                    name, page = s
                    streams_final.append((name, page))
    return streams_final

def resolve_movies(url):
    stream = ''
    sub = ''
    for modulo in modules_import:
        if not stream:
            source = modulo.source.resolve_movies(url)
            if len(source) > 0:
                stream = source[0][0]
                sub = source[0][1]
                break            
        else:
            break
    return stream, sub

def resolve_tvshows(url):
    stream = ''
    sub = ''
    for modulo in modules_import:
        if not stream:
            source = modulo.source.resolve_tvshows(url)
            if len(source) > 0:
                stream = source[0][0]
                sub = source[0][1]
                break            
        else:
            break
    return stream, sub

def search_tvshows(imdb, year, season, episode):
    try:
        dp = progress()
        dp.create(AutoTranslate.language('wait'), AutoTranslate.language('find_source'))
    except:
        pass
    stream_tvshows = []
    for n, modulo in enumerate(modules_import):
        count = n + 1
        update = int(count / total_sites * 100)
        stream_tvshows.append(modulo.source.search_tvshows(imdb, year, season, episode))
        # FUNC UPDATE KODI      
        try:
            dp.update(update, str(modulo.WEBSITE))
        except:
            pass
    streams_final = []
    if stream_tvshows:
        for streams in stream_tvshows:
            if streams:
                for s in streams:
                    name, page = s
                    streams_final.append((name, page))
    return streams_final

def show_content(imdb, year, season, episode):
    if not season and not episode:
        stream_list = search_movies(imdb, year)
        return stream_list
    elif season and episode:
        stream_list = search_tvshows(imdb, year, season, episode)
        return stream_list
    return None

def select_resolver(url, season, episode):
    if not season and not episode:
        stream, sub = resolve_movies(url)
        return stream, sub
    elif season and episode:
        stream, sub = resolve_tvshows(url)
        return stream, sub        
    return None, None