#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql.cursors

from uhashring import HashRing

nodes = {
    'mydb1.local': {
        'instance': pymysql.connect(host='mydb1.local', user='user', password='passwd', db='db'),
        'port': 3306
    },
    'mydb2.local': {
        'instance': pymysql.connect(host='mydb2.local', user='user', password='passwd', db='db'),
        'port': 3306
    },
    'mydb3.local': {
        'instance': pymysql.connect(host='mydb3.local', user='user', password='passwd', db='db'),
        'port': 3306
    },
    'mydb4.local': {
        'instance': pymysql.connect(host='mydb4.local', user='user', password='passwd', db='db'),
        'port': 3306
    },
}

# create the ring
hr = HashRing(nodes)

# we have some data and use the key to distribute it on the right server
some_data = {
    'client A': 'user data of client A',
    'client B': 'user data of client B',
    'client C': 'user data of client C',
    'client D': 'user data of client D'
}

# use the ring intuitively
for partition_key, data in some_data.items():
    with hr[partition_key].cursor() as cursor:
        sql = "INSERT INTO `users` (`data`) VALUES (%s)"
        cursor.execute(sql, (data))

    # hr[partition_key] == 'instance' of selected node (pymysql.connect)
    hr[partition_key].commit()
