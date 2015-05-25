# -*- coding: utf-8 -*-
import collections


# Commands.
QUIT = object()
HELP = object()

Option = collections.namedtuple('Option', 'prefix help')


class UserCommand(object):

    options = {
        'o': Option('order', 'Set sort by column e.g. +name'),
        '?': Option('', 'Show this help message'),
        'ESC': Option('', 'Quit terminal or active command'),
    }

    def __init__(self):
        self._name = ''
        self._buffer = ''
        self.error = ''

    @property
    def status(self):
        if self.error:
            return 'error: %s' % self.error
        return '%s: %s' % (self._name, self._buffer) if self._name else ''

    def read(self, terminal):
        char = self.getch(terminal)
        if not char:
            return
        if self._name:
            self.error = ''
            if char.name == 'KEY_ENTER':
                cmd = self._buffer
                self.clear()
                return cmd
            elif char.name == 'KEY_DELETE':
                self._buffer = self._buffer[:-1]
            elif char.name == 'KEY_ESCAPE':
                self.clear()
            else:
                self._buffer += char
        else:
            self.error = ''
            if char.name == 'KEY_ESCAPE':
                return QUIT
            if str(char) == '?':
                return HELP
            try:
                self._name = self.options[str(char)].prefix
            except KeyError:
                pass

    @staticmethod
    def getch(terminal):
        with terminal.cbreak():
            return terminal.inkey(timeout=.1)

    def clear(self):
        self._name = ''
        self._buffer = ''
