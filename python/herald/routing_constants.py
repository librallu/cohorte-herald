#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Routing service constants

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


GET_NEIGHBOURS_AVAILABLE = "herald.routing.neighbours_available"
"""
Specification of a service that gets all neighbours
available (i.e. with a protocol in common)
"""

ROUTING_INFO = "herald.routing.routing_info"
"""
Return the next hop for a destination.
None if there are no road to this destination.

It also allows to modify metrics for nodes
"""

ROUTING_JSON = "herald.routing.routing_json"
"""
Return a json string containing the routing
table of the node
"""

def print_message(logger, message):
    """
    Print message in a logger
    :param logger: logger to use
    :param message: message to print
    :return: nothing
    """
    pass
    n = 25
    # logger.info("="*n)
    # logger.info("Message received {} :".format(message.uid))
    # logger.info("subject: {}".format(message.subject))
    # logger.info("content: {}".format(message.content))
    # logger.info("="*n)
