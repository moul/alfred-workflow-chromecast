# -*- coding: utf-8 -*-

import os
import ConfigParser
import time
import urllib
import urllib2

import alfred


CHROMECAST_IP='192.168.86.40'


def request(url, values=None, headers=None, method=None, data=None):
    if values and not data:
        data = urllib.urlencode(values)
    if not headers:
        headers = {}
    request = urllib2.Request(url, data, headers)
    if method:
        request.get_method = lambda: method
    response = urllib2.urlopen(request)
    result = response.read()
    return result


class ChromecastWorkflow(alfred.AlfredWorkflow):
    _reserved_words = ['add', 'update', 'remove']

    def __init__(self, ip, port=8008, max_results=20):
        self.max_results = max_results
        self.ip = ip
        self.port = port

    def build_url(self, path):
        return 'http://{}:{}/{}'.format(self.ip, self.port, path)

    @property
    def youtube_url(self):
        return self.build_url('apps/YouTube')

    def do_youtube_run(self, query):
        print(query)
        if query == 'stop':
            return self.do_youtube_stop()
        print(request(self.youtube_url, {'v': query, 't': 0}))

    def do_youtube_stop(self, query=None):
        print(request(self.youtube_url, method='DELETE'))


def main(action, query):
    chromecast = ChromecastWorkflow(ip=CHROMECAST_IP)
    chromecast.route_action(action, query)


if __name__ == "__main__":
    main(action=alfred.args()[0], query=alfred.args()[1])
