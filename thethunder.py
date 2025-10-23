# -*- coding: utf-8 -*-
'''
	The Thunder

	@package plugin.video.thethunder

	@copyright (c) 2024, The Thunder
	@license GNU General Public License, version 3 (GPL-3.0)
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
