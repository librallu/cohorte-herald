#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Bluetooth beans definition

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

import functools

from . import ACCESS_ID


@functools.total_ordering
class BluetoothAccess:
    """
    Description of a Bluetooth access
    """

    def __init__(self, mac, name):
        """
        Sets up access information.

        :param mac: MAC adress of the device
        :param name: visible name of the device
        :return: nothing
        """
        self.__mac = mac
        self.__name = name

    def __hash__(self):
        """
        Hash based on the MAC address of the pair
        """
        return hash(self.__mac)

    def __lt__(self, other):
        """
        :param other: other BluetoothAccess
        :return: False if incomparable or greater than other, True elsewhere
        """
        if isinstance(other, BluetoothAccess):
            self.mac < other.mac
        return False

    def __eq__(self, other):
        """
        :param other: other BluetoothAccess
        :return: False if incomparable or different than other, True elsewhere
        """
        if isinstance(other, BluetoothAccess):
            self.mac == other.mac
        return False

    def __str__(self):
        """
        :return: string representation
        """
        return "Bluetooth({0}:{1})".format(self.mac, self.name)

    @property
    def access_id(self):
        """
        :return: acces id associated to this kind of access
        """
        return ACCESS_ID

    @property
    def mac(self):
        """
        :return: MAC address of access
        """
        return self.__mac

    @property
    def name(self):
        """
        :return: name of access
        """
        return self.__name

    @property
    def access(self):
        """
        :return: tuple (mac, name)
        """
        return self.mac, self.name

    def dump(self):
        """
        :return: the content to store in a directory dump.
            For describing this access.
        """
        return self.access
