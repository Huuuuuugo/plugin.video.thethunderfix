# -*- coding: utf-8 -*-
'''
	The Thunder
'''

from sys import argv
from resources.lib import home
from kodi_helper import parse_qsl

try:
    params = dict(parse_qsl(argv[2].replace('?', '')))
except:
    params = {}

# AUTO UPDATE (silencioso) - branch main
try:
    from resources.lib import update
    update.auto_update()
except:
    pass

home.router(params)