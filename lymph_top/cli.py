# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import time
import traceback

import blessed

from lymph.client import Client
from lymph.cli.base import Command

from .command import UserCommand, QUIT, HELP
from .table import Table
from .metrics_poller import MetricsPoller
from .prettifier import prettifier


def redirect_traceback(func):
    # With blessed tracebacks doesn't show up since they are by default
    # wrote to stderr, else it happen that blessed (under the hood curses)
    # hide stderr output, this function will print traceback to stdout.
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (SystemExit, KeyboardInterrupt):
            # Don't show traceback in case CTRL-C or normal exit.
            raise
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise SystemExit(1)
    return _inner


class TopCommand(Command):
    """
    Usage: lymph top [--order=<column> | -o <column>] [--fqdn=<fqdn>] [--name=<name>] [--columns=<columns>] [-n <ninst>] [-i <interval>] [-t <timeout>] [options]

    Display and update sorted metrics about services.

    Options:

      --order=<column>, -o <column>           Order a specific column.
      --fqdn=<fqdn>                           Show only metrics comming from machine with given full qualified domain name.
      --name=<name>                           Show only metrics comming from service with given name.
      --columns=<columns>                     Columns to show.
      -n <ninsts>                             Only display up to <ninsts> instances.
      -i <interval>                           Set interval between polling metrics.
      -t <timeout>                            Lymph request timeout.

    {COMMON_OPTIONS}

    """

    short_description = 'Display and update sorted metrics about services.'
    default_columns = [
        ('name', 20),
        ('endpoint', 25),
        ('rusage.maxrss', 20),
        ('greenlets.count', 20),
        ('rpc', 20),
        ('exceptions', 20),
    ]

    def __init__(self, *args, **kwargs):
        super(TopCommand, self).__init__(*args, **kwargs)
        self.terminal = blessed.Terminal()
        self.table = Table(self.default_columns, prettifier=prettifier)
        self.current_command = UserCommand()
        self.poller = MetricsPoller(Client.from_config(self.config))

    @redirect_traceback
    def run(self):
        self._parse_args()
        self.poller.run()
        with self.terminal.fullscreen():
            self._top()

    def _parse_args(self):
        sort_by = self.args.get('--order')
        if sort_by:
            try:
                self.table.sort_by = sort_by
            except ValueError:
                raise SystemExit('no column with name: %s' % sort_by)

        fqdn = self.args.get('--fqdn')
        if fqdn:
            self.poller.fqdn = fqdn

        name = self.args.get('--name')
        if name:
            self.poller.name = name

        limit = self.args.get('-n')
        if limit:
            try:
                self.table.limit = int(limit)
            except ValueError:
                raise SystemExit('-n must be integer')

        interval = self.args.get('-i')
        if interval:
            try:
                self.poller.interval = int(interval)
            except ValueError:
                raise SystemExit('-i must be integer')

        timeout = self.args.get('-t')
        if timeout:
            try:
                self.poller.timeout = int(timeout)
            except ValueError:
                raise SystemExit('-t must be integer')

        columns = self.args.get('--columns')
        if columns:
            # TODO: Size is hardcoded ! Maybe --columns <name>:<size>,... !?
            self.table.headers = [(name, 20) for name in columns.split(',') if name]

    def _top(self):
        while True:
            with self.terminal.location(0, 2):
                self.table.display(self.terminal)
            self.table.instances = self.poller.instances
            with self.terminal.location(0, 1):
                print(self.current_command.status, end='')
                sys.stdout.flush()  # We don't want a new line after command.
                self._on_user_input()
            time.sleep(.01)
            print(self.terminal.clear, end='')

    def _on_user_input(self):
        command = self.current_command.read(self.terminal)
        if command:
            if command is QUIT:
                raise SystemExit()
            elif command is HELP:
                self._help()
            else:
                # TODO: Currently we only support 'sort by'.
                try:
                    self.table.sort_by = command
                except ValueError:
                    self.current_command.error = 'invalid sort by: %s' % command

    def _help(self):
        t = self.terminal
        with t.fullscreen():
            print(t.underline('Command') + t.move_x(20) + t.underline('Description'))
            for name, cmd in UserCommand.options.items():
                print(name + t.move_x(20) + cmd.help)
            with t.location(0, t.height - 1):
                print('Press any key to continue...', end='')
            sys.stdout.flush()
            key_pressed = False
            while not key_pressed:
                key_pressed = self.current_command.getch(t)
