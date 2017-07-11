#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy
from hashlib import md5
from time import time
from uuid import uuid4

from gevent import monkey
monkey.patch_all()  # noqa

from flask import Flask, redirect, request, Response
from flask import render_template
from gevent import spawn_later
from gevent.pywsgi import WSGIServer
from uhashring import HashRing

from settings import IMG_URLS, NODE_TIMEOUT, WIN_URL

ep2017 = Flask(__name__)


def get_url_for_node():
    """
    """
    if HASH_FUNCTION == modulo:
        img_index = get_index_from_md5(request.mod_id, IMG_URLS)
        return IMG_URLS[img_index]
    else:
        return url_hr.get_node(request.mod_id)


def get_index_from_md5(key, ref_list):
    """
    """
    return int(md5(key.encode('utf-8')).hexdigest(), 16) % len(ref_list)


def add_node():
    """
    """
    ttl = time() + NODE_TIMEOUT
    if HASH_FUNCTION == modulo:
        if request.mod_id not in nodes:
            nodes.append(request.mod_id)
        nodes_ttl[request.mod_id] = ttl
    else:
        hr.add_node(request.mod_id, conf={'instance': ttl})


def clean_nodes():
    """
    """
    if HASH_FUNCTION == modulo:
        for node in copy(nodes):
            if time() > nodes_ttl[node]:
                print('cleaning node', node)
                nodes.remove(node)
                nodes_ttl.pop(node)
        print('{} active nodes'.format(len(nodes)))
    else:
        for node, conf in copy(hr.nodes).items():
            if time() > conf['instance']:
                print('cleaning dead node', node)
                hr.remove_node(node)
        print('{} active nodes'.format(len(hr.nodes)))
    spawn_later(NODE_TIMEOUT, clean_nodes)


def modulo():
    """
    """
    add_node()
    if nodes[get_index_from_md5(WIN_URL, nodes)] == request.mod_id:
        img_url = WIN_URL
    else:
        img_url = get_url_for_node()
    return img_url


def consistent_hashing():
    """
    """
    add_node()
    if hr.get_node(WIN_URL) == request.mod_id:
        img_url = WIN_URL
    else:
        img_url = get_url_for_node()
    return img_url


@ep2017.before_request
def get_cookie_id():
    """
    """
    request.mod_id = request.cookies.get('mod_id')
    if request.mod_id is None:
        is_ping = request.args.get('ping') == '1'
        if is_ping is False:
            response = redirect('{}?ping=1'.format(request.url))
            response.set_cookie(key='mod_id', value=str(uuid4()))
            return response
        else:
            return Response(
                'You disabled cookie support, cannot do without, sorry.')


@ep2017.route('/')
def handle_request():
    """
    """
    img_url = HASH_FUNCTION()
    if img_url == WIN_URL:
        print('winner is', request.mod_id)
    return render_template(
        'index.html.j2', node=request.mod_id, img_url=img_url)


@ep2017.route('/live')
def live_page():
    """
    """
    if HASH_FUNCTION == modulo:
        nodes_count = len(nodes)
        try:
            winner_node = nodes[get_index_from_md5(WIN_URL, nodes)]
        except ZeroDivisionError:
            winner_node = 'None'
    else:
        nodes_count = len(hr.nodes)
        winner_node = hr.get_node(WIN_URL)
    return render_template(
        'live.html.j2',
        hash_function=HASH_FUNCTION.__name__,
        nodes_count=nodes_count,
        winner_node=winner_node)


if __name__ == "__main__":
    """
    """
    HASH_FUNCTION = modulo
    #
    if HASH_FUNCTION == modulo:
        nodes = []
        nodes_ttl = {}
    else:
        nodes = {}
        hr = HashRing(compat=False)
        url_hr = HashRing(IMG_URLS, compat=False)
    #
    print('Spawning node cleaner greenlet...')
    spawn_later(NODE_TIMEOUT, clean_nodes)
    print('Serving on 80...')
    WSGIServer(('0.0.0.0', 80), ep2017).serve_forever()
