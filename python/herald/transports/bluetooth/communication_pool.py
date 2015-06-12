#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Communication pool for bluetooth links

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


class CommunicationPool:
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

    def has_connection(self, mac):
        """
        :param mac: peer to test connection
        :return: True if there is a connection
                 False elsewhere
        """
        return mac in self._connections

    def list_connections(self):
        """
        :return: list of peers known in the pool
        """
        return list(self._connections)

    def send_to(self, target, msg):
        """
        sends a message msg to a target
        :param target: MAC address of the target
        :param msg: message to send
        """
        self._connections[target].send_message(msg)

    def update_devices(self, mac_list):
        """
        updates device connections. Start new connections or stop
        some if necessary.
        :param mac_list: list of devices list(mac)
        """
        # if a device needs to be deleted
        tmp = {}
        for i in self._connections:
            if i in mac_list:
                tmp[i] = self._connections[i]
            else:
                print("pool: deleting connection with: {}".format(i))
                self._connections[i].close()

        # if a device needs to be added
        for i in mac_list:
            if i not in tmp:
                print("pool: creating connection with: {}".format(i))
                tmp[i] = Connection(i,
                                    timeout=10,
                                    err_callback=lambda: self._connections.pop(i)
                                    )

        self._connections = tmp
