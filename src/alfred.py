# -*- coding: utf-8 -*-
import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

"""
You should run your script via /bin/bash with all escape options ticked.
The command line should be

python yourscript.py "{query}" arg2 arg3 ...
"""


UNESCAPE_CHARACTERS = u""" ;()"""

_MAX_RESULTS_DEFAULT = 9

preferences = plistlib.readPlist('info.plist')
bundleid = preferences['bundleid']


class Item(object):
    @classmethod
    def unicode(cls, value):
        try:
            items = value.iteritems()
        except AttributeError:
            return unicode(value)
        else:
            return dict(map(unicode, item) for item in items)

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml(), encoding='utf-8')

    def xml(self):
        item = Element(u'item', self.unicode(self.attributes))
        for attribute in (u'title', u'subtitle', u'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            try:
                (value, attributes) = value
            except:
                attributes = {}
                elem = SubElement(item, attribute, self.unicode(attributes))
                elem.text = unicode(value)
        return item


def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])


def config():
    return _create('config')


def decode(s):
    return unicodedata.normalize('NFC', s.decode('utf-8'))


def get_uid(uid):
    return u'-'.join(map(unicode, (bundleid, uid)))


def unescape(query, characters=None):
    if not characters:
        characters = UNESCAPE_CHARACTERS
    for character in characters:
        query = query.replace('\\%s' % character, character)
    return query


def write(text):
    sys.stdout.write(text)


def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')


def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path


class AlfredWorkflow(object):
    _reserved_words = []

    def write_text(self, text):
        print(text)

    def write_item(self, item):
        return self.write_items([item])

    def write_items(self, items):
        return write(xml(items, maxresults=self.max_results))

    def message_item(self, title, message, icon=None, uid=0):
        return Item({u'uid': get_uid(uid), u'arg': '',
                            u'ignore': 'yes'}, title, message, icon)

    def warning_item(self, title, message, uid=0):
        return self.message_item(title=title, message=message, uid=uid,
                                 icon='warning.png')

    def error_item(self, title, message, uid=0):
        return self.message_item(title=title, message=message, uid=uid,
                                 icon='error.png')

    def exception_item(self, title, exception, uid=0):
        message = str(exception).replace('\n', ' ')
        return self.error_item(title=title, message=message, uid=uid)

    def route_action(self, action, query=None):
        method_name = 'do_{}'.format(action)
        if not hasattr(self, method_name):
            raise RuntimeError('Unknown action {}'.format(action))

        method = getattr(self, method_name)
        return method(query)

    def is_command(self, query):
        try:
            command, rest = query.split(' ', 1)
        except ValueError:
            command = query
            command = command.strip()
        return command in self._reserved_words or \
            hasattr(self, 'do_{}'.format(command))
