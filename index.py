#!/usr/bin/python
# -*- coding: utf-8 -*-

SYS_PATH = '/home/james/public_wsgi/'

import os
import time
import sys
sys.path.append(SYS_PATH)

from tools import Player, log, db_check, GET_to_dict, dict_to_GET
from CONSTANTS import VERBOSE

#macronedE = u'\uC493'.encode('utf8') 
#TITLE = "Epis" + macronedE  + "ma"
TITLE = "Episema"

HTML = "<html><head><title>{0}</title></head><body>{1}</body></html>"
LINK = "<a href='{0}'>{1}</a>"

# Should run once when the server first starts. Makes sure the database
# exists with tables and values
db_check()

def application(environ, start_response):
    header = [('Content-Type', 'text/html')]
    jpgheader = [('Content-Type', 'image/jpeg')]

    path = environ['PATH_INFO'].split('/')[1:]
    get = environ['REQUEST_URI'].split('?')[1:]
    
    if not path[0]:
        start_response('200 OK', header)
        return load_home()
    elif path[0] == "game":
        start_response('200 OK', header)
        return load_episema(path[0], get)
    elif path[0] == "place":
        start_response('200 OK', header)
        return load_place(environ)
    elif path[0] == "404image.jpg":
        start_response('200 OK', jpgheader)
        with open(SYS_PATH + path[0], 'rb') as f:
            image = f.read()
        return image
    
    start_response('404 Not Found', header)
    return load_404()

def load_404():
    src = '404image.jpg'
    link = "<a href='/'> <img src='{0}'> </a>".format(src)
    log("404 String: " + link)
    return error(link, "404")

def load_place(env):
    title = "Another place"
    text = "More room for activites and a reminder to improve link handling."
    link = "<br>Go <a href='/'>home</a>."

    info = [ str(key) + ": " + str(env[key]) for key in env ]
    body = "<br>".join([text, link] + info + [link])
    
    return HTML.format(title, body)

def load_home():
    title = "Home"
    header = "<h2>{0} Home</h2>".format(TITLE)
    links = ["Play <a href='/game'>{0}</a>.".format(TITLE),
             "Another  <a href='/place'>link</a>.",
            ]
    text = """Much of this is being written from scratch, so don't expect
              anything and you might be pleasantly surprised sometimes."""
    body = "<br>".join([header] + links + [text])
    return HTML.format(title, body)

def load_episema(path, get):
    refresh_link = path
    if get: refresh_link += "?" + get[0]
    link_home = "Go <a href='/'>home</a>."

    get = GET_to_dict(get)

    if 'pid' not in get:
        text = ["No player is loaded. <a href='/game?pid=1'>Log in</a>."]
    else:
        player = Player(get['pid'])
        if not player.valid_pid:
            text = ["The given pid doesn't correspond to a player."]
        else:
            if "a" in get: player.do_action(get["a"])
            links = [ LINK.format(path + action, string)
                      for action, string in player.get_links() ]
            links = "<br>".join(links)
            text = [str(player.get_location()), links]

    refresh = "<a href=" + refresh_link + ">Refresh</a>."
    info = [refresh, link_home] + text
    body = "<br>".join(info)
    return HTML.format(TITLE, body)
    
def error(message, title="Error"):
    return HTML.format(title, message)
