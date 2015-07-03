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

    Notes:
       maxrss is in kilobytes in Lunix and bytes in OSX.

        - http://man7.org/linux/man-pages/man2/getrusage.2.html
        - https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man2/getrusage.2.html

    Example:
    >>> format_memory_usage('81673856')
    '77M'
    """
    # XXX: Assume linux !
    return sizing.size(int(value) * 1000)
