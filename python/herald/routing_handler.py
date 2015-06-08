#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Routing service

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
    Provides, Instantiate, Property, Requires
import herald
import logging
import herald.routing_constants

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-replies-factory")
@Provides(herald.SERVICE_LISTENER)
@Requires('_routing', herald.routing_constants.ROUTING_INFO, optional=True)
@Property('_filters', herald.PROP_FILTERS, ['herald/routing/hello/*'])
@Instantiate('herald-routing-replies')
class MessageHandler:
    """
    Herald Routing Reply sender Daemon

    It's purpose is to listen when a Hello message is got.
    It next send back a Reply message to the sender.
    """

    def __init__(self):
        """
        Sets up members
        """
        self._routing = None

    def is_router(self):
        """
        :return: true if isolate is router, false elsewhere
        """
        if self._routing is None:
            return 'N'
        else:
            return 'R'

    def herald_message(self, herald_svc, message):
        """
        An Herald hello message has been received
        """
        subject = 'herald/routing/reply/{}/'.format(self.is_router())
        herald_svc.reply(message, None, subject=subject)
