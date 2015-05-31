# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import time
import collections

import blessed

from lymph.client import Client
from lymph.cli.base import Command

from .input import UserInput, UniqueKeyOption, TextOption
from .table import Table
from .metrics_poller import MetricsPoller
from .prettifier import prettifier
from .fail import gracefull_fail


class TopCommand(Command):
    """
    Usage: lymph top [--order=<column> | -o <column>] [--fqdn=<fqdn>] [--name=<name>] [--columns=<columns>] [-n <ninst>] [-i <interval>] [-t <timeout>] [--guess-external-ip] [options]

    Display and update sorted metrics about services.

    Options:

      --order=<column>, -o <column>           Order a specific column.
      --fqdn=<fqdn>                           Comma separated full qualified domain names to show metrics of.
      --name=<name>                           Comma separated service names to show metrics of.
      --columns=<columns>                     Columns to show.
      -n <ninsts>                             Only display up to <ninsts> instances.
      -i <interval>                           Set interval between polling metrics.
      -t <timeout>                            Lymph request timeout.
      --guess-external-ip                     Guess and use external ip.

    {COMMON_OPTIONS}

    """

    short_description = 'Display and update sorted metrics about services.'
    default_columns = [
        ('name', 20),
        ('endpoint', 25),
        ('rusage.maxrss', 20),
        ('greenlets.count', 20),
        ('rpc', 20),
    ]

    def __init__(self, *args, **kwargs):
        super(TopCommand, self).__init__(*args, **kwargs)
        self.terminal = blessed.Terminal()
        self.metrics_table = Table(self.default_columns, prettifier=prettifier)
        self.metrics_poller = MetricsPoller(Client.from_config(self.config))
        # TODO: Set TextOption values from command line arguments.
        self.input = UserInput({
            'o': TextOption('order', 'Set order by column e.g. +name', self._on_order),
            'f': TextOption('fqdns', 'Set comma separated fqdns to show, set to empty to disable filtering', self._on_filetring_by_fqdns),
            'n': TextOption('name', 'Set comma separated services name to show, set to empty to disable filtering', self._on_filetring_by_names),
            '?': UniqueKeyOption('', 'Show this help message', self._on_help),
            'KEY_ESCAPE': UniqueKeyOption('', 'Quit terminal or active command', self._on_escape),
        })

    @gracefull_fail
    def run(self):
        self._parse_args()
        self.metrics_poller.run()
        with self.terminal.fullscreen():
            self._top()

    def _parse_args(self):
        order_by = self.args.get('--order')
        if order_by:
            try:
                self.metrics_table.order_by = order_by
            except ValueError:
                raise SystemExit('no column with name: %s' % order_by)
            self.input.options['o'].last_value = order_by

        fqdn = self.args.get('--fqdn')
        if fqdn:
            self.metrics_poller.fqdns = fqdn.split(',')
            self.input.options['f'].last_value = fqdn

        name = self.args.get('--name')
        if name:
            self.metrics_poller.names = name.split(',')
            self.input.options['n'].last_value = name

        limit = self.args.get('-n')
        if limit:
            try:
                self.metrics_table.limit = int(limit)
            except ValueError:
                raise SystemExit('-n must be integer')

        interval = self.args.get('-i')
        if interval:
            try:
                self.metrics_poller.interval = int(interval)
            except ValueError:
                raise SystemExit('-i must be integer')

        timeout = self.args.get('-t')
        if timeout:
            try:
                self.metrics_poller.timeout = int(timeout)
            except ValueError:
                raise SystemExit('-t must be integer')

        columns = self.args.get('--columns')
        if columns:
            # TODO: Size is hardcoded ! Maybe --columns <name>:<size>,... !?
            self.metrics_table.headers = [(name, 20) for name in columns.split(',') if name]

    def _top(self):
        while True:
            with self.terminal.location(0, 2):
                self.metrics_table.display(self.terminal)
            with self.terminal.location(0, 1):
                self.input.display(self.terminal)
            self.metrics_table.instances = self.metrics_poller.instances
            time.sleep(.01)
            print(self.terminal.clear, end='')

    def _on_help(self):
        def print_line(line):
            print(''.join(s + t.move_x(20 * i) for i, s in enumerate(line, start=1)))
        t = self.terminal
        with t.fullscreen():
            print_line(map(t.underline, ['State', 'Command', 'Description']))
            for name, opt in self.input.options.items():
                last_value = getattr(opt, 'last_value', '')
                print_line([last_value, name, opt.help])
            with t.location(0, t.height - 1):
                print('Press any key to continue...', end='')
            sys.stdout.flush()
            key_pressed = False
            while not key_pressed:
                key_pressed = self.input.getch(t)
                time.sleep(.01)

    def _on_order(self, order_by):
        try:
            self.metrics_table.order_by = order_by
        except ValueError:
            raise ValueError('invalid sort by: %s' % order_by)

    def _on_filetring_by_names(self, names):
        names = names.split(',') if names else None
        self.metrics_poller.names = names

    def _on_filetring_by_fqdns(self, fqdns):
        fqdns = fqdns.split(',') if fqdns else None
        self.metrics_poller.fqdns = fqdns

    def _on_escape(self):
        raise SystemExit()
