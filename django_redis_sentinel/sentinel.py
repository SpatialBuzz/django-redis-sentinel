# -*- coding: utf-8 -*-

import logging
import random
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from redis.sentinel import Sentinel

from django_redis.client import DefaultClient

DJANGO_REDIS_LOGGER = getattr(settings, "DJANGO_REDIS_LOGGER", False)
DJANGO_REDIS_CLOSE_CONNECTION = getattr(settings, "DJANGO_REDIS_CLOSE_CONNECTION", False)


class SentinelClient(DefaultClient):
    """
    Sentinel client object extending django-redis DefaultClient
    """

    def __init__(self, server, params, backend):
        """
        Slightly different logic than connection to multiple Redis servers.
        Reserve only one write and read descriptors, as they will be closed on exit anyway.
        """
        super(SentinelClient, self).__init__(server, params, backend)
        self._client_write = None
        self._client_read = None
        self._client_write_last_check = 0
        self._client_read_last_check = 0
        self._connection_string = server
        self.log = logging.getLogger((DJANGO_REDIS_LOGGER or __name__))

    def parse_connection_string(self, constring):
        """
        Parse connection string in format:
            master_name/sentinel_server:port,sentinel_server:port/db_id
        Returns master name, list of tuples with pair (host, port) and db_id
        """
        try:
            connection_params = constring.split('/')
            master_name = connection_params[0]
            servers = [host_port.split(':') for host_port in connection_params[1].split(',')]
            sentinel_hosts = [(host, int(port)) for host, port in servers]
            db = connection_params[2]
        except (ValueError, TypeError, IndexError):
            raise ImproperlyConfigured("Incorrect format '%s'" % (constring))

        return master_name, sentinel_hosts, db

    def get_client(self, write=True, tried=(), show_index=False):
        """
        Method used to obtain a raw redis client.

        This function is used by almost all cache backend
        operations to obtain a native redis client/connection
        instance.
        """
        self.log.debug("get_client called: write=%s", write)
        if write:
            if self._client_write is None:
                self._client_write = self.connect(write=True)

            if show_index:
                return self._client_write, 0
            else:
                return self._client_write

        if self._client_read is None:
            self._client_read = self.connect(write=False)

        if show_index:
            return self._client_read, 0
        else:
            return self._client_read

    def connect(self, write=True, SentinelClass=None):
        """
        Creates a redis connection with connection pool.
        """
        if SentinelClass is None:
            SentinelClass = Sentinel
        self.log.debug("connect called: write=%s", write)
        master_name, sentinel_hosts, db = self.parse_connection_string(self._connection_string)

        sentinel_timeout = self._options.get('SENTINEL_TIMEOUT', 1)
        password = self._options.get('PASSWORD', None)
        always_master = self._options.get('ALWAYS_MASTER', False)
        sentinel = SentinelClass(sentinel_hosts,
                                 socket_timeout=sentinel_timeout,
                                 password=password)

        if write or always_master:
            connect = sentinel.master_for(
                master_name,
                socket_timeout=sentinel_timeout,
                db=db,
            )
        else:
            connect = sentinel.slave_for(
                master_name,
                socket_timeout=sentinel_timeout,
                db=db,
            )
        return connect

    def _close_write(self):
        if self._client_write:
            for c in self._client_write.connection_pool._available_connections:
                    c.disconnect()
            self.log.debug("client_write closed")

    def _close_read(self):
        if self._client_read:
            for c in self._client_read.connection_pool._available_connections:
                c.disconnect()
            self.log.debug("client_read closed")

    def close(self, **kwargs):
        """
        Closing old connections, as master may change in time of inactivity.
        """
        self.log.debug("close called")
        if DJANGO_REDIS_CLOSE_CONNECTION:
            self._close_read()
            self._close_write()

            del self._client_write
            del self._client_read
            self._client_write = None
            self._client_read = None
