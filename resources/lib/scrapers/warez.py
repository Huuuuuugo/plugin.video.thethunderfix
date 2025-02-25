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
    @classmethod
    def warezcdn_servers(cls, imdb, season=False, episode=False):
        links = []
        if season and episode:
            # get series page
            referer_url = 'https://embed.warezcdn.link/serie/%s' % (str(imdb))
            data = requests.get(referer_url).text

            # extract url to get seasons information
            season_url = re.compile(r"var cachedSeasons\s*=\s*(?P<url>'(?:[^\']+)'|\"([^\"]+)\")", re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(data)[0][1]
            season_url = 'https://embed.warezcdn.link/' + season_url

            # get seasons information
            seasons_info = requests.get(season_url, headers={'Referer': referer_url}).json()['seasons']

            # search for specified season and episode
            episode_info = {}
            for key in seasons_info.keys():
                season_dict = seasons_info[key]
                if season_dict['name'] == str(season):
                    # search for specified episode
                    for key in season_dict['episodes'].keys():
                        episode_dict = season_dict['episodes'][key]
                        if episode_dict['name'] == str(episode):
                            episode_info = episode_dict
                            break
            
            # request audio data
            request_url = 'https://embed.warezcdn.link/core/ajax.php?audios=%s' % episode_dict['id']

            audio_ids = requests.get(
                request_url,
                headers={'Referer': referer_url}
                ).json()
            audio_ids = json.loads(audio_ids)
                        
            if audio_ids:
                for audio in audio_ids:
                    if int(audio['audio']) == 1:
                        lg = english
                    elif int(audio['audio']) == 2:
                        lg = portuguese

                    servers = ['warezcdn', 'mixdrop']
                    for server in servers:
                        if server in audio['servers']:
                            embed_referer_url = 'https://embed.warezcdn.link/getEmbed.php?id=%s&sv=%s&lang=%s' % (audio['id'], server, audio['audio'])
                            play_url = 'https://embed.warezcdn.link/getPlay.php?id=%s&sv=%s' % (audio['id'], server)

                            # get referer urls to avoid bot detection
                            requests.get(referer_url)
                            requests.get(
                                embed_referer_url,
                                headers={'Referer': referer_url}
                                )
                            
                            # get embed play html
                            play_response = requests.get(
                                play_url,
                                headers={'Referer': embed_referer_url}
                                ).text

                            # extract video url from play_response
                            video_url = re.compile(r"window.location.href = (?:\'|\")(.+)(?:\'|\")").findall(play_response)[0]
                            
                            # save name and url to the list of links
                            name = server.upper() + ' - ' + lg
                            links.append((name, video_url))

        else:
            # movie page url
            referer_url = 'https://embed.warezcdn.link/filme/%s' % imdb

            # request html content of the movie page
            data = requests.get(referer_url).text

            # extract audio data from the html content
            audio_ids = re.compile(r"let data = (?:\'|\")(\[.+\])(?:\'|\")").findall(data)
            audio_ids = json.loads(audio_ids[0])
            
            if audio_ids:
                for audio in audio_ids:
                    if int(audio['audio']) == 1:
                        lg = english
                    elif int(audio['audio']) == 2:
                        lg = portuguese

                    servers = ['warezcdn', 'mixdrop']
                    for server in servers:
                        if server in audio['servers']:
                            embed_referer_url = 'https://embed.warezcdn.link/getEmbed.php?id=%s&sv=%s&lang=%s' % (audio['id'], server, audio['audio'])
                            play_url = 'https://embed.warezcdn.link/getPlay.php?id=%s&sv=%s' % (audio['id'], server)

                            # get referer urls to avoid bot detection
                            requests.get(referer_url)
                            requests.get(
                                embed_referer_url,
                                headers={'Referer': referer_url}
                                )
                            
                            # get embed play html
                            play_response = requests.get(
                                play_url,
                                headers={'Referer': embed_referer_url}
                                ).text

                            # extract video url from play_response
                            video_url = re.compile(r"window.location.href = (?:\'|\")(.+)(?:\'|\")").findall(play_response)[0]
                            
                            # save name and url to the list of links
                            name = server.upper() + ' - ' + lg
                            links.append((name, video_url))

        return links
    
    @classmethod
    def search_movies(cls, imdb, year):
        try:
            return cls.warezcdn_servers(imdb, False, False)
        except:
            return []      
    
    @classmethod
    def resolve_movies(cls, url):
        streams = []
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        if url:
            # extract subtitles url
            try:
                sub = url.split('http')[2]
                sub = 'http%s' % sub
                try:
                    sub = sub.split('&')[0]
                except:
                    pass
                if not '.srt' in sub:
                    sub = ''
            except:
                sub = ''

            # extract video src
            try:
                stream = url.split('?')[0]
            except:
                try:
                    stream = url.split('#')[0]
                except:
                    pass
            
            # extract mp4 link from mixdrop
            if 'mixdrop' in url:
                try:
                    # requests html for the video player on mixdrop
                    video_html_response = requests.get(
                        url,
                        headers={"User-Agent": user_agent}
                    )
                    video_html_response = video_html_response.text
                    
                    # deobfuscate js code
                    js_matches = re.compile(r"eval\((.+)\)").findall(video_html_response)
                    for packed_js in js_matches:
                        if 'delivery' in packed_js:
                            mdcore = jsunpack.unpack(packed_js)
                    
                    stream = 'https:' + re.compile(r"MDCore.wurl=\"(.+?)\"").findall(mdcore)[0] +'|user-agent=%s' %user_agent

                except:
                    pass

            # extract m3u8 links from warezcdn
            else:
                try:
                    stream_data = re.compile(r"(https://.+/)video/(.+)").findall(stream)[0]
                    host_url, video_id = stream_data

                    # make request for master.m3u8 url based on data from video_html_url
                    master_request_url = '%splayer/index.php?data=%s&do=getVideo' % (host_url, video_id)

                    master_m3u8_url = requests.post(
                        master_request_url,
                        data={'hash': video_id, 'r': ''},
                        headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://embed.warezcdn.link/'},
                        allow_redirects=True
                    )
                    master_m3u8_url = master_m3u8_url.text
                    master_m3u8_url = json.loads(master_m3u8_url)['videoSource']

                    # extract the url for the playlist containing all the parts from master.m3u8
                    master_m3u8 = requests.get(master_m3u8_url, headers={'Referer': 'https://embed.warezcdn.link/'}).text
                    for line in master_m3u8.split('\n'):
                        matches = re.compile(r"https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})(:\d+)?(/[^\s]*)?").match(line)
                        if matches:
                            stream = matches[0]
                            break
                except:
                    pass

            # append results
            streams.append((stream, sub, user_agent))
        return streams
    
    @classmethod
    def search_tvshows(cls, imdb, year, season, episode):
        try:
            return cls.warezcdn_servers(imdb, season, episode)
        except:
            return []  

    @classmethod
    def resolve_tvshows(cls, url):
        streams = []
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
        if url:
            # extract subtitles url
            try:
                sub = url.split('http')[2]
                sub = 'http%s' % sub
                try:
                    sub = sub.split('&')[0]
                except:
                    pass
                if not '.srt' in sub:
                    sub = ''
            except:
                sub = ''

            # extract video src
            try:
                stream = url.split('?')[0]
            except:
                try:
                    stream = url.split('#')[0]
                except:
                    pass
            
            # extract mp4 link from mixdrop
            if 'mixdrop' in url:
                try:
                    # requests html for the video player on mixdrop
                    video_html_response = requests.get(
                        url,
                        headers={"User-Agent": user_agent}
                    )
                    video_html_response = video_html_response.text
                    
                    # deobfuscate js code
                    js_matches = re.compile(r"eval\((.+)\)").findall(video_html_response)
                    for packed_js in js_matches:
                        if 'delivery' in packed_js:
                            mdcore = jsunpack.unpack(packed_js)
                    
                    stream = 'https:' + re.compile(r"MDCore.wurl=\"(.+?)\"").findall(mdcore)[0] +'|user-agent=%s' %user_agent

                except:
                    pass

            # extract m3u8 links from warezcdn
            else:
                try:
                    stream_data = re.compile(r"(https://.+/)video/(.+)").findall(stream)[0]
                    host_url, video_id = stream_data

                    # make request for master.m3u8 url based on data from video_html_url
                    master_request_url = '%splayer/index.php?data=%s&do=getVideo' % (host_url, video_id)

                    master_m3u8_url = requests.post(
                        master_request_url,
                        data={'hash': video_id, 'r': ''},
                        headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://embed.warezcdn.link/'},
                        allow_redirects=True
                    )
                    master_m3u8_url = master_m3u8_url.text
                    master_m3u8_url = json.loads(master_m3u8_url)['videoSource']

                    # extract the url for the playlist containing all the parts from master.m3u8
                    master_m3u8 = requests.get(master_m3u8_url, headers={'Referer': 'https://embed.warezcdn.link/'}).text
                    for line in master_m3u8.split('\n'):
                        matches = re.compile(r"https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})(:\d+)?(/[^\s]*)?").match(line)
                        if matches:
                            stream = matches[0]
                            break
                except:
                    pass

            # append results
            streams.append((stream, sub, user_agent))
        return streams
