#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Ping Pong test

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
    Validate, Invalidate, Instantiate, Property, Requires
import logging
import threading
import time
import ping

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

@ComponentFactory("herald-pong-test-factory")
@Requires('_ping', ping.PING_PONG_SERVICE)
@Property('_interval', 'time_interval', 2)
@Instantiate('herald-pong-test')
class PingTest:
    """
    A simple component that asks for a remote service each time interval
    """

    def __init__(self):
        # private objects
        self._loop_thread = None    # looping thread
        self._active = None         # True if looping thread active

        # remote objects
        self._ping = None

        # properties
        self._interval = None       # time interval between two calls

    @Validate
    def validate(self, _):
        """
        when all the requirements are satisfied.
        :param _: context
        :return: nothing
        """
        _logger.info("=== entering in validate ===")
        self._active = True
        self._loop_thread = threading.Thread(target=self._loop, args=())

        # launching daemon thread
        self._loop_thread.start()
        _logger.info("=== quitting validate ===")

    @Invalidate
    def invalidate(self, _):
        """
        when some requirements are unsatisfied
        :param _: context
        :return: nothing
        """
        _logger.info("=== entering in invalidate ===")
        self._active = False
        # wait for looping thread to stop current iteration
        self._loop_thread.join()
        _logger.info("=== quitting invalidate ===")

    def _loop(self):
        _logger.info("=== start main loop ===")
        while self._active:
            # wait a moment
            time.sleep(self._interval)
            # call ping
            _logger.info("=== "+str(self._ping.ping())+" ===")


