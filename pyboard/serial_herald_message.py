#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Bluetooth Message Implementation

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

import pyb

DELIMITER = ':'
HELLO_MESSAGE = b'[[[HELLO]]]'


def to_string(msg):
    """
    Take a str and returns the same object
    or take a bytes object and transform it
    to a string object (useful for comparisons)
    :param msg: message to transform to a string
    :return: resulted string
    """
    if type(msg) is bytes:
        msg = str(msg)
        msg = msg[2:]
        return msg[:-1]
    else:
        return msg


def to_bluetooth_message(msg):
    """
    put a bluetooth message to the peer.
    It adds correct delimiters
    :param msg: string message
    :return: bluetooth message as a string
    """
    msg = to_string(msg)
    return str(len(msg)) + DELIMITER + msg


def gen_uuid():
    """
    :return uuid of a message 32 random hexadecimal chars
    """
    res = ''
    for i in range(0, 32):
        res += hex(pyb.rng() % 16)[2:].upper()
    return res


class MessageReader:
    """
    reads herald message from bluetooth messages
    """

    def __init__(self, automata, hello_callback=None):
        self._automata = automata
        self._buffer = []
        self._hello_received_callback = hello_callback

    def read(self):
        if self._automata.any_message():
            msg = self._automata.get_message()
            # if there is a hello message
            # if len(self._buffer) == 0:
            # if we are not into reading a new herald message
            if to_string(msg) == to_string(HELLO_MESSAGE):
                # call the hello received callback
                if self._hello_received_callback:
                    self._hello_received_callback()
                # exiting before continuing in the
                # creation of an herald message
                return None
            self._buffer.append(msg)
            print('READER BUFFER: {}'.format(self._buffer))
            print('BUFFER LEN: {}'.format(len(self._buffer)))
            if len(self._buffer) >= 7:
                res = SerialHeraldMessage(*self._buffer)
                self._buffer.clear()
                return res
        return None


class SerialHeraldMessage:
    """
    Represents a bluetooth message implementation
    """

    def __init__(self,
                 subject,
                 sender_uid,
                 original_sender,
                 final_destination,
                 content,
                 reply_to='',
                 message_uid=''):
        self._subject = to_string(subject)
        self._sender_uid = to_string(sender_uid)
        self._original_sender = to_string(original_sender)
        self._final_destination = to_string(final_destination)
        self._content = to_string(content)
        self._reply_to = to_string(reply_to)
        self._message_uid = to_string(message_uid)
        if self._message_uid == '':
            self._message_uid = gen_uuid()

    def to_automata_string(self):
        res = ''
        res += to_bluetooth_message(self.subject)
        res += to_bluetooth_message(self.sender_uid)
        res += to_bluetooth_message(self.original_sender)
        res += to_bluetooth_message(self.final_destination)
        res += to_bluetooth_message(self.content)
        res += to_bluetooth_message(self.reply_to)
        res += to_bluetooth_message(self.message_uid)
        return res

    @property
    def subject(self):
        return self._subject

    @property
    def sender_uid(self):
        return self._sender_uid

    @property
    def original_sender(self):
        return self._original_sender

    @property
    def final_destination(self):
        return self._final_destination

    @property
    def content(self):
        return self._content

    @property
    def reply_to(self):
        return self._reply_to

    @property
    def message_uid(self):
        return self._message_uid

    def set_uid(self, new_uid):
        self._message_uid = new_uid

    def __str__(self):
        """
        :return: string representing the message
        """
        return """
        ===================
        message uid: {}
        subject: {}
        sender uid: {}
        original sender: {}
        final destination: {}
        replies to: {}
        -------------------
        {}
        -------------------
        """.format(self.message_uid, self.subject, self.sender_uid,
                   self.original_sender, self.final_destination, self.reply_to,
                   self.content)
