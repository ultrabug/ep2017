#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import memcache

from uhashring import monkey
monkey.patch_memcache()

mc = memcache.Client(['node1:11211', 'node2:11211'])
