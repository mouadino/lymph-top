# -*- coding: utf-8 -*-
import collections
import time

import gevent

from lymph.utils import Undefined
from lymph.exceptions import Timeout

from .fail import gracefull_fail


class MetricsPoller(object):

    def __init__(self, client, timeout=1, interval=2, fqdns=None, names=None):
        self._client = client
        self._instances = {}

        self.timeout = timeout
        self.interval = interval
        self.fqdns = fqdns
        self.names = names
        self.running = True

    @property
    def instances(self):
        return self._instances

    def run(self):
        gevent.spawn(self._loop)

    def _loop(self):
        while self.running:
            self._refresh_metrics()
            time.sleep(self.interval)

    @gracefull_fail
    def _refresh_metrics(self):
        services = self._client.container.discover()
        current_instances = {}
        for interface_name in services:
            if self.names and interface_name not in self.names:
                continue
            interface_instances = self._client.container.lookup(interface_name)
            for instance in list(interface_instances):
                if self.fqdns and instance.fqdn not in self.fqdns:
                    continue
                metrics = self._get_instance_metrics(instance)
                if not metrics:
                    continue
                current_instances[instance.endpoint] = InstanceInfo(interface_name, instance.endpoint, metrics)
        self._instances = current_instances

    def _get_instance_metrics(self, instance):
        try:
            metrics = self._client.request(instance.endpoint, 'lymph.get_metrics', {}, timeout=self.timeout).body
        except Timeout:
            return
        return {name: value for name, value, _ in metrics}


class InstanceInfo(collections.namedtuple('InstanceInfo', 'name endpoint metrics')):

    def get(self, name, default=Undefined):
        try:
            return getattr(self, name)
        except AttributeError:
            try:
                return self.metrics[name]
            except KeyError:
                if default is not Undefined:
                    return default
                raise
