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
import time
import datetime
from herald.transports.bluetooth.serial_automata import SerialAutomata
import logging

from herald.transports.bluetooth.serial_herald_message import \
    HELLO_MESSAGE, to_string, to_bluetooth_message, MessageReader
PORT = 1
DELAY_BETWEEN_TRIES = 10
TIMEOUT = 30

_logger = logging.getLogger(__name__)

class NotValid(Exception):
    def _init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Connection:

    def __init__(self, mac, msg_callback,
                 msg_handle_freq=1, timeout=3,
                 err_callback=None, start_callback=None):
        """
        constructor of a connection.
        Start a new process to initialize the connection
        with the distant pair. This process puts the is_valid()
        method to True when it's done.
        :param mac: mac address of the peer bluetooth device
        :param msg_callback: function that will be called with the
            received message (String) and the MAC address (String)
            in parameter
        :param msg_handle_freq: consult new messages every
            msg_handle_freq seconds (default 1)
        :param timeout: if set to None, it can wait forever,
                elsewhere, waits the timeout before quitting.
        :param err_callback: function to be called if
                there is an error when initialization connection.
        :param start_callback: function to be called when
                the peer is started (has responded correctly)
        :return:
        """
        self._timeout = timeout
        self._err_callback = err_callback
        self._start_callback = start_callback
        self._mac = mac
        self._msg_callback = msg_callback
        self._msg_handle_freq = msg_handle_freq
        self._valid = False
        self._closed = False
        self._socket = None
        self._automata = SerialAutomata()
        self._reader = None
        self._loop_thread = None
        self._init_thread = threading.Thread(target=self._init_connection)
        self._init_thread.start()
        self._alive_thread = None
        self._last_hello_received = None

    def _handle_hello(self):
        print('hello handled')
        self._last_hello_received = datetime.datetime.now()

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
            self._socket.settimeout(self._timeout)
            print('sending message 1')
            # step 1 - send a HELLO_MESSAGE
            self.send_message(HELLO_MESSAGE, check_valid=False, encapsulate=True)
            print('receiving message 2')
            # step 2 - wait a HELLO_MESSAGE
            msg = self._receive_message(check_valid=False)
            # if msg is None, connection is OK
            # if msg is '', the pair didn't respond

            # if timeout elapsed
            print('message 2 received {}'.format(msg))
            if msg == '':
                print("connection aborted with pair {}".format(self._mac))
                self.close()
            else:
                self._valid = True
                # starting handle thread for new messages
                self._reader = MessageReader(self._automata, self._handle_hello)
                self._loop_thread = threading.Thread(target=self._loop)
                self._loop_thread.start()
                self._alive_thread = threading.Thread(target=self._alive_loop)
                self._alive_thread.start()

                self._start_callback(self._mac)
        except bluetooth.btcommon.BluetoothError:
            if self._err_callback is None:
                pass
            else:
                _logger.info('{} disconnected: bluetooth exception'.format(self._mac))
                self._err_callback(self._mac)

    def _alive_loop(self):
        """
        loop that send a message every period of time, then
        waits for a response. If there is no response,
        close the connection
        """
        while self._valid:
            last_ask = datetime.datetime.now()
            time.sleep(DELAY_BETWEEN_TRIES)
            self.send_message(HELLO_MESSAGE, encapsulate=True)
            # time.sleep(TIMEOUT)
            if self._last_hello_received < last_ask - datetime.timedelta(seconds=TIMEOUT):
                _logger.info('{} disconnected: timeout elapsed'.format(self._mac))
                self._err_callback(self._mac)

    def _loop(self):
        """
        Loop function that checks if there is new
        messages on the bluetooth interface, put it
        in the automata and call the callback function
        (msg_callback) when there is a new message.
        """
        while self._valid:
            # add content in the automata
            try:
                recv = to_string(self._socket.recv(1))
            except bluetooth.btcommon.BluetoothError:
                recv = ''
            self._automata.read(recv)
            msg = self._reader.read()
            # msg = self._receive_message(with_timeout=True)
            if msg != '' and msg is not None:
                # print('connection: message obtained:{}'.format(msg))
                self._msg_callback(msg, self._mac)

    def send_message(self, msg, check_valid=True, encapsulate=False):
        """
        Sends message msg to the peer
        :param msg: message to send
        :param check_valid: if true, wait to the connection
        :param encapsulate: if true, encapsulate for bluetooth transmission
            False by default
        to be valid.
        """
        # wait for the communication
        while check_valid and not self._valid:
            pass
        if encapsulate:
            self._socket.send(to_bluetooth_message(msg))
        else:
            self._socket.send(msg)

    def _receive_message(self, with_timeout=True, check_valid=True):
        """
        WARNING: This is a blocking call.
        So, for common uses, please use
        the callback mechanism available.
        :param with_timeout: if true, waits until
        the timeout before returning nothing.
        :param check_valid: if True, raise NotValid
        if the connection is not valid (is_valid()==False)
        :return: message read from the peer
            None if timeout passed
        """
        while not self._automata.any_message():
            try:
                if check_valid and not self._valid:
                    raise NotValid('is_valid()=False')
                recv = to_string(self._socket.recv(1))
            except bluetooth.btcommon.BluetoothError:
                recv = ''
            if recv == '' and with_timeout:  # if timeout passed
                return ''
            if recv != '':
                self._automata.read(recv)
        msg = self._automata.get_message()
        print('msg received: {}'.format(msg))
        if to_string(HELLO_MESSAGE) == to_string(msg):
            self._handle_hello()
            return None
        return msg

    def close(self):
        """
        Close the connection with the pair
        """
        self._valid = False
        self._closed = True
        self._socket.close()

    def is_valid(self):
        """
        :return: True if the connection is valid
            false elsewhere
        """
        return self._valid

    def is_closed(self):
        """
        :return: True if connection is closed
        i.e. it is not used
        """
        return self._closed
