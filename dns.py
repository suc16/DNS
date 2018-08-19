#!/usr/bin/python3.6
# -*- coding :u tf-8 -*-
#
# __author__ = Su
#

import socket


def dns(file_path):
    """
    Query DNS
    :param file_path: a list of urls
    :return:
        x: a set of ip
        y: urls can't be queried successfully
    """
    x = set()
    y = []
    with open(file_path, "r") as f:
        for url in f.readlines():
            try:
                r = socket.gethostbyname_ex(url.strip())
            except (socket.gaierror, socket.herror):
                y.append(url)
            else:
                for i in r[2]:
                    x.add(i)
    return x, y
