#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import beanstalkc

from uhashring import HashRing

nodes = {
    'server_1': {
        'instance': beanstalkc.Connection(host='server_1'),
        'port': 11300
    },
    'server_2': {
        'instance': beanstalkc.Connection(host='server_2'),
        'port': 11300
    },
    'server_3': {
        'instance': beanstalkc.Connection(host='server_3'),
        'port': 11300
    },
    'server_4': {
        'instance': beanstalkc.Connection(host='server_4'),
        'port': 11300
    },
}

# create the ring
hr = HashRing(nodes)

# we get some jobs from a local beanstalkd server and forward them
# based on their content
local_bean = beanstalkc.Connection(host='localhost')
while True:
    job = local_bean.reserve()

    # assume that the first char of the job content is the routing key
    routing_key = job.body[0]

    # forward the job based on the routing key
    hr[routing_key].put(job.body)

    # delete our local copy
    job.delete()
