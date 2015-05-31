import traceback
import sys


def gracefull_fail(func):
    # With blessed tracebacks doesn't show up since they are by default
    # wrote to stderr, else it happen that blessed (under the hood curses)
    # hide stderr output, this function will print traceback to stdout.
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # Don't show traceback in case CTRL-C or normal exit.
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise SystemExit(0)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise SystemExit(1)
    return _inner
