#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Test bluetooth module that displays informations from
bluetooth and print a message when a bluetooth device
appears or disappears.

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

from pelix.ipopo.decorators import ComponentFactory, Instantiate, Requires, Validate
import logging
import herald.utils

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-bluetooth-test-factory")
@Requires('_discovery', herald.transports.bluetooth.BLUETOOTH_DISCOVERY_SERVICE)
@Instantiate('herald-bluetooth-test-test')
class BluetoothTest:
    """ A simple Test bluetooth module that displays information from
        bluetooth and print a message when a bluetooth device
        appears or disappears.
    """

    def __init__(self):
        self._discovery = None

    @Validate
    def validate(self, _):
        # ask to be notified when there is a new device in the bluetooth network
        self._discovery.listen_new(lambda x: print(x+" appears"))
        self._discovery.listen_del(lambda x: print(x+" disappears"))
        print('LISTENING TO THE BLUETOOTH NETWORK !')
