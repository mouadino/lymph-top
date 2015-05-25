# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import operator as op

import six


class Table(object):

    def __init__(self, headers, limit=None, prettifier=lambda _, value: value, sort_by=None):
        self._prettifier = prettifier
        self._instances = {}
        self._metrics_received = False

        self.headers = headers
        self.limit = limit
        self.sort_by = sort_by or '-name'

    @property
    def sort_by(self):
        return self._sort_by

    @sort_by.setter
    def sort_by(self, sort_by):
        if not sort_by.startswith(("-", "+")):
            sort_by = "-" + sort_by
        order, column = sort_by[0], sort_by[1:]
        for header, _ in self.headers:
            if column == header:
                self._sort_by = header
                break
        else:
            raise ValueError('Unkown column %r' % column)
        self._ascending = order == "+"

    @property
    def instances(self):
        return sorted(self._instances.values(), reverse=self._ascending, key=op.methodcaller('get', self._sort_by, default=None))

    @instances.setter
    def instances(self, new_instances):
        self._metrics_received = True
        self._instances = new_instances

    def display(self, terminal):
        self._display_headers(terminal)
        self._display_metrics(terminal)

    def _display_headers(self, terminal):
        for header, size in self.headers:
            if header == self._sort_by:
                header += " ▼" if self._ascending else " ▲"
            header = self._truncate(header, size)
            print(terminal.bold(header), end=' ')
        print()  # flush

    def _display_metrics(self, terminal):
        for instance in self.instances[:self.limit]:
            values = []
            for name, size in self.headers:
                value = instance.get(name, 'N/A')
                value = self._prettifier(name, value)
                values.append((value, size))
            print(' '.join(self._truncate(value, size) for value, size in values))
        if not self.instances:
            if self._metrics_received:
                print('No metrics found')
            else:
                print('Fetching metrics ...')
        print()  # flush

    @staticmethod
    def _truncate(value, size):
        value = six.text_type(value)
        if len(value) > size:
            return value[:size - 2] + ".."
        return value.ljust(size)
