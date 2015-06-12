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

def to_string(msg):
    if type(msg) is bytes:
        msg = str(msg)
        msg = msg[2:]
        return msg[:-1]
    else:
        return msg

class Connection:

    def __init__(self, mac, timeout=None, err_callback=None):
        """
        constructor of a connection.
        Start a new process to initialize the connection
        with the distant pair. This process puts the is_valid()
        method to True when it's done.
        :param mac: mac address of the peer bluetooth device
        :param timeout: if set to None, it can wait forever,
                elsewhere, waits the timeout before quitting.
        :param err_callback: function to be called if
                there is an error when initialization connection.
        :return:
        """
        print("starting init")
        self._timeout = timeout
        self._err_callback = err_callback
        self._mac = mac
        self._valid = False
        self._socket = None
        self._automata = SerialAutomata(DELIMITER)
        print("init automata")
        self._thread = threading.Thread(target=self._init_connection)
        self._thread.start()
        print("ending init")

    def _init_connection(self):
        """
        initialize connection with a two step discovery.
        - first: send a HELLO_MESSAGE to the device
        - second: wait a HELLO_MESSAGE from the device
        """
        try:
            # connection with the peer
            self._socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._socket.connect((self._mac, PORT))
            self._socket.settimeout = self._timeout

            # step 1 - send a HELLO_MESSAGE
            self.send_message(HELLO_MESSAGE)

            # step 2 - wait a HELLO_MESSAGE
            msg = self.receive_message()
            while msg is not None and msg != HELLO_MESSAGE:
                msg = self.receive_message()
            if msg is None:
                print("connection aborted with pair {}".format(self._mac))
                self._err_callback()
            else:
                self._valid = True
        except bluetooth.btcommon.BluetoothError:
            if self._err_callback is None:
                pass
            else:
                self._err_callback()

    def send_message(self, msg):
        """
        Sends message msg to the peer
        :param msg: message to send
        """
        self._socket.send(msg+DELIMITER)

    def receive_message(self):
        """
        :return: message read from the peer
            None if timeout passed
        """
        while not self._automata.any_message():
            recv = to_string(self._socket.recv(1))
            if recv == '':  # if timeout passed
                print('connection({}): timeout passed'.format(self._mac))
                return None
            self._automata.read(recv)
        return self._automata.get_message()

    def close(self):
        """
        Close the connection with the pair
        """
        self._socket.close()

    def is_valid(self):
        """
        :return: True if the connection is valid
            false elsewhere
        """
        return self._valid
