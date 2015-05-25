lymph-top
=========

A top-like utility for monitoring lymph [1]_ services.

Usage
=====
::

    $ lymph top
    name                 endpoint                  rusage.maxrss        greenlets.count      rpc ▲                exceptions
    demo                 tcp://127.0.0.1:47761     26M                  36                   297                  N/A
    web                  tcp://127.0.0.1:47217     28M                  33                   297                  N/A
    echo                 tcp://127.0.0.1:38427     26M                  35                   298                  N/A

For more info about usage, check command help message ::

    $ lymph help top

Authors
=======

- Mouad Benchchaoui: https://github.com/mouadino/
- Jacques Rott: https://github.com/jacqueslh


.. [1] https://github.com/deliveryhero/lymph
