# -*- coding: utf-8 -*-
import re
import json
import base64
import random
import string
import time
import urllib.parse
try:
    from kodi_helper import urlparse, quote_plus
    import requests
except ImportError:
    import requests
    from urllib.parse import urlparse, quote_plus
try:
    from resources.lib import jsunpack
except ImportError:
    import jsunpack
try:
    import sys
    from kodi_helper import myAddon
    addonId = re.search('plugin://(.+?)/',str(sys.argv[0])).group(1)
    addon = myAddon(addonId)
except:
    pass

class Resolver:
    IE_USER_AGENT = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
    OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 OPR/126.0.0.0'
    IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1'
    IPAD_USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1'
    ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'
    EDGE_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
    CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'        
    SAFARI_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15'
    USER_AGENTS = [FF_USER_AGENT, OPERA_USER_AGENT, EDGE_USER_AGENT, CHROME_USER_AGENT, SAFARI_USER_AGENT]
    _headers = {'User-Agent': CHROME_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="140", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
    }     

    @classmethod
    def rand_ua(cls):
        return random.choice(cls.USER_AGENTS)

    @classmethod
    def append_headers(cls, headers):
        return '|%s' % '&'.join(['%s=%s' % (key, quote_plus(headers[key])) for key in headers])

    @classmethod
    def get_packed_data(cls, html):
        packed_data = ''
        try:
            for match in re.finditer(r'''(eval\s*\(function\(p,a,c,k,e,.*?)</script>''', html, re.DOTALL | re.I):
                r = match.group(1)
                t = re.findall(r'(eval\s*\(function\(p,a,c,k,e,)', r, re.DOTALL | re.IGNORECASE)
                if len(t) == 1:
                    if jsunpack.detect(r):
                        packed_data += jsunpack.unpack(r)
                else:
                    t = r.split('eval')
                    t = ['eval' + x for x in t if x]
                    for sub_r in t:
                        if jsunpack.detect(sub_r):
                            packed_data += jsunpack.unpack(sub_r)
        except Exception:
            pass
        return packed_data

    @classmethod
    def tear_decode(cls, data, key):
        dec = ''
        for i in range(len(data)):
            dec += chr(ord(data[i]) ^ ord(key[i % len(key)]))
        return base64.b64decode(dec).decode('utf-8')

    @classmethod
    def dood_decode(cls, data):
        t = string.ascii_letters + string.digits
        return data + ''.join([random.choice(t) for _ in range(10)])

    @classmethod
    def resolve_mixdrop(cls, url, referer):
        stream = ''
        url = url.replace('.club', '.co')
        try:
            url = url.split('?')[0]
        except:
            pass
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
        try:
            r = requests.head(url, headers={'User-Agent': user_agent}, allow_redirects=True)
            url = r.url
        except Exception:
            pass
        parsed_uri = urlparse(url)
        protocol = parsed_uri.scheme
        host = parsed_uri.netloc
        rurl = 'https://%s/' % host
        if referer:
            rurl = referer
        headers = {'Origin': rurl[:-1], 'Referer': rurl, 'User-Agent': user_agent}
        try:
            html = requests.get(url, headers=headers, allow_redirects=True).text
            r = re.search(r'location\s*=\s*["\']([^"\']+?)["\'][^;]*$', html)
            if r:
                location_val = r.group(1)
                if '+' not in location_val and ('e+' not in location_val) and (location_val.startswith('/') or location_val.startswith('http')):
                    new_url = 'https://%s%s' % (host, location_val) if location_val.startswith('/') else location_val
                    url = new_url
                    html = requests.get(url, headers=headers, allow_redirects=True).text
            unpacked = cls.get_packed_data(html)
            full_html = html + unpacked
            patterns = [
                r'MDCore\.wurl\s*=\s*"([^"]+)',
                r'(?:vsr|wurl|surl)[^=]*=\s*"([^"]+)',
                r'sources:\s*\[\s*\{\s*file:\s*"([^"]+)',
                r'file:\s*"([^"]+)"',
                r'"file":"([^"]+)"',
                r'src:\s*"([^"]+)"',
                r'mdcore[^"]*["\']([^"\']+?)["\'][^;]*$'
            ]
            surl = None
            for pat in patterns:
                r = re.search(pat, full_html, re.DOTALL)
                if r:
                    candidate = r.group(1)
                    if candidate.startswith('http') or candidate.startswith('//') or candidate.startswith('/'):
                        surl = candidate
                        break
            if surl:
                if surl.startswith('//'):
                    surl = 'https:' + surl
                elif surl.startswith('/'):
                    surl = 'https://%s%s' % (host, surl)
                headers.update({'Referer': url})
                stream = surl + cls.append_headers(headers)
            else:
                delivery_match = re.search(r'//s-delivery\d+\.mxcontent\.net/[^"]+', full_html)
                if delivery_match:
                    surl = 'https:' + delivery_match.group(0)
                    headers.update({'Referer': url})
                    stream = surl + cls.append_headers(headers)
                else:
                    mdcore_match = re.search(r'mdcore\.player\([^)]+"([^"]+)"', full_html)
                    if mdcore_match:
                        surl = mdcore_match.group(1)
                        if surl.startswith('//'):
                            surl = 'https:' + surl
                        headers.update({'Referer': url})
                        stream = surl + cls.append_headers(headers)
        except Exception:
            pass
        return stream

    @classmethod
    def resolve_streamtape(cls, url, referer):
        link = ''
        try:
            correct_url = url.replace('/v/', '/e/')
            try:
                r = requests.head(correct_url, headers=cls._headers, allow_redirects=True)
                correct_url = r.url
            except Exception:
                pass
            parsed_uri = urlparse(correct_url)
            protocol = parsed_uri.scheme
            host = parsed_uri.netloc
            if not referer:
                referer = '%s://%s/' % (protocol, host)
            headers = cls._headers.copy()
            headers.update({'Referer': referer})
            r = requests.get(correct_url, headers=headers)
            data = r.text
            src = re.findall(r'''ById\('.+?=\s*(["']//[^;<]+)''', data)
            if src:
                src_url = ''
                parts = src[-1].replace("'", '"').split('+')
                for part in parts:
                    p1 = re.findall(r'"([^"]*)', part)[0]
                    p2 = 0
                    if 'substring' in part:
                        subst = re.findall(r'substring\((\d+)', part)
                        for sub in subst:
                            p2 += int(sub)
                    src_url += p1[p2:]
                src_url += '&stream=1'
                if src_url.startswith('//'):
                    src_url = 'https:' + src_url
                last_stream = cls.last_url(src_url, headers=headers)
                if last_stream:
                    link = last_stream + cls.append_headers(headers)
        except Exception:
            pass
        return link

    @classmethod
    def resolve_filemoon(cls, url, referer):
        stream = ''
        try:
            from urllib.parse import urljoin, unquote
            parsed = urlparse(url)
            host = parsed.netloc
            if '|' in url or '%7C' in url:
                decoded_url = unquote(url)
                if '|' in decoded_url:
                    filemoon_url, direct_stream = decoded_url.split('|', 1)
                    if direct_stream.startswith('http'):
                        play_headers = {
                            'User-Agent': cls.CHROME_USER_AGENT,
                            'Referer': f'https://{host}/',
                            'Origin': f'https://{host}'
                        }
                        stream = direct_stream + cls.append_headers(play_headers)
                        return stream
            media_id = parsed.path.split('/')[-1].split('?')[0]
            if '$$' in media_id:
                media_id, ref = media_id.split('$$')
                referer = urljoin(ref, '/')
            if '/' in media_id:
                media_id = media_id.split('/')[0]
            web_url = f"https://{host}/e/{media_id}"
            headers = {
                'User-Agent': cls.CHROME_USER_AGENT,
                'Cookie': '__ddg1_=PZYJSmASXDCQGP6auJU9; __ddg2_=hxAe1bBqtlYhVSik'
            }
            if referer:
                headers['Referer'] = referer
            r = requests.get(web_url, headers=headers)
            html = r.text
            if '<h1>Page not found</h1>' in html or '<h1>This video cannot be watched under this domain</h1>' in html:
                web_url = web_url.replace('/e/', '/d/')
                r = requests.get(web_url, headers=headers)
                html = r.text
            match = re.search(r'<iframe\s*src="([^"]+)', html, re.DOTALL)
            if match:
                iframe_url = match.group(1)
                if not iframe_url.startswith('http'):
                    iframe_url = f"https://{host}{iframe_url}"
                headers.update({
                    'accept-language': 'en-US,en;q=0.9',
                    'sec-fetch-dest': 'iframe',
                    'Referer': web_url
                })
                r = requests.get(iframe_url, headers=headers)
                html = r.text
            html += cls.get_packed_data(html)
            match = re.search(r'var\s*postData\s*=\s*(\{.+?\})', html, re.DOTALL)
            if match:
                postdata_str = match.group(1)
                try:
                    postdata = json.loads(postdata_str)
                    edata_list = postdata.get('eData', [])
                    if edata_list:
                        edata = edata_list[0]
                        file_data = edata.get('file')
                        seed = edata.get('seed')
                        if file_data and seed:
                            surl = cls.tear_decode(file_data, seed)
                            if surl:
                                play_headers = {
                                    'User-Agent': headers['User-Agent'],
                                    'Referer': web_url,
                                    'Origin': urljoin(web_url, '/')[:-1]
                                }
                                stream = surl + cls.append_headers(play_headers)
                                return stream
                except Exception:
                    pass
            match = re.search(r'sources:\s*\[{\s*file:\s*"([^"]+)', html, re.DOTALL)
            if match:
                surl = match.group(1)
                play_headers = {
                    'User-Agent': headers['User-Agent'],
                    'Referer': web_url,
                    'Origin': urljoin(web_url, '/')[:-1]
                }
                stream = surl + cls.append_headers(play_headers)
            else:
                file_patterns = [
                    r'file:\s*"([^"]+)"',
                    r'"file":"([^"]+)"',
                    r'src:\s*"([^"]+)"'
                ]
                for pat in file_patterns:
                    match = re.search(pat, html, re.DOTALL)
                    if match:
                        surl = match.group(1)
                        play_headers = {
                            'User-Agent': headers['User-Agent'],
                            'Referer': web_url,
                            'Origin': urljoin(web_url, '/')[:-1]
                        }
                        stream = surl + cls.append_headers(play_headers)
                        break
        except Exception:
            pass
        return stream

    @classmethod
    def resolve_doodstream(cls, url, referer):
        stream = ''
        subtitles = {}
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            if any(host.endswith(x) for x in ['.cx', '.wf']):
                host = 'dood.so'
            if host not in ['doodstream.com', 'vidply.com', 'all3do.com', 'vide0.net', 'dsvplay.com']:
                host = 'dsvplay.com'
            media_id = re.search(r'/[de]/([0-9a-zA-Z]+)', url).group(1)
            web_url = f"https://{host}/d/{media_id}"
            headers = {'User-Agent': cls.FF_USER_AGENT, 'Referer': f'https://{host}/'}
            r = requests.get(web_url, headers=headers, allow_redirects=True)
            if r.url != web_url:
                host = re.findall(r'(?://|\.)([^/]+)', r.url)[0]
                web_url = f"https://{host}/d/{media_id}"
            headers['Referer'] = web_url
            html = r.text
            matches = re.findall(r"""dsplayer\.addRemoteTextTrack\({src:'([^']+)',\s*label:'([^']*)',kind:'captions'""", html)
            if matches:
                matches = [(src, label) for src, label in matches if len(label) > 1]
                for src, label in matches:
                    subtitles[label] = 'https:' + src if src.startswith('//') else src
            match = re.search(r'<iframe\s*src="([^"]+)', html)
            if match:
                iframe = match.group(1)
                iframe_url = f"https://{host}{iframe}"
                r = requests.get(iframe_url, headers=headers)
                html = r.text
            else:
                alt_url = web_url.replace('/d/', '/e/')
                r = requests.get(alt_url, headers=headers)
                html = r.text
            match = re.search(r'''dsplayer\.hotkeys[^']+'([^']+).+?function\s*makePlay.+?return[^?]+([^"]+)''', html, re.DOTALL)
            if match:
                token = match.group(2)
                api_path = match.group(1)
                api_url = f"https://{host}{api_path}"
                r = requests.get(api_url, headers=headers)
                html = r.text
                if 'cloudflarestorage.' in html:
                    stream = html.strip() + cls.append_headers(headers)
                else:
                    decoded = cls.dood_decode(html)
                    timestamp = str(int(time.time() * 1000))
                    stream = decoded + token + timestamp + cls.append_headers(headers)
        except Exception:
            pass
        return stream, subtitles

    @classmethod
    def resolve_warezcdn(cls, url, referer):
        stream = ''
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            media_id = re.search(r'/video/([A-Za-z0-9]+)', url).group(1)
            user_agent = cls.CHROME_USER_AGENT
            if host.endswith(".cyou") and media_id.startswith("m3/"):
                headers = {'User-Agent': user_agent}
                stream_url = f"https://{host}/{media_id}" + cls.append_headers(headers)
                return stream_url
            master_request_url = f'https://{host}/player/index.php?data={media_id}&do=getVideo'
            origin_url = f'https://{host}/'
            headers = {
                'User-Agent': user_agent,
                'Origin': origin_url.rstrip('/'),
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://embed.warezcdn.cc/'
            }
            r = requests.post(master_request_url, data={'hash': media_id, 'r': ''}, headers=headers)
            data_json = r.json()
            if 'securedLink' in data_json and data_json['securedLink']:
                headers.pop('X-Requested-With', None)
                stream = data_json['securedLink'] + cls.append_headers(headers)
            elif 'videoSource' in data_json and data_json['videoSource']:
                master_m3u8_url = data_json['videoSource']
                r = requests.get(master_m3u8_url, headers={'Referer': 'https://embed.warezcdn.cc/', 'User-Agent': user_agent})
                playlist = r.text
                base_url = master_m3u8_url.rsplit("/", 1)[0] + "/"
                for line in playlist.split('\n'):
                    if line.strip():
                        if not line.startswith("http"):
                            line = base_url + line
                        line = quote_plus(line, safe=':/?&=%')
                        stream = line + cls.append_headers({'User-Agent': user_agent})
                        break
        except Exception:
            pass
        return stream

    @classmethod
    def resolve_brplayer(cls, url):
        parsed_uri = urlparse(url)
        protocol = parsed_uri.scheme
        host = parsed_uri.netloc        
        try:
            headers = {'User-Agent': cls.FF_USER_AGENT}
            html = requests.get(url, headers=headers).text
            r = re.search(r'sniff\("[^"]+","([^"]+)","([^"]+)".+?],([^,]+)', html)
            if r:
                group1, group2, group3 = r.groups()
                source = "https://{0}/m3u8/{1}/{2}/master.txt?s=1&cache={3}".format(host, group1, group2, group3)
                headers.update({'Referer': url})
                final = source + cls.append_headers(headers)
                return final
        except Exception:
            pass
        return ''

    @classmethod
    def last_url(cls, url, headers):
        stream = ''
        try:
            r = requests.head(url, headers=headers, allow_redirects=True)
            stream = r.url
        except Exception:
            pass
        return stream

    @classmethod
    def resolverurls(cls, url, referer):
        stream = ''
        sub = ''
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain = domain.replace('www.', '').replace('ww3.', '').replace('ww4.', '')
        streamtape_domains = [
            'streamtape.com', 'strtape.cloud', 'streamtape.net', 'streamta.pe', 'streamtape.site',
            'strcloud.link', 'strcloud.club', 'strtpe.link', 'streamtape.cc', 'scloud.online', 'stape.fun',
            'streamadblockplus.com', 'shavetape.cash', 'streamtape.to', 'streamta.site',
            'streamadblocker.xyz', 'tapewithadblock.org', 'adblocktape.wiki', 'antiadtape.com',
            'streamtape.xyz', 'tapeblocker.com', 'streamnoads.com', 'tapeadvertisement.com',
            'tapeadsenjoyer.com', 'watchadsontape.com', 'streamtape'
        ]
        mixdrop_domains = [
            'mixdrop.co', 'mixdrop.to', 'mixdrop.sx', 'mixdrop.bz', 'mixdrop.ch',
            'mixdrp.co', 'mixdrp.to', 'mixdrop.gl', 'mixdrop.club', 'mixdroop.bz',
            'mixdroop.co', 'mixdrop.vc', 'mixdrop.ag', 'mdy48tn97.com',
            'md3b0j6hj.com', 'mdbekjwqa.pw', 'mdfx9dc8n.net', 'mixdropjmk.pw',
            'mixdrop21.net', 'mixdrop.is', 'mixdrop.si', 'mixdrop23.net', 'mixdrop.nu',
            'mixdrop.ms', 'mdzsmutpcvykb.net', 'mixdrop.ps', 'mxdrop.to', 'mixdrop.sb',
            'mixdrop.my', 'mixdrop.cv', 'mixdrop'
        ]
        filemoon_domains = [
            'filemoon.sx', 'filemoon.to', 'filemoon.in', 'filemoon.link', 'filemoon.nl',
            'filemoon.wf', 'cinegrab.com', 'filemoon.eu', 'filemoon.art', 'moonmov.pro',
            'kerapoxy.cc', 'furher.in', '1azayf9w.xyz', '81u6xl9d.xyz', 'smdfs40r.skin',
            'bf0skv.org', 'z1ekv717.fun', 'l1afav.net', '222i8x.lol', '8mhlloqo.fun', '96ar.com',
            'xcoic.com', 'f51rm.com', 'c1z39.com', 'boosteradx.online'
        ]
        dood_domains = [
            'dood.watch', 'doodstream.com', 'dood.to', 'dood.so', 'dood.cx', 'dood.la', 'dood.ws',
            'dood.sh', 'doodstream.co', 'dood.pm', 'dood.wf', 'dood.re', 'dood.yt', 'dooood.com',
            'dood.stream', 'ds2play.com', 'doods.pro', 'ds2video.com', 'd0o0d.com', 'do0od.com',
            'd0000d.com', 'd000d.com', 'dood.li', 'dood.work', 'dooodster.com', 'vidply.com',
            'all3do.com', 'do7go.com', 'doodcdn.io', 'doply.net', 'vide0.net', 'vvide0.com',
            'd-s.io', 'dsvplay.com'
        ]
        warez_domains = ["warezcdn.cc", "loldewfwvwvwewefdw.cyou"]
        if domain in streamtape_domains:
            stream = cls.resolve_streamtape(url, referer)
        elif domain in mixdrop_domains:
            stream = cls.resolve_mixdrop(url, referer)
        elif domain in filemoon_domains:
            stream = cls.resolve_filemoon(url, referer)
        elif domain in dood_domains:
            stream, sub = cls.resolve_doodstream(url, referer)
        elif domain in warez_domains:
            stream = cls.resolve_warezcdn(url, referer)
        elif domain in ['brplayer.site', 'watch.brplayer.site']:
            stream = cls.resolve_brplayer(url)
        return stream, sub

def resolveurl(url, referer):
    stream, sub = Resolver.resolverurls(url, referer)
    return stream, sub
