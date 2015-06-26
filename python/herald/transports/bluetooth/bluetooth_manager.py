#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Bluetooth connection manager. handle incoming messages,
can fire message, and notify when a new device appears or
a device disappears.

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


# Module version
__version_info__ = (0, 0, 3)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------

from pelix.ipopo.decorators import ComponentFactory, \
    Validate, Invalidate, Instantiate, Provides, Requires
import logging
import herald.utils
from herald.transports.bluetooth.communication_set import CommunicationSet

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-bluetooth-manager-factory")
@Requires('_discovery', herald.transports.bluetooth.BLUETOOTH_DISCOVERY_SERVICE)
@Provides(herald.transports.bluetooth.BLUETOOTH_MANAGER_SERVICE)
@Instantiate('herald-bluetooth-manager-test')
class BluetoothManager:

    def __init__(self):
        self._discovery = None

        self.coms = None

    def _when_change(self, mac):
        self.coms.update_devices(self._discovery.devices_set())

    def validate(self, _):
        """
        :param _: context (not used)
        """
        self.coms = CommunicationSet()
        self._discovery.listen_new(self._when_change)
        self._discovery.listen_del(self._when_change)

    def invalidate(self, _):
        """
        :param _: context (not used)
        """
        self.coms.close()
        while not self.coms.close_ended():
            pass
        self.coms = None

    def listen_new(self, f):
        """
        add a listener for new elements
        :param f: callback with a mac parameter
        :return: nothing
        """
        self._discovery.listen_new(f)

    def listen_del(self, f):
        """
        add a listener for deleted elements in
        the bluetooth network
        :param f: callback with a mac parameter
        :return: nothing
        """
        self._discovery.listen_del(f)

    def fire(self, mac, message):
        """
        send a message to a device
        :param mac: mac address of the device
        :param message: string message to send
        :return: True if the message has been
        successfully sent and False elsewhere
        """
        if not self.coms.has_connection(mac):
            return False
        self.coms.send_to(mac, message)
        return True

    def handle_messages