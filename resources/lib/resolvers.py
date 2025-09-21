# -*- coding: utf-8 -*-
import re
try:
    from kodi_helper import requests, urlparse, quote_plus
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
    from resources.lib.unblock import unblock as requests
    addonId = re.search('plugin://(.+?)/',str(sys.argv[0])).group(1)
    addon = myAddon(addonId)
    log = addon.log
except:
    pass

import random



class Resolver:
    IE_USER_AGENT = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 OPR/67.0.3575.97'
    IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Safari/604.1'
    IPAD_USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
    ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 9; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36'
    EDGE_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
    CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'        
    SAFARI_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15'
    USER_AGENTS = [FF_USER_AGENT, OPERA_USER_AGENT, EDGE_USER_AGENT, CHROME_USER_AGENT, SAFARI_USER_AGENT]
    _headers = {'User-Agent': CHROME_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
                'sec-ch-ua': '"Chromium";v="115", "Not A(Brand";v="99", "Google Chrome";v="115"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
    }     

    @classmethod
    def rand_ua(cls):
        RAND_UA = random.choice(cls.USER_AGENTS)
        return RAND_UA

    @classmethod
    def append_headers(cls,headers):
        return '|%s' % '&'.join(['%s=%s' % (key, quote_plus(headers[key])) for key in headers])
    
    @classmethod
    def get_packed_data(cls,html):
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
                    for r in t:
                        if jsunpack.detect(r):
                            packed_data += jsunpack.unpack(r)
        except:
            pass
        return packed_data    

    @classmethod
    def resolve_mixdrop(cls,url,referer):
        url = url.replace('.club', '.co')
        try:
            url = url.split('?')[0]
        except:
            pass
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        try:
            #r = requests.head(url,headers={'User-Agent': cls.rand_ua()},allow_redirects=True)
            r = requests.head(url,headers={'User-Agent': user_agent},allow_redirects=True)
            url = r.url
        except:
            pass
        stream = ''
        parsed_uri = urlparse(url)
        protocol = parsed_uri.scheme
        host = parsed_uri.netloc
        # if host.endswith('.club'):
        #     host = host.replace('.club', '.co')
        rurl = 'https://%s/'%host
        if referer:
            rurl = referer   
        #headers = {'Origin': rurl[:-1],'Referer': rurl, 'User-Agent': cls.rand_ua()}
        headers = {'Origin': rurl[:-1],'Referer': rurl, 'User-Agent': user_agent}
        try:
            html = requests.get(url,headers=headers,allow_redirects=True).text
            r = re.search(r'location\s*=\s*"([^"]+)', html)
            if r:
                url = 'https://%s%s'%(host,r.group(1))
                html = requests.get(url,headers=headers,allow_redirects=True).text
            if '(p,a,c,k,e,d)' in html:
                html = cls.get_packed_data(html)
            r = re.search(r'(?:vsr|wurl|surl)[^=]*=\s*"([^"]+)', html)
            if r:
                surl = r.group(1)
                if surl.startswith('//'):
                    surl = 'https:' + surl
                #headers.pop('Origin')
                headers.update({'Referer': url})
                # headers.update({'Origin': 'https://mdzsmutpcvykb.net'})
                # headers.update({'Referer': 'https://mdzsmutpcvykb.net/'})
                stream = surl + cls.append_headers(headers)
        except:
            pass
        return stream
    
    @classmethod
    def resolve_brplayer(cls,url):
        parsed_uri = urlparse(url)
        protocol = parsed_uri.scheme
        host = parsed_uri.netloc        
        try:
            headers = {'User-Agent': cls.FF_USER_AGENT}
            html = requests.get(url,headers=headers).text
            r = re.search(r'sniff\("[^"]+","([^"]+)","([^"]+)".+?],([^,]+)', html)
            if r:
                source = "https://{0}/m3u8/{1}/{2}/master.txt?s=1&cache={3}".format(
                    host, r.group(1), r.group(2), r.group(3)
                ) 
                headers.update({'Referer': url})
                return source + cls.append_headers(headers)
        except:
            pass
        return ''              



    
    @classmethod
    def last_url(cls,url,headers):
        stream = ''
        try:
            r = requests.head(url,headers=headers,allow_redirects=True)
            stream = r.url
        except:
            pass
        return stream
    
    @classmethod
    def resolve_streamtape(cls,url,referer):
        link = ''
        try:
            correct_url = url.replace('/v/', '/e/')
            try:
                r = requests.head(correct_url,headers=cls._headers,allow_redirects=True)
                correct_url = r.url
            except:
                pass            
            parsed_uri = urlparse(correct_url)
            protocol = parsed_uri.scheme
            host = parsed_uri.netloc
            if not referer:
                referer = '%s://%s/'%(protocol,host)
            headers = cls._headers
            headers.update({'Referer': referer})
            r = requests.get(correct_url,headers=headers)
            data = r.text
            link_part1_re = re.compile('<div.+?style="display:none;">(.*?)&token=.+?</div>').findall(data)
            link_part2_re = re.compile("&token=(.*?)'").findall(data)
            if link_part1_re and link_part2_re:
                part1 = link_part1_re[0]
                part2 = link_part2_re[-1]
                part1 = part1.replace(' ', '')
                if 'streamtape' in part1:
                    try:
                        part1 = part1.split('streamtape')[1]
                        final = 'streamtape' + part1 + '&token=' + part2
                        stream = 'https://' + final + '&stream=1'
                        last_stream = cls.last_url(stream,headers=headers)
                        if last_stream:
                            link = last_stream + cls.append_headers(headers)
                        else:
                            link = ''
                    except:
                        link = ''
                elif 'get_video' in part1:
                    try:
                        part1_1 = part1.split('get_video')[0]
                        part1_2 = part1.split('get_video')[1]
                        part1_1 = part1_1.replace('/', '')
                        part1 = part1_1 + '/get_video' + part1_2
                        final = part1 + '&token=' + part2
                        stream = 'https://' + final + '&stream=1'
                        last_stream = cls.last_url(stream,headers=headers)
                        if last_stream:
                            link = last_stream + cls.append_headers(headers)
                        else:
                            link = ''
                    except:
                        link = ''
        except:
            pass           
        return link

    @classmethod
    def resolverurls(cls,url,referer):
        try:
            log('Resolving: %s'%url)
        except:
            pass
        stream = ''
        sub = ''
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain = domain.replace('www.', '').replace('ww3.', '').replace('ww4.', '')
        #streamtape
        if domain in ['streamtape.com', 'strtape.cloud', 'streamtape.net', 'streamta.pe', 'streamtape.site',
               'strcloud.link', 'strtpe.link', 'streamtape.cc', 'scloud.online', 'stape.fun',
               'streamadblockplus.com', 'shavetape.cash', 'streamtape.to', 'streamta.site',
               'streamadblocker.xyz', 'tapewithadblock.org', 'adblocktape.wiki', 'streamtape']:
            stream = cls.resolve_streamtape(url,referer)
        #mixdrop
        elif domain in ['mixdrop.co', 'mixdrop.to', 'mixdrop.sx', 'mixdrop.bz', 'mixdrop.ch',
               'mixdrp.co', 'mixdrp.to', 'mixdrop.gl', 'mixdrop.club', 'mixdroop.bz',
               'mixdroop.co', 'mixdrop.vc', 'mixdrop.ag', 'mdy48tn97.com',
               'md3b0j6hj.com', 'mdbekjwqa.pw', 'mdfx9dc8n.net', 'mdzsmutpcvykb.net', 'mixdrop.is', 'mixdrop']:
            stream = cls.resolve_mixdrop(url,referer)
        elif domain in ['brplayer.site', 'watch.brplayer.site']:
            stream = cls.resolve_brplayer(url)
        return stream, sub 

    
def resolveurl(url,referer):
    stream, sub = Resolver.resolverurls(url,referer)
    return stream, sub

# stream, sub = resolveurl('https://watch.brplayer.site/watch?v=CERF23T1', '')
# print(stream)

