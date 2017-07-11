#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from uhashring import HashRing
from uuid import uuid4
from os import listdir

nodes = {
    '/mnt/disk1/': {
        'instance': open('/mnt/disk1/commitlog', 'a')
    },
    '/mnt/disk2/': {
        'instance': open('/mnt/disk2/commitlog', 'a')
    },
    '/mnt/disk3/': {
        'instance': open('/mnt/disk3/commitlog', 'a')
    },
    '/mnt/disk4/': {
        'instance': open('/mnt/disk4/commitlog', 'a')
    },
}

# create the ring
hr = HashRing(nodes)


# dummy function to showcase disk I/O write balancing
def dummy_writer(task_id):
    output_data = '{} output'.format(task_id)

    # keep a trace of our write time
    write_id = str(uuid4())
    hr[task_id].write('{}:{}\n'.format(write_id, task_id))

    # write the actual data on a file
    file_path = '{}/{}.out'.format(hr.get_node(task_id), write_id)
    with open(file_path, 'w') as output_file:
        output_file.write(output_data)


# dummy function to showcase disk I/O read balancing
def dummy_reader(task_id):
    output_files = listdir(hr.get_node(task_id))
    for file_name in output_files:
        if file_name.endswith('.out'):
            file_path = '{}/{}'.format(hr.get_node(task_id), file_name)
            with open(file_path, 'r') as input_file:
                print(input_file.read())


# ok let's try this
dummy_writer('task_for_real')
dummy_writer('task_for_the_win')
dummy_writer('task_down')
dummy_writer('task_is_known')
dummy_writer('task_g')

dummy_reader('task_for_the_win')
