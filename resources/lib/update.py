# resources/lib/update.py
# -*- coding: utf-8 -*-
'''
Atualização automática dos scrapers
Executado toda vez que o addon é aberto
'''

import os
import json
import xbmc
import xbmcvfs
import xbmcaddon
from urllib.request import urlopen, Request
from contextlib import closing

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
SCRAPERS_PATH = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib', 'scrapers'))
COMMIT_FILE = os.path.join(SCRAPERS_PATH, '.scraper_commit')

GITHUB_USER = "icarok99"
GITHUB_REPO = "plugin.video.thethunder"
GITHUB_BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/resources/lib/scrapers"
API_COMMIT = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def log(msg):
    xbmc.log(f"[TheThunder AutoUpdate] {msg}", xbmc.LOGINFO)

def get_latest_sha():
    try:
        req = Request(API_COMMIT, headers={'User-Agent': USER_AGENT})
        with closing(urlopen(req)) as r:
            return json.loads(r.read().decode())['sha']
    except Exception as e:
        log(f"Erro ao obter commit: {e}")
        return None

def get_local_sha():
    if not xbmcvfs.exists(COMMIT_FILE):
        return None
    try:
        with open(xbmcvfs.translatePath(COMMIT_FILE), 'r') as f:
            return f.read().strip()
    except:
        return None

def save_sha(sha):
    try:
        with open(xbmcvfs.translatePath(COMMIT_FILE), 'w') as f:
            f.write(sha)
    except:
        pass

def download_file(filename):
    url = f"{RAW_BASE}/{filename}"
    try:
        req = Request(url, headers={'User-Agent': USER_AGENT})
        with closing(urlopen(req)) as r:
            return r.read()
    except Exception as e:
        log(f"Erro ao baixar {filename}: {e}")
        return None

def auto_update_scrapers(silent=True):
    latest = get_latest_sha()
    if not latest:
        return False

    local = get_local_sha()
    if local == latest:
        return False

    # Lista arquivos no GitHub
    try:
        req = Request(API_COMMIT, headers={'User-Agent': USER_AGENT})
        with closing(urlopen(req)) as r:
            tree_sha = json.loads(r.read().decode())['commit']['tree']['sha']
        tree_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/git/trees/{tree_sha}?recursive=1"
        req = Request(tree_url, headers={'User-Agent': USER_AGENT})
        with closing(urlopen(req)) as r:
            files = [item['path'].split('/')[-1] for item in json.loads(r.read().decode())['tree']
                     if item['path'].startswith('resources/lib/scrapers/') and item['type'] == 'blob']
    except Exception as e:
        log(f"Erro ao listar arquivos: {e}")
        return False

    updated = 0
    for fname in files:
        if fname in ['__init__.py', '.scraper_commit']:
            continue
        content = download_file(fname)
        if content is not None:
            path = os.path.join(SCRAPERS_PATH, fname)
            with open(xbmcvfs.translatePath(path), 'wb') as f:
                f.write(content)
            updated += 1

    if updated > 0:
        save_sha(latest)
        log(f"Atualizados {updated} scrapers")
    return updated > 0
