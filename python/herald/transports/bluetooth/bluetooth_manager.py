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
import herald.transports.peer_contact as peer_contact

from . import ACCESS_ID
from . import beans

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-bluetooth_manager-factory")
@Requires('_discovery', herald.transports.bluetooth.BLUETOOTH_DISCOVERY_SERVICE)
@Requires('_directory', herald.SERVICE_DIRECTORY)
@Requires('_herald', herald.SERVICE_HERALD_INTERNAL)  # for receiving messages
@Provides(herald.transports.bluetooth.BLUETOOTH_MANAGER_SERVICE)
@Instantiate('herald-bluetooth_manager-test')
class BluetoothManager:

    def __init__(self):
        self._discovery = None
        self._coms = None
        self.__contact = None
        self._discovery = None
        self._herald = None

    def _when_added(self, mac):
        if self._coms is not None:
            self._coms.update_devices([mac])

    def _register_herald(self, msg, _):
        # extracting string before to pass it
        # to the rest of the system
        # try:
        print('\n\npassing to herald :\n\n')
        print(msg)
        received_msg = herald.utils.from_json(msg)

        # prepare bean
        sender_uid = received_msg.sender
        received_msg.add_header(herald.MESSAGE_HEADER_SENDER_UID, sender_uid)
        received_msg.set_access(ACCESS_ID)
        extra = {ACCESS_ID: received_msg.content['accesses']['bluetooth']}
        received_msg.set_extra(extra)

        # if the message is a discovery message
        if received_msg.subject.startswith(peer_contact.SUBJECT_DISCOVERY_PREFIX):
            # Handle discovery message
            self.__contact.herald_message(self._herald, received_msg)
        else:
            self._herald.handle_message(received_msg)

    @staticmethod
    def __load_dump(message, description):
        """
        Loads and updates the remote peer dump with its HTTP access

        :param message: A message containing a remote peer description
        :param description: The parsed remote peer description
        :return: The peer dump map
        """
        # print('message.access:{} ACCESS_ID:{}'.format(message.access, ACCESS_ID))
        if message.access == ACCESS_ID:
            # Forge the access to the HTTP server using extra information
            extra = message.extra
            description['accesses'][ACCESS_ID] = \
                beans.BluetoothAccess(extra[ACCESS_ID]).dump()
            print(description)
        return description

    @Validate
    def validate(self, _):
        """
        :param _: context (not used)
        """
        print('starting bluetooth manager')
        self._coms = CommunicationSet()
        self._discovery.listen_new(self._when_added)
        self._coms.register_leaving_callback(
            self._discovery.delete_mac
        )
        self.register_callback(self._register_herald)

        # Prepare the peer contact handler
        self.__contact = peer_contact.PeerContact(
            self._directory, self.__load_dump, __name__ + ".contact")

    @Invalidate
    def invalidate(self, _):
        """
        :param _: context (not used)
        """
        _logger.info('CLOSING BLUETOOTH CONNECTIONS')
        self._coms.close()
        while not self._coms.close_ended():
            # waiting close of all connections
            pass
        self._coms = None
        _logger.info('BLUETOOTH CONNECTIONS SUCCESSFULLY CLOSED')

        # Clean up internal storage
        if self.__contact:
            self.__contact.clear()
            self.__contact = None

    def fire(self, mac, message):
        """
        send a message to a device
        :param mac: mac address of the device
        :param message: string message to send
        :return: True if the message has been
        successfully sent and False elsewhere
        """

        _logger.info('SENDING MESSAGE {}'.format(message))
        print(mac)
        print(type(mac))
        if not self._coms.has_connection(mac):
            return False
        print('*'*30)
        self._coms.send_to(mac, message)
        return True

    def register_callback(self, f):
        """
        :param f: f(msg, mac) that is called when
        a message is received.
        """
        print('callback registered in bluetooth manager')
        self._coms.register_callback(f)

    def listen_del(self, f):
        """
        register f for be called when a peer
        is removed
        :param f: f(mac) added to callbacks
        :return: nothing
        """
        self._coms.register_leaving_callback(f)

    def listen_new(self, f):
        """
        register f for be called when a peer
        is new
        :param f: f(mac) added to callbacks
        :return: nothing
        """
        self._coms.register_starting_callback(f)
