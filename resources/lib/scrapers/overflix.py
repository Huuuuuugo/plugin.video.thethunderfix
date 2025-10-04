# -*- coding: utf-8 -*-

WEBSITE = 'OVERFLIX'

try:
    from resources.lib.ClientScraper import cfscraper, USER_AGENT
except ImportError:
    from ClientScraper import cfscraper, USER_AGENT

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, urljoin
import os
import sys
import re

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
    from kodi_helper import myAddon
    addonId = re.search('plugin\://(.+?)/', str(sys.argv[0])).group(1)
    addon = myAddon(addonId)
    select = addon.select
except ImportError:
    local_path = os.path.dirname(os.path.realpath(__file__))
    lib_path = local_path.replace('scrapers', '')
    sys.path.append(lib_path)

try:
    from resources.lib import resolveurl
except ImportError:
    local_path = os.path.dirname(os.path.realpath(__file__))
    lib_path = local_path.replace('scrapers', '')
    sys.path.append(lib_path)
    from resolvers import resolveurl

class source:
    @classmethod
    def normalize_title(cls, title):
        title = title.lower().strip()
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', '-', title)
        return title

    @classmethod
    def find_brazil_title(cls, imdb):
        url = f'https://www.imdb.com/title/{imdb}/releaseinfo'
        try:
            r = cfscraper.get(url)
            if not r or r.status_code != 200:
                return ''
            soup = BeautifulSoup(r.text, 'html.parser')
            akas_table = soup.find('table', class_='akas-table')
            if akas_table:
                for row in akas_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2 and 'Brazil' in cells[0].text:
                        return cells[1].text.strip()
            return ''
        except Exception:
            return ''

    @classmethod
    def find_title(cls, imdb):
        url = f'https://www.imdb.com/title/{imdb}'
        try:
            r = cfscraper.get(url)
            if not r or r.status_code != 200:
                return ''
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('h1', {'data-testid': 'hero__pageTitle'})
            if title:
                return title.find('span').text
            return ''
        except Exception:
            return ''

    @classmethod
    def _extract_embeds_from_page(cls, html):
        embeds = []
        soup = BeautifulSoup(html, 'html.parser')
        token = 'cfxp594cpa4to'
        token_match = re.search(r'token\s*=\s*["\']([^"\']+)["\']', html)
        if token_match:
            token = token_match.group(1)
        player_divs = soup.find_all('div', class_='item', onclick=re.compile(r'GetIframe\([^)]+\)'))
        for div in player_divs:
            onclick = div.get('onclick', '')
            match = re.search(r"GetIframe\('([^']+)','([^']+)'\)", onclick)
            if not match:
                continue
            player_id, server = match.groups()
            getembed = f"https://etv-embed.help/e/getembed.php?sv={server}&id={player_id}&site=overflix&token={token}"
            server_name = server.upper()
            embeds.append((server_name, getembed, {'id': player_id, 'sv': server, 'token': token}))
        return embeds

    @classmethod
    def _get_play_url(cls, referer_url, getembed_url, meta):
        headers = {
            'User-Agent': USER_AGENT,
            'Referer': cls.__site_url__[-1]
        }
        try:
            requests.get(referer_url, headers=headers)
        except Exception:
            pass
        headers_embed = {
            'User-Agent': USER_AGENT,
            'Referer': cls.__site_url__[-1]
        }
        try:
            r1 = requests.get(getembed_url, headers=headers_embed)
            if r1.status_code != 200:
                return None
        except Exception:
            return None
        id_ = meta.get('id')
        sv = meta.get('sv')
        play_url = f"https://etv-embed.help/e/getplay.php?id={id_}&sv={sv}"
        try:
            r2 = requests.get(play_url, headers={'User-Agent': USER_AGENT, 'Referer': getembed_url}, allow_redirects=True)
            if r2.status_code != 200:
                return None
            if r2.history:
                return r2.url
            html = r2.text
            patterns = [
                r'window\.location\.href\s*=\s*[\'"](https?://(?:filemoon|dood|doodstream|mixdrop|streamtape)\.[a-z0-9.-]+/[^\s"\']+)[\'"]',
                r'<iframe[^>]+src=[\'"](https?://(?:filemoon|dood|doodstream|mixdrop|streamtape)\.[a-z0-9.-]+/[^\s"\']+)[\'"]',
                r'(?:href|src)=[\'"](https?://(?:filemoon|dood|doodstream|mixdrop|streamtape)\.[a-z0-9.-]+/[^\s"\']+)[\'"]',
                r'var\s+videoUrl\s*=\s*[\'"](https?://(?:filemoon|dood|doodstream|mixdrop|streamtape)\.[a-z0-9.-]+/[^\s"\']+)[\'"]'
            ]
            final_video = None
            for pattern in patterns:
                match = re.search(pattern, html, re.I)
                if match:
                    final_video = match.group(1)
                    break
            if not final_video:
                if sv == 'doodstream':
                    redirect = re.search(r'window\.location\.href\s*=\s*[\'"](https?://dsvplay\.com/[^\s"\']+)[\'"]', html, re.I)
                    if redirect:
                        final_video = redirect.group(1)
                elif sv == 'filemoon':
                    iframe = re.search(r'<iframe[^>]+src=[\'"](https?://filemoon\.[a-z0-9.-]+/[^\s"\']+)[\'"]', html, re.I)
                    if iframe:
                        final_video = iframe.group(1)
                elif sv == 'mixdrop':
                    mixdrop = re.search(r'(?:window\.location\.href|var\s+videoUrl)\s*=\s*[\'"](https?://mixdrop\.[a-z0-9.-]+/[^\s"\']+)[\'"]', html, re.I)
                    if mixdrop:
                        final_video = mixdrop.group(1)
            if not final_video:
                return None
            return final_video
        except Exception:
            return None

    @classmethod
    def search_movies(cls, imdb, year):
        links = []
        title = cls.find_brazil_title(imdb) or cls.find_title(imdb)
        if not title:
            return links
        try:
            query = quote_plus(cls.normalize_title(title))
            search_url = cls.__site_url__[-1].rstrip('/') + '/pesquisar/?p=' + query
            r = cfscraper.get(search_url)
            if not r or r.status_code != 200 or "captcha" in r.text.lower():
                return links
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all('a', href=re.compile(r'/assistir-.*-\d{4}-\d+'))
            movie_url = None
            for item in results:
                href = urljoin(cls.__site_url__[-1], item['href'])
                found_title = item.get_text(strip=True).lower()
                y_match = re.search(r'-(\d{4})-(\d+)/?$', href)
                y = y_match.group(1) if y_match else None
                t0 = cls.normalize_title(title)
                if t0 in found_title.replace(' ', '-') or t0 in found_title:
                    try:
                        if y and int(year) == int(y):
                            movie_url = href
                            break
                    except Exception:
                        pass
            if not movie_url:
                return links
            movie_urls = {}
            t0 = cls.normalize_title(title)
            for item in results:
                href = urljoin(cls.__site_url__[-1], item['href'])
                found_title = item.get_text(strip=True).lower()
                y_match = re.search(r'-(\d{4})-(\d+)/?$', href)
                y = y_match.group(1) if y_match else None
                if (t0 in found_title.replace(' ', '-') or t0 in found_title) and y:
                    try:
                        if int(year) == int(y):
                            if 'dublado' in href:
                                movie_urls['dublado'] = href
                            elif 'legendado' in href:
                                movie_urls['legendado'] = href
                    except Exception:
                        pass
            if not movie_urls:
                movie_urls['dublado'] = movie_url
            r = cfscraper.get(f"{movie_url}?area=online", headers={'Referer': cls.__site_url__[-1]})
            if not r or r.status_code != 200 or "captcha" in r.text.lower():
                return links
            embeds_final = []
            soup0 = BeautifulSoup(r.text, 'html.parser')
            audio_tabs = soup0.find('span', class_='tab_order')
            languages = ['dublado', 'legendado'] if audio_tabs else ['dublado']
            for lang in languages:
                lang_label = portuguese if lang == 'dublado' else english
                lang_url = movie_urls.get(lang)
                if lang_url:
                    if 'area=online' not in lang_url:
                        sep = '&' if '?' in lang_url else '?'
                        lang_url = lang_url + sep + 'area=online'
                else:
                    lang_url = f"{movie_url}?area=online&audio={lang}"
                rlang = cfscraper.get(lang_url, headers={'Referer': cls.__site_url__[-1]})
                if not rlang or rlang.status_code != 200 or "captcha" in rlang.text.lower():
                    continue
                embeds = cls._extract_embeds_from_page(rlang.text)
                if not embeds:
                    continue
                for server_name, getembed_url, meta in embeds:
                    final_video = cls._get_play_url(referer_url=lang_url, getembed_url=getembed_url, meta=meta)
                    if final_video:
                        name = f"{server_name} - {lang_label}"
                        embeds_final.append((name, final_video))
            return embeds_final
        except Exception:
            return links

    @classmethod
    def search_tvshows(cls, imdb, year, season, episode):
        links = []
        title = cls.find_brazil_title(imdb) or cls.find_title(imdb)
        if not title:
            return links
        try:
            query = quote_plus(cls.normalize_title(title))
            search_url = cls.__site_url__[-1].rstrip('/') + '/pesquisar/?p=' + query
            r = cfscraper.get(search_url)
            if not r or r.status_code != 200 or "captcha" in r.text.lower():
                return links
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all('a', href=re.compile(r'/assistir-.*-\d{4}-\d+'))
            series_urls = {}
            t0 = cls.normalize_title(title)
            for item in results:
                href = urljoin(cls.__site_url__[-1], item['href'])
                found_title = item.get_text(strip=True).lower()
                y_match = re.search(r'-(\d{4})-(\d+)/?$', href)
                y = y_match.group(1) if y_match else None
                if t0 in found_title.replace(' ', '-') or t0 in found_title:
                    year_match = True
                    if y:
                        try:
                            year_match = int(year) == int(y)
                        except Exception:
                            year_match = False
                    if year_match:
                        if 'dublado' in href.lower():
                            series_urls['dublado'] = href
                        elif 'legendado' in href.lower():
                            series_urls['legendado'] = href
            if not series_urls:
                return links
            embeds_final = []
            languages = ['dublado', 'legendado']
            for lang in languages:
                series_url = series_urls.get(lang)
                if not series_url:
                    continue
                r = cfscraper.get(series_url, headers={'Referer': cls.__site_url__[-1]})
                if not r or r.status_code != 200 or "captcha" in r.text.lower():
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                episode_links = soup.find_all('a', href=re.compile(r'/assistir-.*-\d+x\d+-[a-z]+(?:-[a-z]+\d+)?-\d+'))
                episode_url = None
                for item in episode_links:
                    href = urljoin(cls.__site_url__[-1], item['href'])
                    ep_match = re.search(r'-(\d+)x(\d+)-([a-z]+)(?:-[a-z]+\d+)?-(\d+)/?$', href, re.I)
                    if ep_match:
                        found_season = int(ep_match.group(1))
                        found_episode = int(ep_match.group(2))
                        found_lang_in_url = ep_match.group(3).lower()
                        lang_variations = [lang, 'leg'] if lang == 'legendado' else [lang]
                        if (found_season == int(season) and found_episode == int(episode) and 
                            found_lang_in_url in lang_variations):
                            episode_url = href
                            break
                if not episode_url:
                    continue
                lang_label = portuguese if lang == 'dublado' else english
                lang_url = episode_url
                rlang = cfscraper.get(lang_url, headers={'Referer': cls.__site_url__[-1]})
                if not rlang or rlang.status_code != 200 or "captcha" in rlang.text.lower():
                    continue
                embeds = cls._extract_embeds_from_page(rlang.text)
                if not embeds:
                    continue
                for server_name, getembed_url, meta in embeds:
                    final_video = cls._get_play_url(referer_url=lang_url, getembed_url=getembed_url, meta=meta)
                    if final_video:
                        name = f"{server_name} - {lang_label}"
                        embeds_final.append((name, final_video))
            return embeds_final
        except Exception:
            return links

    __site_url__ = ['https://overflixtv.ltd/']

    @classmethod
    def resolve_movies(cls, url):
        streams = []
        if not url:
            return streams
        sub = ''
        try:
            sub_part = url.split('http')[2]
            sub = 'http' + sub_part.split('&')[0]
            if '.srt' not in sub:
                sub = ''
        except:
            pass
        stream = url.split('?')[0].split('#')[0]
        try:
            resolved, sub_from_resolver = resolveurl(stream, referer=None)
            if resolved:
                streams.append((resolved, sub if sub else sub_from_resolver, USER_AGENT))
        except Exception:
            pass
        return streams

    @classmethod
    def resolve_tvshows(cls, url):
        return cls.resolve_movies(url)
