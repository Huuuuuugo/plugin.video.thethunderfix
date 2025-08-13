# -*- coding: utf-8 -*-
from kodi_helper import myAddon, xbmcgui
from resources.lib.autotranslate import AutoTranslate, get_country
from resources.lib import httpclient, sources
import os
import xbmcgui
import xbmcplugin
import sys
import re

class Donate(xbmcgui.WindowDialog):
    def __init__(self):
        addonId = re.search('plugin\://(.+?)/', str(sys.argv[0])).group(1)
        addon = myAddon(addonId)
        translate = addon.translate
        homeDir = addon.homeDir
        pix_image = translate(os.path.join(homeDir, 'resources', 'images', 'qrcode-pix.png'))
        self.image = xbmcgui.ControlImage(440, 145, 400, 400, pix_image)
        self.text = xbmcgui.ControlLabel(
            x=150, y=570, width=1100, height=25,
            label='[B]SE ESSE ADD-ON LHE AGRADA, FAÇA UMA DOAÇÃO VIA PIX ACIMA E MANTENHA ESSE SERVIÇO ATIVO[/B]',
            textColor='white'
        )
        self.text2 = xbmcgui.ControlLabel(
            x=380, y=600, width=1000, height=25,
            label='[B]PRESSIONE VOLTAR PARA SAIR (PRESS BACK TO RETURN)[/B]',
            textColor='white'
        )
        self.addControl(self.image)
        self.addControl(self.text)
        self.addControl(self.text2)


class thunder(myAddon):
    def icon(self, image):
        return self.translate(os.path.join(self.homeDir, 'resources', 'images', '{0}.png'.format(image)))

    def get_preferred_language(self):
        """Retorna o idioma preferido das configurações do addon."""
        try:
            lang_pref = self.getSetting("preferred_language")
            if lang_pref == "0":
                return "DUBLADO"
            else:
                return "LEGENDADO"
        except:
            return "DUBLADO"

    def play(self, url, title, iconimage, fanart, description):
        """Reproduz o vídeo usando o player do Kodi."""
        try:
            li = xbmcgui.ListItem(label=title)
            li.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart': fanart})
            li.setInfo('video', {'title': title, 'plot': description})
            li.setPath(url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
        except Exception as e:
            self.notify(f"Erro ao tentar reproduzir: {e}")

    def is_auto_play_enabled(self):
        """Verifica se o modo automático está ativado (robusto a diferentes APIs)."""
        try:
            import xbmcaddon
            return xbmcaddon.Addon().getSettingBool("auto_play_enabled")
        except Exception:
            try:
                val = self.getSetting("auto_play_enabled")
                return str(val).lower() in ("true", "1", "yes")
            except Exception:
                return False

    def try_resolve_with_fallback(self, menus_links, season, episode):
        """
        Tenta primeiro MIXDROP, depois WAREZCDN como fallback,
        priorizando o idioma configurado nas configurações.
        Retorna (stream, sub) ou (None, None) se falhar.
        """
        try:
            preferred_lang = self.get_preferred_language().upper()

            # 1. Filtra pelos links no idioma preferido
            preferred_links = [link for link in menus_links if preferred_lang in link[0].upper()]
            other_links = [link for link in menus_links if preferred_lang not in link[0].upper()]

            # Função interna para tentar resolver com prioridade MIXDROP > WAREZCDN
            def try_links(links):
                mixdrop_link = next(((lbl, url) for lbl, url in links if "MIXDROP" in lbl.upper()), None)
                if mixdrop_link:
                    print(f"[DEBUG] try_resolve_with_fallback: tentando MIXDROP ({preferred_lang}) -> {mixdrop_link[1]}")
                    stream, sub = sources.select_resolver(mixdrop_link[1], season, episode)
                    if stream:
                        return stream, sub
                    print("[DEBUG] MIXDROP falhou, tentando WAREZCDN...")

                warez_link = next(((lbl, url) for lbl, url in links if "WAREZCDN" in lbl.upper()), None)
                if warez_link:
                    print(f"[DEBUG] try_resolve_with_fallback: tentando WAREZCDN ({preferred_lang}) -> {warez_link[1]}")
                    stream, sub = sources.select_resolver(warez_link[1], season, episode)
                    if stream:
                        return stream, sub
                return None, None

            # 2. Primeiro tenta no idioma preferido
            stream, sub = try_links(preferred_links)
            if stream:
                return stream, sub

            # 3. Se não achar, tenta nos outros idiomas
            if other_links:
                print(f"[DEBUG] Nenhuma stream encontrada no idioma preferido ({preferred_lang}), tentando outros idiomas...")
                stream, sub = try_links(other_links)
                if stream:
                    return stream, sub

            print("[DEBUG] Nenhuma stream válida encontrada")
            return None, None

        except Exception as e:
            print(f"[ERROR] try_resolve_with_fallback: exceção: {e}")
            return None, None

    def auto_play_preferred_language(self, imdb, year, season, episode, video_title, genre, iconimage, fanart, description):
        """
        Reproduz automaticamente priorizando MIXDROP e usando WAREZCDN como fallback.
        """
        try:
            menus_links = sources.show_content(imdb, year, season, episode)
            print(f"[DEBUG] auto_play_preferred_language: menus_links={menus_links}")

            if not menus_links:
                print("[DEBUG] auto_play_preferred_language: nenhuma fonte encontrada")
                return False

            # Resolver com fallback
            stream, sub = self.try_resolve_with_fallback(menus_links, season, episode)

            if not stream:
                print("[DEBUG] auto_play_preferred_language: nenhuma stream válida encontrada")
                return False

            import xbmc
            import xbmcgui
            list_item = xbmcgui.ListItem(label=video_title)
            list_item.setArt({'thumb': iconimage, 'icon': iconimage, 'fanart': fanart})
            if sub:
                list_item.setSubtitles([sub])
            xbmc.Player().play(stream, list_item)
            return True

        except Exception as e:
            print(f"[ERROR] auto_play_preferred_language: exceção geral: {e}")
            return False

    def home(self):
        self.setcontent('videos')        
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Movies') + '[/B]','action': 'movies', 'mediatype': 'video', 'iconimage': self.icon('movies')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Tv shows') + '[/B]','action': 'tv_shows', 'mediatype': 'video', 'iconimage': self.icon('tvshows')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Animes') + '[/B]','action': 'animes', 'mediatype': 'video', 'iconimage': self.icon('animes')})
        if get_country() == 'BR':
            self.addMenuItem({'name':'[B]' + AutoTranslate.language('donation') + '[/B]','action': 'donate', 'mediatype': 'video', 'iconimage': self.icon('donate')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('settings') + '[/B]', 'action': 'settings', 'mediatype': 'video', 'iconimage': self.icon('settings')})
        self.end()

    def movies(self):
        self.setcontent('videos')
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('New movies') + '[/B]','action': 'premiere_movies', 'mediatype': 'video', 'iconimage': self.icon('premiere')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Trending') + '[/B]','action': 'trending_movies', 'mediatype': 'video', 'iconimage': self.icon('trending')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Popular') + '[/B]','action': 'popular_movies', 'mediatype': 'video', 'iconimage': self.icon('popular')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Search') + '[/B]','action': 'search_movies', 'mediatype': 'video', 'iconimage': self.icon('search')})
        self.end()
    
    def tv_shows(self): 
        self.setcontent('videos') 
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('New tv shows') + '[/B]','action': 'premiere_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('premiere')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Trending') + '[/B]','action': 'trending_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('trending')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Popular') + '[/B]','action': 'popular_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('popular')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Search') + '[/B]','action': 'search_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('search')})
        self.end()

    def animes(self): 
        self.setcontent('videos') 
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Animes') + '[/B]','action': 'animes_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('animes')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Movies') + '[/B]','action': 'animes_movies', 'mediatype': 'video', 'iconimage': self.icon('movies')})
        self.end()

    def animes_movies(self): 
        self.setcontent('videos') 
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Popular') + '[/B]','action': 'popular_animes_movies', 'mediatype': 'video', 'iconimage': self.icon('popular')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Search') + '[/B]','action': 'search_movies', 'mediatype': 'video', 'iconimage': self.icon('search')})
        self.end()

    def animes_tv_shows(self): 
        self.setcontent('videos') 
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('New animes') + '[/B]','action': 'premiere_animes', 'mediatype': 'video', 'iconimage': self.icon('premiere')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Popular recent') + '[/B]','action': 'popular_animes', 'mediatype': 'video', 'iconimage': self.icon('popular')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Airing') + '[/B]','action': 'airing_animes', 'mediatype': 'video', 'iconimage': self.icon('airing')})
        self.addMenuItem({'name':'[B]' + AutoTranslate.language('Search') + '[/B]','action': 'search_tv_shows', 'mediatype': 'video', 'iconimage': self.icon('search')})
        self.end()

    def open_movie(self,id):
        src = httpclient.open_movie_api(id)
        try:
            imdb_id = src.get('imdb_id')
            runtime = src.get('runtime')
            genres = src.get('genres')
            external_ids = src.get('external_ids')
            if external_ids:
                imdb_external = external_ids.get('imdb_id')
            else:
                imdb_external = 'false'            
            if runtime:
                runtime = runtime*60
            else:
                runtime = 0
            try:
                runtime = str(runtime)
            except:
                pass
            if genres:
                genres = []
                for genre in src['genres']:
                    genres.append(genre['name']+' /')
                genres[-1]=genres[-1].replace(' /', '')
                genres = ' '.join(genres)
            else:
                genres = ''
            if imdb_id:
                imdb_id = imdb_id
            else:
                imdb_id = imdb_external
        except:
            runtime = ''
            genres = ''
            imdb_id = ''
        return runtime,genres,imdb_id 

    def process_movie(self,results):
        for item_ in results:       
            id = item_.get('id')
            name = item_.get('title')
            original_name = item_.get('original_title')
            release = item_.get('release_date')
            if release:
                year = release.split('-')[0]
                year = str(year)
            else:
                release = 'false'
                year = '0'
            description = item_.get('overview')
            if not description:
                description = ''
            backdrop_path = item_.get('backdrop_path')
            search1 = name
            search2 = original_name
            if backdrop_path:
                fanart = 'https://www.themoviedb.org/t/p/original%s'%backdrop_path
            else:
                fanart = ''
            poster_path = item_.get('poster_path')
            if poster_path:
                iconimage = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2%s'%poster_path
            else:
                iconimage = '' 
            if backdrop_path and poster_path and id and name and original_name:
                if not year == '0':
                    new_name = '%s (%s)'%(name,year)
                else:
                    new_name = name
                duration,genre,imdbnumber = self.open_movie(id)
                item_data = {
                    'name': new_name,
                    'action': 'provider', 'iconimage': iconimage, 
                    'fanart': fanart, 'description': description, 
                    'aired': release, 
                    'duration': duration, 
                    'genre': genre, 
                    'imdbnumber': imdbnumber, 
                    'codec': 'h264', 
                    'video_title': name, 
                    'originaltitle': original_name, 
                    'year': year, 
                    'mediatype': 'movie'}
                self.addMenuItem(item_data,folder=True) 

    def movies_premiere(self,page):
        total_pages,results = httpclient.movies_api(page,'premiere')
        if results:
            total_items = len(results)
            self.process_movie(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_movies_premiere(self,page):    
        next_page = str(int(page) + 1)
        self.setcontent('movies')
        total_pages, total_items = self.movies_premiere(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'premiere_movies',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'movie'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def movies_trending(self,page):
        total_pages,results = httpclient.movies_api(page,'trending') 
        if results:
            total_items = len(results)
            self.process_movie(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_movies_trending(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('movies')
        total_pages, total_items = self.movies_trending(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'trending_movies',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'movie'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def movies_popular(self,page):
        total_pages,results = httpclient.movies_popular_api(page) 
        if results:
            total_items = len(results)
            self.process_movie(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_movies_popular(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('movies')
        total_pages, total_items = self.movies_popular(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'popular_movies',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'movie'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def animes_movies_popular(self,page):
        total_pages,results = httpclient.animes_movies_popular_api(page) 
        if results:
            total_items = len(results)
            self.process_movie(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_animes_movies_popular(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('movies')
        total_pages, total_items = self.animes_movies_popular(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'popular_animes_movies',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'movie'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def search_movies(self,search,page):
        total_pages,results = httpclient.search_movies_api(search,page)
        if results:
            total_items = len(results)
            self.process_movie(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_search_movies(self,search,page):
        next_page = str(int(page) + 1)
        self.setcontent('movies')
        total_pages,total_items = self.search_movies(search,page)
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'search_movies',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'search': str(search),
                'mediatype': 'movie'
            }
            self.addMenuItem(item_data)

        if total_items > 0:
            self.end()

    def process_tvshow(self,results):
        for item_ in results:         
            id = item_.get('id')
            name = item_.get('name')
            original_name = item_.get('original_name')
            description = item_.get('overview')
            if not description:
                description = ''
            backdrop_path = item_.get('backdrop_path')
            if backdrop_path:
                fanart = 'https://www.themoviedb.org/t/p/original%s'%backdrop_path
            else:
                fanart = ''
            poster_path = item_.get('poster_path')
            if poster_path:
                iconimage = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2%s'%poster_path
            else:
                iconimage = ''
            release = item_.get('first_air_date')
            if release:
                year = release.split('-')[0]
                year = str(year)
            else:
                release = 'false'
                year = '0'
            if backdrop_path and poster_path and id and name and original_name:
                if not year == '0':
                    new_name = '%s (%s)'%(name,year)
                else:
                    new_name = name
                item_data = {
                    'name': new_name,
                    'action': 'season_tvshow',
                    'iconimage': iconimage,
                    'fanart': fanart,
                    'description': description,
                    'aired': release,
                    'codec': 'h264',
                    'video_title': name,
                    'originaltitle': original_name,
                    'video_id': id,
                    'year': year,
                    'mediatype': 'tvshow'
                }
                self.addMenuItem(item_data,True)                                                                         

    def tv_shows_premiere(self,page):
        total_pages,results = httpclient.tv_shows_premiere_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_tv_shows_premiere(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.tv_shows_premiere(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'premiere_tv_shows',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'tvshow'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def tv_show_trending(self,page):
        total_pages,results = httpclient.tv_shows_trending_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_tv_shows_trending(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.tv_show_trending(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'trending_tv_shows',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'tvshow'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def tv_shows_popular(self,page):
        total_pages,results = httpclient.tv_shows_popular_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_tv_shows_popular(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.tv_shows_popular(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'popular_tv_shows',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'tvshow'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def animes_premiere(self,page):
        total_pages,results = httpclient.animes_premiere_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_animes_premiere(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.animes_premiere(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'premiere_animes',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'animes'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def animes_popular(self,page):
        total_pages,results = httpclient.animes_popular_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_animes_popular(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.animes_popular(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'popular_animes',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'animes'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def animes_airing(self,page):
        total_pages,results = httpclient.animes_airing_api(page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_animes_airing(self,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages, total_items = self.animes_airing(page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'airing_animes',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'mediatype': 'animes'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()

    def season_tvshow(self,video_title,originaltitle,year,id):
        self.setcontent('tvshows')
        r = httpclient.open_season_api(id)
        backdrop_path = r.get('backdrop_path')
        if backdrop_path:
            fanart = 'https://www.themoviedb.org/t/p/original%s'%backdrop_path
        else:
            fanart = ''
        runtime = r.get('episode_run_time')
        if runtime:
            runtime = runtime[0]*60
        else:
            runtime = 0
        try:
            runtime = str(runtime)
        except:
            pass
        genres = r.get('genres')
        id = str(id)
        if genres:
            genres = []
            for genre in r['genres']:
                genres.append(genre['name']+' /')
            genres[-1]=genres[-1].replace(' /', '')
            genres = ' '.join(genres)
        else:
            genres = 'false'
        external_ids = r.get('external_ids')             
        if external_ids:
            imdb_external = external_ids.get('imdb_id')
        else:
            imdb_external = 'false'            
        seasons = r.get('seasons')
        if seasons:
            for item_ in seasons:
                release2 = item_.get('air_date')
                if not release2:
                    release2 = 'false'
                name = item_.get('name')
                description = item_.get('overview')
                if not description:
                    description = ''
                poster_path = item_.get('poster_path')
                if poster_path:
                    iconimage = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2%s'%poster_path
                else:
                    iconimage = ''
                season = item_.get('season_number')            
                if season and name and not imdb_external == 'false':
                    item_data = {
                        'name': name,
                        'action': 'episode_tvshow',
                        'iconimage': iconimage,
                        'fanart': fanart,
                        'description': description,
                        'search1': video_title,
                        'search2': originaltitle,
                        'aired': release2,
                        'duration': runtime,
                        'genre': genres,
                        'imdbnumber': imdb_external,
                        'video_title': video_title,
                        'originaltitle': originaltitle,
                        'year': year,
                        'video_id': id,
                        'season': season,
                        'codec': 'h264',
                        'mediatype': 'season'
                    }
                    self.addMenuItem(item_data,folder=True)
            self.end()

    def open_episode(self,id,season,episode):
        r = httpclient.open_episode_api(id,season,episode)
        description = r.get('overview')
        if description:
            desc = description
        else:
            desc = ''
        still_path = r.get('still_path')
        if still_path:
            iconimage = 'https://www.themoviedb.org/t/p/original%s'%still_path
        else:
            iconimage = ''
        return desc,iconimage 

    def episode_tvshow(self,video_title,originaltitle,genre,imdb,year,duration,id,season,iconimage,fanart):
        last_year, fulldate = httpclient.get_date()
        r = httpclient.show_episode_api(id,season)
        episodes = r.get('episodes')
        if episodes:
            for item_ in episodes:
                air_date = item_.get('air_date')
                if not air_date:
                    release = ''
                else:
                    release = air_date
                episode = item_.get('episode_number')
                if episode:
                    episode = str(episode)
                else:
                    episode = ''
                if air_date:
                    fulldate = fulldate.replace('-', '')
                    air = air_date.replace('-', '')
                    if int(air) > int(fulldate):
                        episode_avaliable = False
                    else:
                        episode_avaliable = True
                else:
                    episode_avaliable = False                
                name = item_.get('name')
                description = item_.get('overview')
                if not description:
                    description = '' 
                if int(season) < 10:
                    sdesc = '0%s'%str(season)
                else:
                    sdesc = str(season)
                if int(episode) < 10:
                    edesc = '0%s'%str(episode)
                else:
                    edesc = str(episode)                
                if name and not episode_avaliable:
                    name = 'S%sE%s - %s'%(sdesc,edesc,name)
                    name = '[COLOR red]'+name+'[/COLOR]'
                else:
                    name = 'S%sE%s - %s'%(sdesc,edesc,name)
                if episode and name and not episode == 'false':
                    desc, icon = self.open_episode(id,season,episode)
                    if description == '':
                        description = desc
                    if icon != '':
                        iconimage = icon
                    else:
                        iconimage = ''
                    item_data = {
                        'name': name,
                        'action': 'provider',
                        'iconimage': iconimage,
                        'fanart': fanart,
                        'description': description,
                        'aired': release,
                        'duration': duration,
                        'genre': genre,
                        'imdbnumber': imdb,
                        'video_title': video_title,
                        'originaltitle': originaltitle,
                        'year': year,
                        'season': season,
                        'episode': episode,
                        'codec': 'h264',
                        'mediatype': 'episode'
                    }
                    self.addMenuItem(item_data,folder=True)

            self.end()

    def find_tv_show(self,imdb):
        r = httpclient.find_tv_show_api(imdb)
        tv_results = r.get('tv_results')
        if tv_results:
            for item_ in tv_results:
                original_name = item_.get('original_name')
                overview = item_.get('overview')
                if overview:
                    desc = overview
                else:
                    desc = ''
                first_air_date = item_.get('first_air_date')
                name = item_.get('name')
                poster_path = item_.get('poster_path')
                if poster_path:
                    iconimage = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2%s'%poster_path
                else:
                    iconimage = ''            
                if original_name and first_air_date and name:
                    year = first_air_date.split('-')[0]
                    year = str(year)
                    search1 = name
                    search2 = original_name
                else:
                    year = '0'
                    search1 = ''
                    search2 = ''
                    desc = ''
                    iconimage = '' 
                break
        else:
            year = '0'
            search1 = ''
            search2 = ''
            desc = ''
            iconimage = '' 
        return year,search1,search2,desc,iconimage

    def get_lastest_episodes(self,date):
        date = str(date)
        r = httpclient.lastest_episodes_api(date)
        if r:    
            for item_ in r:
                show = item_.get('show')
                release = item_.get('airdate')
                if release:
                    tvshow = release.replace('-', '')
                    date_system = date.replace('-', '')
                    if tvshow == date_system:
                        avaliable = True
                    else:
                        avaliable = False                
                else:
                    avaliable = False
                    release = ''
            
                if show:
                    externals = show.get('externals')
                    if externals:
                        imdb = externals.get('imdb')
                    else:
                        imdb = False
                    genres = show.get('genres')
                    if genres:
                        genres_ = []
                        for genre in genres:
                            genres_.append(genre+' /')
                        genres_[-1]=genres_[-1].replace(' /', '')
                        genres = ' '.join(genres_)
                    else:
                        genres = ''
                    tv_show_name = show.get('name')
                    type = show.get('type')
                    image = show.get('image')
                    if image:
                        iconimage = image.get('original')
                        if not iconimage:
                            iconimage = ''
                    else:
                        iconimage = ''
                    description = show.get('summary')
                    if description:
                        description = httpclient.cleanhtml(description)
                    else:
                        description = ''
                else:
                    imdb = False
                    genres = ''
                    tv_show_name = False
                    type = False
                    iconimage = ''
                    description = ''
                title = item_.get('name')
                season = item_.get('season')
                episode = item_.get('number')
                runtime = item_.get('runtime')
                if runtime:
                    runtime = str(int(runtime)*60)
                else:
                    runtime = ''
                if season:
                    if int(season) < 10:
                        sdesc = '0%s'%str(season)
                    else:
                        sdesc = str(season)
                else:
                    season = ''
                if episode:
                    if int(episode) < 10:
                        edesc = '0%s'%str(episode)
                    else:
                        edesc = str(episode)
                else:
                    episode = ''
                if imdb and release and tv_show_name and title and avaliable and type == 'Scripted' and season and episode:           
                    year,search1,search2,desc,icon = self.find_tv_show(imdb)
                    if desc == '':
                        desc = description
                    if icon == '':
                        icon = iconimage
                    if year !='0' and search1 !='' and search2 !='':                
                        fullname = '%s - S%sE%s - %s'%(search1,sdesc,edesc,title)
                        item_data = {
                            'name': fullname,
                            'action': 'provider',
                            'iconimage': icon,
                            'description': desc,
                            'aired': release,
                            'duration': runtime,
                            'genre': genres,
                            'imdbnumber': imdb,
                            'video_title': search1,
                            'originaltitle': search2,
                            'year': year,
                            'season': str(season),
                            'episode': str(episode),
                            'codec': 'h264',
                            'mediatype': 'episode'
                        }
                        self.addMenuItem(item_data,folder=True)

    def new_episodes(self):
        from datetime import timedelta, date
        date1 = date.today()
        date2 = date1 - timedelta(days = 1)
        date3 = date1 - timedelta(days = 2)
        date4 = date1 - timedelta(days = 3)
        date5 = date1 - timedelta(days = 4)
        self.setcontent('episodes')
        self.get_lastest_episodes(date1)
        self.get_lastest_episodes(date2)
        self.get_lastest_episodes(date3)
        self.get_lastest_episodes(date4)
        self.get_lastest_episodes(date5)
        self.end()

    def search_tv_shows(self,search,page):
        total_pages,results = httpclient.search_tv_shows_api(search,page)
        if results:
            total_items = len(results)
            self.process_tvshow(results)
        else:
            total_items = 0
        return total_pages,total_items

    def pagination_search_tv_shows(self,search,page):
        next_page = str(int(page) + 1)
        self.setcontent('tvshows')
        total_pages,total_items = self.search_tv_shows(search,page)
        
        if int(next_page) <= int(total_pages) and int(total_items) > 0 and int(total_pages) > 1:
            item_data = {
                'name': '[B]' + AutoTranslate.language('Page') + str(next_page) + AutoTranslate.language('of') + str(total_pages) + '[/B]',
                'action': 'search_tv_shows',
                'iconimage': self.icon('next'),
                'page': str(next_page),
                'search': str(search),
                'mediatype': 'tvshow'
            }
            self.addMenuItem(item_data)
            
        if total_items > 0:
            self.end()                                                                                                           



    def list_server_links(self,imdb,year,season,episode,name,video_title,genre,iconimage,fanart,description):
        menus_links = sources.show_content(imdb,year,season,episode)
        if menus_links:
            self.setcontent('videos')
            for name2, page_href in menus_links:
                self.addMenuItem({'name': name2.encode('utf-8', 'ignore'), 'action': 'play_resolve', 'video_title': video_title, 'url': page_href,'iconimage': iconimage, 'fanart': fanart, 'playable': 'false', 'description': name, 'description2': description, 'imdbnumber': imdb, 'season': str(season), 'episode': str(episode), 'genre': genre, 'year': str(year)},False)
            self.end()
        else:
            self.notify('Nenhuma fonte disponivel')

    def resolve_links(self, url, video_title, imdb, year, season, episode, genre, iconimage, fanart, description2, playable):
        if season and episode:
            try:
                video_title = video_title.decode('utf-8')
            except:
                pass
            name = '{0} - {1}x{2}'.format(video_title, season, episode)
        else:
            name = video_title

        # Resolver a URL escolhida usando o mesmo resolver usado no autoplay
        try:
            print(f"[DEBUG] resolve_links: tentando resolver URL escolhida -> {url}")
            stream, sub = sources.select_resolver(url, season, episode)
        except Exception as e:
            print(f"[ERROR] resolve_links: falha ao resolver link: {e}")
            self.notify('Falha ao resolver link')
            return

        if not stream:
            self.notify('Nenhuma fonte disponível')
            return

        import xbmc
        import xbmcgui
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': iconimage, 'icon': iconimage, 'fanart': fanart})
        if sub:
            list_item.setSubtitles([sub])
        xbmc.Player().play(stream, list_item)

        if stream:
            self.play_video({
                'name': name,
                'url': stream,
                'sub': sub,
                'iconimage': iconimage,
                'fanart': fanart,
                'description': description2,
                'originaltitle': video_title,
                'imdbnumber': imdb,
                'season': str(season),
                'episode': str(episode),
                'genre': genre,
                'year': str(year),
                'playable': playable
            })
        else:
            self.notify('Stream indisponível')
