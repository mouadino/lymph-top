# -*- coding: utf-8 -*-
import hurry.filesize as sizing


class _Prettifier(object):
    def __init__(self):
        self._callables = {}

    def __call__(self, name, value):
        try:
            func = self._callables[name]
        except KeyError:
            return value
        else:
            return func(value)

    def register(self, *names):
        def _inner(func):
            for name in names:
                self._callables[name] = func
            return func
        return _inner


prettifier = _Prettifier()


@prettifier.register('rusage.maxrss')
def format_memory_usage(value):
    """Prettify memory size.

    Example:
        >>> format_memory_usage('81673856')
        '77M'
    """
    return sizing.size(int(value))
