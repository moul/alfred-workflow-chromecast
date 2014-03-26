# -*- coding: utf-8 -*-

import os
import ConfigParser
import time
import urllib
import urllib2

import alfred


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
    port = 8008

    def __init__(self, max_results=20):
        self.max_results = max_results

    def build_url(self, path):
        return 'http://{}:{}/{}'.format(self.ip, self.port, path)

    @property
    def ip(self):
        return alfred.config_get('chromecast_ip', 'Not yet configured')

    @ip.setter
    def ip(self, value):
        alfred.config_set('chromecast_ip', value)

    @property
    def youtube_url(self):
        return self.build_url('apps/YouTube')

    def do_youtube_run(self, query):
        if query == 'stop':
            return self.do_youtube_stop()
        request(self.youtube_url, {'v': query, 't': 0})
        self.write_text('Running {} on Chromecast'.format(query))

    def do_youtube_stop(self, query=None):
        request(self.youtube_url, method='DELETE')
        self.write_text('Playback stopped')

    def do_set_ip(self, query):
        self.ip = query
        self.write_text('New ip: {}'.format(query))

    def do_get_ip(self, query=None):
        self.write_text('Current ip: {}'.format(self.ip))


def main(action, query):
    chromecast = ChromecastWorkflow()
    chromecast.route_action(action, query)


if __name__ == "__main__":
    main(action=alfred.args()[0], query=alfred.args()[1])
