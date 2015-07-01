#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Communication set for bluetooth links

:author: Luc Libralesso
:copyright: Copyright 2014, isandlaTech
:license: Apache License 2.0
:version: 0.0.3
:status: Alpha

..

    Copyright 2014 isandlaTech

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from herald.transports.bluetooth.connection import Connection

import threading


class CommunicationSet:
    """
    When a list of devices is send, the
    create_connection method creates a new
    connection with the bluetooth device.
    When it have a new device, it initiate
    a connection with it in two steps.
    It sends a hello and receives a hello too.

    At this point, the connection is initialized
    and applications can send and receive messages from it.
    """

    def __init__(self):
        self._connections = {}
        self._callbacks = []
        self._lock = threading.Lock()   # for mutex
        self._leave_callbacks = []
        self._start_callbacks = []

    def has_connection(self, mac):
        """
        :param mac: peer to test connection
        :return: True if there is a connection
                 False elsewhere
        """
        return mac in self._connections

    def list_connections(self):
        """
        :return: list of peers known in the set
        """
        return set(self._connections)

    def register_leaving_callback(self, f):
        """
        register f for be called when a peer
        is removed
        :param f: f(mac) added to callbacks
        :return: nothing
        """
        self._leave_callbacks.append(f)

    def register_starting_callback(self, f):
        """
        register f for be called when a peer
        is started
        :param f: f(mac) added to callbacks
        :return: nothing
        """
        self._start_callbacks.append(f)

    def _when_leave(self, mac):
        """
        called when a peer leaves
        :param mac: mac address of peer
        :return: nothing
        """
        for i in self._leave_callbacks:
            i(mac)
        if mac in self._connections:
            self._connections[mac].close()
            self._connections.pop(mac)

    def _when_start(self, mac):
        """
        called when a peer appears
        :param mac: mac address of the peer
        :return: nothing
        """
        for i in self._start_callbacks:
            i(mac)

    def send_to(self, target, msg):
        """
        sends a message msg to a target
        :param target: MAC address of the target
        :param msg: message to send
        """
        self._connections[target].send_message(msg)

    def register_callback(self, f):
        """
        :param f: f(msg, mac) that is called when
        a message is received.
        """
        with self._lock:
            self._callbacks.append(f)

    def _handle_messages(self, msg, mac):
        """
        Calls all registered functions when
        a message appears.
        :param msg: message
        :param mac: sender's mac address
        """
        with self._lock:
            for i in self._callbacks:
                print('{}:{}'.format(msg,mac))
                i(msg, mac)

    def update_devices(self, mac_list):
        """
        updates device connections. Start new connections.
        :param mac_list: list of devices list(mac)
        """
        # if a device needs to be added
        for i in mac_list:
            if i not in self._connections:
                print("set: creating connection with: {}".format(i))
                self._connections[i] = Connection(
                    i,
                    msg_callback=self._handle_messages,
                    timeout=10,
                    err_callback=self._when_leave,
                    start_callback=self._when_start
                )

    def close(self):
        """
        Close all known connections.
        """
        for i in self._connections:
            self._connections[i].close()

    def close_ended(self):
        """
        :return: True if close ended correctly, False elsewhere
        """
        for i in self._connections:
            if self._connections[i].is_valid():
                return False
        return True
