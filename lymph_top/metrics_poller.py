# -*- coding: utf-8 -*-
import collections
import time

import gevent

from lymph.utils import Undefined
from lymph.exceptions import Timeout


class MetricsPoller(object):

    def __init__(self, client, timeout=1, interval=2, fqdn=None, name=None):
        self._client = client
        self._instances = {}

        self.timeout = timeout
        self.interval = interval
        self.fqdn = fqdn
        self.name = name
        self.running = True

    @property
    def instances(self):
        return self._instances

    def run(self, *_):
        greenlet = gevent.spawn(self._loop)
        # Respawn when greenlet die.
        greenlet.link_exception(self.run)
        greenlet.start()

    def _loop(self):
        while self.running:
            self._refresh_metrics()
            time.sleep(self.interval)

    def _refresh_metrics(self):
        services = self._client.container.discover()
        alive_endpoints = set()
        for interface_name in services:
            if self.name and interface_name != self.name:
                continue
            interface_instances = self._client.container.lookup(interface_name)
            for instance in interface_instances:
                if self.fqdn and instance.fqdn != self.fqdn:
                    continue
                metrics = self._get_instance_metrics(instance)
                if not metrics:
                    continue
                self._instances[instance.endpoint] = InstanceInfo(interface_name, instance.endpoint, metrics)
                alive_endpoints.add(instance.endpoint)
        for endpoint in self._instances:
            if endpoint not in alive_endpoints:
                self._instances.pop(endpoint, None)

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
