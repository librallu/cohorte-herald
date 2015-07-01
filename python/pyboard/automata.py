#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Serial automata for receiving messages

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


class SerialAutomata:
    """
    Object that reads chars from the method read and extract messages from
    the flux.
    """

    def __init__(self):
        """
        initialize attributes
        """
        self._delimiter_char = ':'  # it can be anything except a number
        self._is_reading_number = True
        self._remaining = 0
        self._number_list = []
        self._current_message = ''
        self._previous_messages = []

    def any_message(self):
        """
        :return: True if there is available messages, false elsewhere
        """
        return self._previous_messages != []

    def get_message(self):
        """
        :return: First non-read message
        Throws an exception if there is no waiting message
        """
        return self._previous_messages.pop(0)

    def read(self, part):
        """
        reads a part of the message
        :part: string read in the serial input
        """
        for i in part:
            self._read_char(i)

    @staticmethod
    def int_from_numbers(l):
        """
        :param l: list of numbers
        :return: integer value of a list of numbers in a reverse order

        >>> SerialAutomata.int_from_numbers([])
        0

        >>> SerialAutomata.int_from_numbers([1,2,3])
        321
        """
        if l is None:
            return 0
        elif len(l) == 1:
            return l[0]
        else:
            return l[0]+10*SerialAutomata.int_from_numbers(l[1:])

    def _read_char(self, char):
        """
        Reads a char from the input flux.
        :param char: input
        """
        if self._is_reading_number:
            if ord('0') <= ord(char) <= ord('9'):
                self._number_list.insert(0, ord(char)-ord('0'))
            elif char == self._delimiter_char:
                self._remaining = self.int_from_numbers(self._number_list)
                self._number_list = []
                self._is_reading_number = False
            else:
                print('SERIAL AUTOMATA: bad data ignoring char {}'.format(char))
        else:  # if we are reading a message
            self._remaining -= 1
            if self._remaining == 0:
                self._previous_messages.append(self._current_message)
                self._current_message = ''
                self._is_reading_number = True
            else:
                self._current_message = self._current_message+char
