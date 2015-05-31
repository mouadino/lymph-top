# -*- coding: utf-8 -*-
from __future__ import print_function
import sys


DONE = object()


class _Option(object):
    def __init__(self, prefix, help, callback):
        self._prefix = prefix
        self._help = help
        self._callback = callback

    @property
    def prefix(self):
        return self._prefix

    @property
    def help(self):
        return self._help

    @property
    def status(self):
        return ''

    def react(self):
        raise NotImplementedError()


class UniqueKeyOption(_Option):
    """Option that is meant to react to one key press."""

    def react(self):
        self._callback()


class TextOption(_Option):
    """Option that is meant to accept a text limited by Enter key."""

    def __init__(self, *args, **kwargs):
        self._buffer = ''
        self.last_value = kwargs.pop('value', '')
        super(TextOption, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return '%s: %s' % (self._prefix, self._buffer)

    @property
    def buffer(self):
        return self._buffer

    def react(self, read_char):
        if read_char.name == 'KEY_ENTER':
            self._callback(self.buffer)
            self._last_value = self.buffer
            self._clear()
            return DONE
        elif read_char.name == 'KEY_DELETE':
            self._buffer = self._buffer[:-1]
        elif read_char.name == 'KEY_ESCAPE':
            self._clear()
            return DONE
        else:
            self._buffer += read_char

    def _clear(self):
        self._buffer = ''


class UserInput(object):

    def __init__(self, options):
        self.options = options
        self._error = ''
        self._active_option = None

    @property
    def status(self):
        if self._error:
            return 'error: %s' % self._error
        if self._active_option:
            return self._active_option.status
        return ''

    def display(self, terminal):
        print(self.status, end='')
        sys.stdout.flush()  # We don't want a new line after command.
        self._read_stdin(terminal)

    def _read_stdin(self, terminal):
        char = self.getch(terminal)
        if not char:
            return
        if self._active_option:
            self._error = ''
            try:
                res = self._active_option.react(char)
            except ValueError as ex:
                self._error = str(ex)
                self._active_option = None
            else:
                if res is DONE:
                    self._active_option = None
        else:
            self._error = ''
            char_name = char.name if char.is_sequence else char
            option = self.options.get(char_name)
            if option:
                if isinstance(option, UniqueKeyOption):
                    option.react()
                else:
                    self._active_option = option

    @staticmethod
    def getch(terminal):
        with terminal.cbreak():
            return terminal.inkey(timeout=.1)
