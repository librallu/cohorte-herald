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

from pelix.ipopo.decorators import ComponentFactory, Provides, \
    Validate, Invalidate, Instantiate, Requires
import herald
import logging
import herald.routing_constants

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-info-factory")
@Provides(herald.routing_constants.ROUTING_JSON)  # for getting messages of type reply
@Requires('_routing', herald.routing_constants.ROUTING_INFO)  # for sending messages
@Requires('_hellos', herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)  # for metrics
@Instantiate('herald-routing-info')
class RoutingJson:
    """
    Herald routing JSON.

    It's purpose is to send JSON information to a debug interface
    from the routing algorithm.

    For instance, getting the routing table metric and next_hop.
    And also known neighbours with metrics
    """

    def __init__(self):
        """
        sets up members
        :return: nothing
        """
        # remote objects
        self._routing = None

    @Validate
    def validate(self, context):
        """
        :param context:
        :return: nothing
        """
        pass

    @Invalidate
    def invalidate(self, context):
        """
        :param context:
        :return: nothing
        """
        pass

    def get_json_routing(self):
        """
        :return: a JSON object (dict) that contains the routing table with metrics.
        """
        return self._routing.get_accessible_pairs()

    def get_json_next_hop(self):
        """
        :return: a JSON object (dict) that contains the next hops
        """
        return self._routing.get_next_hops()

    def get_json_neighbours(self):
        """
        :return: a JSON object (dict) that contains neighbours with metrics.
        """
        res = {}
        for i in self._hellos.get_neighbours():
            res[i] = self._hellos.get_neighbour_metric(i)
        return res