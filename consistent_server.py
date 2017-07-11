#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy
from time import time
from uuid import uuid4

from gevent import monkey
monkey.patch_all()  # noqa

from flask import Flask, redirect, request, Response
from flask import render_template
from gevent import sleep, spawn_later
from gevent.pywsgi import WSGIServer

from uhashring import HashRing

from settings import IMG_URLS, NODE_TIMEOUT, WIN_URL

"""
Implementation code
"""


def add_node(node_id):
    """
    """
    ttl = time() + NODE_TIMEOUT
    ep2017.hr.add_node(node_id, conf={'instance': ttl})
    sleep(0.2)


def clean_nodes():
    """
    """
    for node, conf in copy(ep2017.hr.nodes).items():
        if time() > conf['instance']:
            print('cleaning dead node', node)
            ep2017.hr.remove_node(node)
            sleep(0.2)
    print('{} active nodes'.format(len(ep2017.hr.nodes)))
    spawn_later(NODE_TIMEOUT, clean_nodes)


def update_winners(node_id):
    """
    """
    if not ep2017.winners or ep2017.winners[-1] != node_id:
        ep2017.winners.append(node_id)


def get_img_url_for_node(node_id):
    """
    """
    if ep2017.hr.get_node(WIN_URL) == node_id:
        img_url = WIN_URL
        update_winners(node_id)
    else:
        img_url = ep2017.url_hr.get_node(node_id)
    return img_url


def get_live_stats():
    """
    """
    return len(ep2017.hr.nodes), ep2017.hr.get_node(WIN_URL)


"""
Flask webapp code
"""


def set_node_id():
    """
    """
    if request.path == '/favicon.ico':
        return Response(status=404)
    request.mod_id = request.cookies.get('mod_id')
    if not request.headers.get('User-Agent', '').startswith('Mozilla/'):
        return Response('You look like a bot, sorry.')
    if request.mod_id is None:
        is_ping = request.args.get('ping') == '1'
        if is_ping is False:
            response = redirect('{}?ping=1'.format(request.url))
            response.set_cookie(key='mod_id', value=str(uuid4()))
            return response
        else:
            return Response(
                'You disabled cookie support, cannot do without, sorry.')


def set_no_cache_headers(response):
    """
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, private'
    response.headers['Etag'] = str(uuid4())
    response.headers['Expires'] = 'Wed, 23 Feb 2000 00:00:01 GMT'
    response.headers['Pragma'] = 'no-cache'
    return response


def game_page():
    """
    """
    add_node(request.mod_id)
    img_url = get_img_url_for_node(request.mod_id)
    return render_template(
        'game.html.j2', node=request.mod_id, img_url=img_url)


def live_page():
    """
    """
    nodes_count, winner_node = get_live_stats()
    print('winner is', winner_node)
    print('winner changed', len(ep2017.winners), 'times')
    return render_template(
        'live.html.j2',
        hash_function=ep2017.mode,
        nodes_count=nodes_count,
        winner_changes=len(ep2017.winners),
        winner_node=winner_node)


if __name__ == "__main__":
    """
    Consistent hashing implementation uses two rings to lookup
        - an image URL from a node id (hr)
        - a node id from an image URL (url_hr)
    """
    ep2017 = Flask(__name__)
    ep2017.mode = 'consistent_hashing'
    ep2017.hr = HashRing()
    ep2017.url_hr = HashRing(IMG_URLS)
    ep2017.winners = []
    #
    ep2017.before_request_funcs = {None: [set_node_id]}
    ep2017.after_request_funcs = {None: [set_no_cache_headers]}
    ep2017.add_url_rule('/', 'game', view_func=game_page)
    ep2017.add_url_rule('/live', 'live', view_func=live_page)
    #
    print('Spawning node cleaner greenlet...')
    spawn_later(NODE_TIMEOUT, clean_nodes)
    print('Serving on 8000...')
    WSGIServer(('0.0.0.0', 8000), ep2017).serve_forever()
