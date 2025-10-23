# -*- coding: utf-8 -*-
'''
Auto-update silencioso dos scrapers - branch main
'''

import os
import json
import xbmcvfs
import xbmcaddon
from urllib.request import urlopen, Request
from contextlib import closing

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
SCRAPERS_PATH = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib', 'scrapers'))
COMMIT_FILE = os.path.join(SCRAPERS_PATH, '.scraper_commit')

# BRANCH OFICIAL
GITHUB_USER = "icarok99"
GITHUB_REPO = "plugin.video.thethunder"
GITHUB_BRANCH = "main"  # <<< AQUI ESTÁ O PRINCIPAL
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/resources/lib/scrapers"
API_COMMIT = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"

def _get(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with closing(urlopen(req)) as r:
            return r.read().decode()
    except:
        return None

def auto_update():
    latest = _get(API_COMMIT)
    if not latest:
        return
    latest_sha = json.loads(latest)['sha']

    if xbmcvfs.exists(COMMIT_FILE):
        with open(xbmcvfs.translatePath(COMMIT_FILE), 'r') as f:
            local_sha = f.read().strip()
        if local_sha == latest_sha:
            return

    tree_sha = json.loads(latest)['commit']['tree']['sha']
    tree = _get(f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/git/trees/{tree_sha}?recursive=1")
    if not tree:
        return

    files = [item['path'].split('/')[-1] for item in json.loads(tree)['tree']
             if item['path'].startswith('resources/lib/scrapers/') and item['type'] == 'blob']

    for fname in files:
        if fname in ['__init__.py', '.scraper_commit']:
            continue
        content = _get(f"{RAW_BASE}/{fname}")
        if content:
            path = os.path.join(SCRAPERS_PATH, fname)
            with open(xbmcvfs.translatePath(path), 'wb') as f:
                f.write(content.encode())

    with open(xbmcvfs.translatePath(COMMIT_FILE), 'w') as f:
        f.write(latest_sha)