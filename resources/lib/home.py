# -*- coding: utf-8 -*-
from resources.lib.menus import thunder, Donate
import sys
import re
import xbmcaddon

addonId = re.search('plugin\://(.+?)/', str(sys.argv[0])).group(1)
addon = thunder(addonId)

def router(params):
    action = params.get("action")
    name = params.get("name", "")
    url = params.get("url", "")
    iconimage = params.get("iconimage", "")
    fanart = params.get("fanart", "")
    description = params.get("description", "")
    description2 = params.get("description2", '')
    codec = params.get("codec", "")
    playable = params.get("playable", "")
    duration = params.get("duration", "")
    originaltitle = params.get("originaltitle", "")
    imdbnumber = params.get("imdbnumber", "")
    aired = params.get("aired", "")
    genre = params.get("genre", "")
    season = params.get("season", "")
    episode = params.get("episode", "")
    year = params.get("year", "")
    video_title = params.get("video_title", "")
    search_text = params.get("search", "")
    video_id = params.get("video_id")
    page = params.get("page") if params.get("page") else 1

    if action == None:        
        addon.home()
    elif action == "movies":
        addon.movies()
    elif action == "tv_shows":
        addon.tv_shows()
    elif action == "animes":
        addon.animes()
    elif action == "animes_movies":
        addon.animes_movies()
    elif action == "animes_tv_shows":
        addon.animes_tv_shows()
    elif action == "popular_animes_movies":
        addon.pagination_animes_movies_popular(page)
    elif action == "premiere_movies":
        addon.pagination_movies_premiere(page)
    elif action == "trending_movies":
        addon.pagination_movies_trending(page)
    elif action == "popular_movies":
        addon.pagination_movies_popular(page)
    elif action == "search_movies":
        if not search_text:
            search_text = addon.input_text('Pesquisar')
        if search_text:
            addon.pagination_search_movies(search_text, page)
    elif action == "premiere_tv_shows":
        addon.pagination_tv_shows_premiere(page)
    elif action == "trending_tv_shows":
        addon.pagination_tv_shows_trending(page)
    elif action == "popular_tv_shows":
        addon.pagination_tv_shows_popular(page)
    elif action == "premiere_animes":
        addon.pagination_animes_premiere(page)
    elif action == "popular_animes":
        addon.pagination_animes_popular(page)
    elif action == "airing_animes":
        addon.pagination_animes_airing(page)
    elif action == "season_tvshow":
        addon.season_tvshow(video_title, originaltitle, year, video_id)
    elif action == "episode_tvshow":
        addon.episode_tvshow(video_title, originaltitle, genre, imdbnumber, year, duration, video_id, season, iconimage, fanart)
    elif action == "new_episodes":
        addon.new_episodes()
    elif action == "search_tv_shows":
        if not search_text:
            search_text = addon.input_text('Pesquisar')
        if search_text:
            addon.pagination_search_tv_shows(search_text, page)                             
    elif action == "provider":
        if addon.is_auto_play_enabled():
            addon.auto_play_preferred_language(imdbnumber, year, season, episode, video_title, genre, iconimage, fanart, description)
        else:
            addon.list_server_links(imdbnumber, year, season, episode, name, video_title, genre, iconimage, fanart, description)
    elif action == "play_resolve":
        addon.resolve_links(url, video_title, imdbnumber, year, season, episode, genre, iconimage, fanart, description2, playable)
    elif action == "settings":
        xbmcaddon.Addon().openSettings()
    elif action == "donate":
        i = Donate()
        i.doModal()