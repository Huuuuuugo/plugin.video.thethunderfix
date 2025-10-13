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
import difflib

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
    def find_title(cls, imdb):
        url = f'https://m.imdb.com/pt/title/{imdb}'
        try:
            r = cfscraper.get(url)
            if not r or r.status_code != 200:
                return '', '', ''
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('h1', {'data-testid': 'hero__pageTitle'})
            title_text = title.find('span').text if title else ''
            original_title = ''
            original_title_element = soup.find('div', class_='sc-cb6a22b2-1 kEdApw baseAlt')
            if original_title_element:
                original_title_text = original_title_element.get_text(strip=True)
                original_title = original_title_text.replace('Título original:', '').strip()
            year = ''
            year_element = soup.find('a', {'class': re.compile(r'ipc-link.*titleYear')})
            if year_element:
                year_match = re.search(r'\d{4}', year_element.text)
                if year_match:
                    year = year_match.group(0)
            if not year:
                release_element = soup.find('a', {'data-testid': re.compile(r'release-date-item|title-details-releasedate')})
                if release_element:
                    year_match = re.search(r'\d{4}', release_element.text)
                    if year_match:
                        year = year_match.group(0)
            if not year:
                meta_elements = soup.find_all('li', {'data-testid': re.compile(r'title-details-releaseyear|title-techspec_release')})
                for elem in meta_elements:
                    year_match = re.search(r'\d{4}', elem.text)
                    if year_match:
                        year = year_match.group(0)
                        break
            if not year:
                release_date = soup.find('span', class_='sc-1f719d57-1 ePuhDr')
                if release_date:
                    year_match = re.search(r'\d{4}', release_date.text)
                    if year_match:
                        year = year_match.group(0)
            return title_text, original_title, year
        except:
            return '', '', ''

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
        except:
            pass
        headers_embed = {
            'User-Agent': USER_AGENT,
            'Referer': cls.__site_url__[-1]
        }
        try:
            r1 = requests.get(getembed_url, headers=headers_embed)
            if r1.status_code != 200:
                return None
        except:
            return None
        id_ = meta.get('id')
        sv = meta.get('sv')
        play_url = f"https://etv-embed.help/e/getplay.php?id={id_}&sv={sv}"
        try:
            r2 = requests.get(play_url, headers={'user-agent': USER_AGENT, 'Referer': getembed_url}, allow_redirects=True)
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
        except:
            return None

    @classmethod
    def search_movies(cls, imdb, year):
        links = []
        title, original_title, imdb_year = cls.find_title(imdb)
        if not title and not original_title:
            return links
        try:
            query = quote_plus(title)
            search_url = cls.__site_url__[-1].rstrip('/') + '/pesquisar/?p=' + query
            r = cfscraper.get(search_url)
            if not r or r.status_code != 200 or "captcha" in r.text.lower():
                return links
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all('a', href=re.compile(r'/assistir-.*-\d{4}-[^/]+'))
            movie_urls = {}
            for item in results:
                href = urljoin(cls.__site_url__[-1], item['href'])
                found_title = None
                caption_div = item.find('div', class_='caption')
                if caption_div:
                    found_title = caption_div.find(text=True, recursive=False)
                    if found_title:
                        found_title = found_title.strip()
                if not found_title:
                    for tag in ['span', 'h2', 'div', 'p']:
                        title_element = item.find(tag, class_=re.compile(r'title|name|movie-title|text', re.I))
                        if title_element:
                            found_title = title_element.get_text(strip=True)
                            break
                if not found_title:
                    found_title = item.get_text(strip=True)
                found_title_cleaned = re.sub(r'(?i)(dublado|legendado|\d{4}\d+min$)', '', found_title).strip()
                y_match = re.search(r'-(\d{4})-([^/]+)/?$', href)
                found_year = y_match.group(1) if y_match else None
                title_similarity = difflib.SequenceMatcher(None, title, found_title_cleaned).ratio() * 100
                original_title_similarity = difflib.SequenceMatcher(None, original_title, found_title_cleaned).ratio() * 100 if original_title else 0
                max_similarity = max(title_similarity, original_title_similarity)
                if max_similarity >= 70 and found_year and int(year) == int(found_year):
                    if not imdb_year or (imdb_year and found_year == imdb_year):
                        if 'dublado' in href.lower():
                            movie_urls['dublado'] = href
                        elif 'legendado' in href.lower():
                            movie_urls['legendado'] = href
            if not movie_urls:
                return links
            r = cfscraper.get(f"{movie_urls.get('dublado', movie_urls.get('legendado', ''))}?area=online", headers={'Referer': cls.__site_url__[-1]})
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
                    lang_url = f"{movie_urls.get('dublado', movie_urls.get('legendado', ''))}?area=online&audio={lang}"
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
        except:
            return links

    @classmethod
    def search_tvshows(cls, imdb, year, season, episode):
        links = []
        title, original_title, imdb_year = cls.find_title(imdb)
        if not title:
            return links
        try:
            query = quote_plus(title)
            search_url = cls.__site_url__[-1].rstrip('/') + '/pesquisar/?p=' + query
            r = cfscraper.get(search_url)
            if not r or r.status_code != 200 or "captcha" in r.text.lower():
                return links
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all('a', href=re.compile(r'/assistir-.*-\d{4}-[^/]+'))
            series_urls = {}
            for item in results:
                href = urljoin(cls.__site_url__[-1], item['href'])
                found_title = None
                caption_div = item.find('div', class_='caption')
                if caption_div:
                    found_title = caption_div.find(text=True, recursive=False)
                    if found_title:
                        found_title = found_title.strip()
                if not found_title:
                    for tag in ['span', 'h2', 'div', 'p']:
                        title_element = item.find(tag, class_=re.compile(r'title|name|movie-title|text', re.I))
                        if title_element:
                            found_title = title_element.get_text(strip=True)
                            break
                if not found_title:
                    found_title = item.get_text(strip=True)
                found_title_cleaned = re.sub(r'(?i)(dublado|legendado|\d{4}\d+min$)', '', found_title).strip()
                y_match = re.search(r'-(\d{4})-([^/]+)/?$', href)
                found_year = y_match.group(1) if y_match else None
                title_similarity = difflib.SequenceMatcher(None, title, found_title_cleaned).ratio() * 100
                original_title_similarity = difflib.SequenceMatcher(None, original_title, found_title_cleaned).ratio() * 100 if original_title else 0
                max_similarity = max(title_similarity, original_title_similarity)
                if max_similarity >= 70 and found_year:
                    if not imdb_year or (imdb_year and found_year == imdb_year):
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
                    if lang == 'legendado' and series_urls.get('dublado'):
                        series_url = series_urls['dublado'].replace('dublado', 'legendado')
                if not series_url:
                    continue
                r = cfscraper.get(series_url, headers={'Referer': cls.__site_url__[-1]})
                if not r or r.status_code != 200 or "captcha" in r.text.lower():
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                episode_links = soup.find_all('a', href=re.compile(r'/assistir-.*-(\d+)x(\d+)-([a-z]+)(?:-[a-z0-9]+)?-\d+/?$'))
                episode_url = None
                for item in episode_links:
                    href = urljoin(cls.__site_url__[-1], item['href'])
                    ep_match = re.search(r'-(\d+)x(\d+)-([a-z]+)(?:-[a-z0-9]+)?-(\d+)/?$', href, re.I)
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
                    season_url = f"{series_url.rstrip('/')}?temporada={season}"
                    r_season = cfscraper.get(season_url, headers={'Referer': cls.__site_url__[-1]})
                    if r_season and r_season.status_code == 200 and "captcha" not in r_season.text.lower():
                        soup_season = BeautifulSoup(r_season.text, 'html.parser')
                        episode_links = soup_season.find_all('a', href=re.compile(r'/assistir-.*-(\d+)x(\d+)-([a-z]+)(?:-[a-z0-9]+)?-\d+/?$'))
                        for item in episode_links:
                            href = urljoin(cls.__site_url__[-1], item['href'])
                            ep_match = re.search(r'-(\d+)x(\d+)-([a-z]+)(?:-[a-z0-9]+)?-(\d+)/?$', href, re.I)
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
        except:
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
        except:
            pass
        return streams

    @classmethod
    def resolve_tvshows(cls, url):
        return cls.resolve_movies(url)