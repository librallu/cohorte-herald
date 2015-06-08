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

from pelix.ipopo.decorators import ComponentFactory, Provides, \
    Validate, Invalidate, Instantiate

PING_PONG_SERVICE = "herald.test.ping_pong"

@ComponentFactory("herald-ping-test-factory")
@Provides(PING_PONG_SERVICE)
@Instantiate('herald-ping-test')
class PingTest:
    """
    A simple component that have a function that returns the number
    of usages of this function.
    """

    def __init__(self):
        self.count = None

    @Validate
    def validate(self, _):
        """
        when all the requirements are satisfied.
        :param _: context
        :return: nothing
        """
        self.count = 0

    @Invalidate
    def invalidate(self, _):
        """
        when some requirements are unsatisfied
        :param _: context
        :return: nothing
        """
        self.count = None

    def ping(self):
        """
        Dummy function that counts the numbers of calls
        it had.
        :return: number of calls it had
        """
        self.count += 1
        return self.count

