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

    def __init__(self, delimiter_string):
        """
        :param delimiter_string: delimiter pattern in the flux
            (needs to be at least 1 character long
        """
        self._delimiter_string = delimiter_string
        self._pattern_position = 0
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

    def _read_char(self, char):
        """
        Reads a char from the input flux.
        :param char: input
        """
        if char == self._delimiter_string[self._pattern_position]:
            # if we have matched the delimiter pattern
            if self._pattern_position == len(self._delimiter_string)-1:
                # the message is over (we have matched all the delimiter)
                self._pattern_position = 0
                self._previous_messages.append(self._current_message)
                self._current_message = ''
            else:
                # we check the next character
                self._pattern_position += 1
        else:
            # if we have not matched the delimiter
            self._current_message += char
            self._pattern_position = 0
