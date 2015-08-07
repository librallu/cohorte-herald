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
from herald.transports.bluetooth.serial_herald_message import *
import threading

from . import ACCESS_ID
from . import beans
from herald.beans import Message, MessageReceived

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
    """
    Implements a component that provides an interface to send herald messages
    to a bluetooth device and provides callbacks when a message appears.

    Requires:
        - herald.transports.bluetooth.BLUETOOTH_DISCOVERY_SERVICE
        - herald.SERVICE_DIRECTORY
        - herald.SERVICE_HERALD_INTERNAL

    Provides:
        - herald.transports.bluetooth.BLUETOOTH_MANAGER_SERVICE
    """

    def __init__(self):
        self._discovery = None
        self._coms = None
        self.__contact = None
        self._directory = None
        self._herald = None
        self._lock = threading.Lock()   # for mutex

    def herald_to_bluetooth(self, bean):
        """
        makes a bluetooth from a herald message

        :param bean: MessageBean
        :return: according bluetooth message
        """

        msg = SerialHeraldMessage(
            subject=bean.subject,
            sender_uid=self._directory.local_uid,
            original_sender=bean.headers['original_sender'] or self._directory.local_uid,
            final_destination=bean.headers.get('final_destination') or '',
            content=str(bean.content).replace('\n', ''),
            reply_to='',
            message_uid=bean.uid
        )
        print('SERIAL FORGED: {}'.format(msg))
        return msg

    @staticmethod
    def bluetooth_to_herald(msg, received=True):
        """
        makes a Herald message from a bluetooth message

        :param msg: bluetooth message
        :param received: if true, returns Received Message
        :return: according herald message
        """
        if received:
            res = MessageReceived(
                uid=msg.message_uid,
                subject=msg.subject,
                content=msg.content,
                sender_uid=msg.sender_uid,
                reply_to=None,
                access=ACCESS_ID
            )
        elif msg.reply_to:
            res = MessageReceived(
                uid=msg.message_uid,
                subject=msg.subject,
                content=msg.content,
                sender_uid=msg.sender_uid,
                reply_to=msg.reply_to,
                access=ACCESS_ID
            )
            res.add_header(herald.MESSAGE_HEADER_REPLIES_TO, msg.reply_to)

        else:
            res = Message(
                subject=msg.subject,
                content=msg.content
            )
            res.add_header(herald.MESSAGE_HEADER_SENDER_UID, msg.sender_uid)
            res.add_header(herald.MESSAGE_HEADER_UID, msg.message_uid)

        res.add_header("original_sender", msg.original_sender)
        if msg.final_destination:
            res.add_header("final_destination", msg.final_destination)

        if msg.group:
            print('BLUETOOTH MANAGER RECEIVES A BROADCAST')
            res.add_header('group', msg.group)
        return res

    def _when_added(self, mac):
        if self._coms is not None:
            self._coms.update_devices([mac])

    def _register_herald(self, msg, mac):
        # extracting string before to pass it
        # to the rest of the system
        # try:
        received_msg = self.bluetooth_to_herald(msg)
        # received_msg = herald.utils.from_json(msg)

        # prepare bean
        # sender_uid = received_msg.sender
        # received_msg.add_header(herald.MESSAGE_HEADER_SENDER_UID, sender_uid)
        # received_msg.set_access(ACCESS_ID)
        extra = {ACCESS_ID: mac}
        received_msg.set_extra(extra)

        # if the message is a discovery message
        if received_msg.subject.startswith(peer_contact.SUBJECT_DISCOVERY_PREFIX):
            # Handle discovery message
            received_msg.set_content(eval(received_msg.content))
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
        if message.access == ACCESS_ID:
            # Forge the access using extra information
            extra = message.extra
            description['accesses'][ACCESS_ID] = \
                [beans.BluetoothAccess(extra[ACCESS_ID]).dump()]
            print('description: {}'.format(description))
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
        with self._lock:
            _logger.info('SENDING MESSAGE {}'.format(message))
            print(mac)
            print(type(mac))
            if not self._coms.has_connection(mac):
                print('ERROR, NO BLUETOOTH CONNECTION')
                return False
            print('*'*30)
            self._coms.send_to(mac,
                               self.herald_to_bluetooth(message).to_automata_string())
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
