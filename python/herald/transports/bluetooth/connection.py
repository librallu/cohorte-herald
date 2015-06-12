#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Bluetooth connection object

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

import threading
import bluetooth
from herald.transports.bluetooth.serial_automata import SerialAutomata

HELLO_MESSAGE = '[[[HELLO]]]'
DELIMITER = '|||'
PORT = 1


class Connection:

    def __init__(self, mac):
        self._mac = mac
        self._valid = False
        self._socket = None
        self._automata = SerialAutomata(DELIMITER)
        self._thread = threading.Thread(target=self._init_connection, args=())

    def _init_connection(self):
        """
        initialize connection with a two step discovery.
        - first: send a HELLO_MESSAGE to the device
        - second: wait a HELLO_MESSAGE from the device
        """
        # connection with the peer
        self._socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._socket.connect((self._mac, PORT))

        # step 1 - send a HELLO_MESSAGE
        self.send_message(HELLO_MESSAGE)

        # step 2 - wait a HELLO_MESSAGE
        msg = self.receive_message()
        while msg != HELLO_MESSAGE:
            msg = self.receive_message()
            print(msg)
        print("connection ok with pair {}".format(self._mac))
        self._valid = True

    def send_message(self, msg):
        """
        Sends message msg to the peer
        :param msg: message to send
        """
        self._socket.send(msg+DELIMITER)

    def receive_message(self):
        """
        :return: message read from the peer
        """
        while not self._automata.any_message():
            self._automata.read(self._socket.recv(1024))
        return self._automata.get_message()

    def is_valid(self):
        """
        :return: True if the connection is valid
            false elsewhere
        """
        return self._valid
