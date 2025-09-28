# -*- coding: utf-8 -*-

WEBSITE = 'CDN'

import re
import os
import sys
import json
import requests
import resources.lib.jsunpack as jsunpack
try:
    from resources.lib.autotranslate import AutoTranslate
    portuguese = AutoTranslate.language('Portuguese')
    english = AutoTranslate.language('English')
    select_option_name = AutoTranslate.language('select_option')
except ImportError:
    portuguese = 'DUBLADO'
    english = 'LEGENDADO'
    select_option_name = 'SELECIONE UMA OPÇÃO ABAIXO:'
try:
    from resources.lib import resolveurl
except ImportError:
    local_path = os.path.dirname(os.path.realpath(__file__))
    lib_path = local_path.replace('scrapers', '')
    sys.path.append(lib_path)
    from resolvers import resolveurl

class source:

    # ===============================
    # Sessão e helpers
    # ===============================

    @classmethod
    def _get_session(cls):
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        })
        return session

    # ===============================
    # Funções auxiliares internas
    # ===============================

    @classmethod
    def _get_audio_ids_series(cls, session, imdb, season, episode, timeout=10):
        referer_url = f"https://embed.warezcdn.link/serie/{imdb}"
        data = session.get(referer_url, timeout=timeout).text

        match = re.search(r"var cachedSeasons\s*=\s*['\"]([^'\"]+)['\"]", data)
        if not match:
            return [], referer_url

        season_url = f"https://embed.warezcdn.link/{match.group(1)}"
        seasons_info = session.get(season_url, headers={'Referer': referer_url}, timeout=timeout).json().get("seasons", {})

        episode_info = next(
            (ep for s in seasons_info.values() if s["name"] == str(season)
             for ep in s["episodes"].values() if ep["name"] == str(episode)),
            None
        )
        if not episode_info:
            return [], referer_url

        audio_ids = session.get(
            f"https://embed.warezcdn.link/core/ajax.php?audios={episode_info['id']}",
            headers={'Referer': referer_url},
            timeout=timeout
        ).json()
        return json.loads(audio_ids), referer_url

    @classmethod
    def _get_audio_ids_movie(cls, session, imdb, timeout=10):
        referer_url = f"https://embed.warezcdn.link/filme/{imdb}"
        data = session.get(referer_url, timeout=timeout).text

        match = re.search(r"let data = ['\"](\[.+\])['\"]", data)
        if not match:
            return [], referer_url

        result = json.loads(match.group(1))
        return result, referer_url

    @classmethod
    def _extract_links(cls, session, audio_ids, referer_url, timeout=10):
        links = []
        LANG_MAP = {1: english, 2: portuguese}
        SERVERS = ['warezcdn', 'mixdrop']

        for audio in audio_ids:
            lg = LANG_MAP.get(int(audio['audio']), 'UNKNOWN')
            for server in SERVERS:
                if server not in audio['servers']:
                    continue

                embed_referer_url = f"https://embed.warezcdn.link/getEmbed.php?id={audio['id']}&sv={server}&lang={audio['audio']}"
                play_url = f"https://embed.warezcdn.link/getPlay.php?id={audio['id']}&sv={server}"

                session.get(referer_url, timeout=timeout)
                session.get(embed_referer_url, headers={'Referer': referer_url}, timeout=timeout)
                play_response = session.get(play_url, headers={'Referer': embed_referer_url}, timeout=timeout).text

                match = re.search(r"window.location.href\s*=\s*['\"](.+?)['\"]", play_response)
                if match:
                    video_url = match.group(1)
                    links.append((f"{server.upper()} - {lg}", video_url))
        return links

    # ===============================
    # Funções principais
    # ===============================

    @classmethod
    def warezcdn_servers(cls, imdb, season=False, episode=False):
        session = cls._get_session()
        timeout = 10

        try:
            if season and episode:
                audio_ids, referer_url = cls._get_audio_ids_series(session, imdb, season, episode, timeout)
            else:
                audio_ids, referer_url = cls._get_audio_ids_movie(session, imdb, timeout)

            result = cls._extract_links(session, audio_ids, referer_url, timeout)
            return result

        except Exception:
            return []

    @classmethod
    def search_movies(cls, imdb, year):
        try:
            return cls.warezcdn_servers(imdb, False, False)
        except Exception:
            return []

    @classmethod
    def resolve_movies(cls, url):
        streams = []
        if not url:
            return streams

        # extrair legenda
        sub = ''
        try:
            sub_part = url.split('http')[2]
            sub = 'http' + sub_part.split('&')[0]
            if '.srt' not in sub:
                sub = ''
        except:
            pass

        # extrair link base
        stream = url.split('?')[0].split('#')[0]
        referer_url = 'https://embed.warezcdn.link/'

        # Usa a função resolveurl de resolvers.py para resolver o link
        resolved, sub_from_resolver = resolveurl(stream, referer=referer_url)
        if resolved:
            streams.append((resolved, sub if sub else sub_from_resolver, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'))

        return streams

    @classmethod
    def search_tvshows(cls, imdb, year, season, episode):
        try:
            return cls.warezcdn_servers(imdb, season, episode)
        except Exception:
            return []

    @classmethod
    def resolve_tvshows(cls, url):
        return cls.resolve_movies(url)