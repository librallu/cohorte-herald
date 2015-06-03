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
    Validate, Invalidate, Instantiate, Property, Requires
import herald
import logging
import herald.routing_constants
import threading
import time
from herald.beans import Message

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

def print_message(logger, message):
    """
    Print message in a logger
    :param logger: logger to use
    :param message: message to print
    :return: nothing
    """
    pass
    n = 25
    logger.info("="*n)
    logger.info("Message received {} :".format(message.uid))
    logger.info("subject: {}".format(message.subject))
    logger.info("content: {}".format(message.content))
    logger.info("="*n)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-roads-factory")
@Provides(herald.SERVICE_LISTENER)  # for getting messages of type reply
@Provides(herald.routing_constants.ROUTING_INFO)
@Requires('_herald', herald.SERVICE_HERALD_INTERNAL)  # for sending messages
@Requires('_hellos', herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)
@Property('_filters', herald.PROP_FILTERS, ['herald/routing/roads/*'])
@Property('_road_delay', 'road_delay', 5)
@Instantiate('herald-routing-roads')
class Roads:
    """
    Herald Routing Roads sender Daemon

    It's purpose is to send every period of time Roads to
    neighbours routers. It keep in mind how to send messages to
    a distant peer.
    It can be used by calling the method get_next_hop(peer) to
    get the next hop to accessing peer.
    """

    def __init__(self):
        """
        Sets up members
        """
        # remote objects
        self._herald = None
        self._hellos = None

        # private objects
        self._active = None
        self._lock = None           # for mutex
        self._loop_thread = None    # looping thread
        self._metric = None         # destination -> time (distance announced)
        self._next_hop = None       # destination -> neighbour (next hop)

    @Validate
    def validate(self, context):
        """
        When all requirements are satisfied
        :param context:
        :return: nothing
        """
        self._lock = threading.Lock()
        self._active = True
        self._metric = {}
        self._next_hop = {}
        self._loop_thread = threading.Thread(target=self._loop, args=())

        # launching daemon thread
        self._loop_thread.start()

    @Invalidate
    def invalidate(self, context):
        """
        when some requirements are unsatisfied
        :param context:
        :return: nothing
        """
        self._active = False
        self._metric.clear()
        self._next_hop.clear()
        self._loop_thread.join()  # wait for looping thread to stop current iteration

    def _loop(self):
        """
        main loop of the road sender daemon.
        It stops when the _active method is set to false
        and the current iteration is over.
        :return: nothing
        """
        while self._active:
            for target in self._hellos.get_neighbours_routers():
                self._send_roads_to(target)
            # wait a moment
            time.sleep(self._road_delay)

    def get_next_hop_to(self, destination):
        """
        :param: destination: a given destination uid
        :return: The next hop to the destination. None if there is no known roads
        """
        # if it's a direct neighbour
        if self._hellos.is_reachable(destination):
            return destination
        # if it's reachable from a neighbour router
        if destination in self._next_hop:
            return self._next_hop[destination]
        # if there is no known roads
        return None

    def get_next_hops(self):
        """
        get a dict() object of next_hop for all known
        pairs.
        :return: returns peer -> next_hop
        """
        return self._next_hop

    def get_accessible_peers(self):
        """
        :return: a dict object peer -> delay
        """
        res = {}
        for i in self._metric:
            if self._hellos.is_reachable(self._next_hop[i]):
                res[i] = self._metric[i]+self._hellos.get_neighbour_metric(self._next_hop[i])
        return res

    def _send_roads_to(self, target):
        """
        Send road message to a target
        """
        roads = {}
        for i in self._next_hop:
            # if the receiver is not the gateway
            if self._next_hop[i] != target:
                # if the gateway is reachable
                if self._hellos.is_reachable(self._next_hop[i]):
                    roads[i] = self._metric[i]+self._hellos.get_neighbour_metric(self._next_hop[i])
        # add neighbours to message
        for i in self._hellos.get_neighbours():
            if i != target:
                if i not in roads or roads[i] > self._hellos.get_neighbours()[i]:
                    roads[i] = self._hellos.get_neighbours()[i]
        msg = Message('herald/routing/roads/', content=str(roads))
        _logger.info("------ SENDING -------")
        print_message(_logger, msg)
        self._herald.fire(target, msg)

    def change_road(self, next_hop, metric, destination):
        """
        Change road for going to destination with next_hop and metric
        If next_hop or metric is None, delete the road
        :param: next_hop:
        :param: metric:
        :param: destination:
        :return: nothing
        """
        self._lock.acquire()
        # if delete operation
        if not next_hop or not metric:
            if destination in self._next_hop:
                del self._next_hop[destination]
            if destination in self._metric:
                del self._metric[destination]
            _logger.info("Deleting road to {}".format(destination))
        else:
            self._next_hop[destination] = next_hop
            self._metric[destination] = metric
        self._lock.release()

    def herald_message(self, herald_svc, message):
        """
        An Herald reply message has been received.
        It measures delay between sending and answer receiving.
        """
        self._lock.acquire()
        _logger.info("-"*10 + " RECEIVE")
        info = eval(message.content)
        _logger.info(info)
        sender_uid = message.sender
        # forget all roads from sender_uid
        next_hop = {}  # a new self._next_hop
        metric = {}  # a new self._metric
        for i in self._next_hop:
            if i != sender_uid:
                next_hop[i] = self._next_hop[i]
                metric[i] = self._metric[i]
        # add all new roads from sender_uid
        # only if neighbour is reachable
        if self._hellos.is_reachable(sender_uid):
            for i in info:
                if i not in self._hellos.get_neighbours():
                    if i not in next_hop:  # if there is no info about this road
                        next_hop[i] = sender_uid
                        metric[i] = info[i]
                    elif metric[i] > info[i]:  # if we get a better metric
                        next_hop[i] = sender_uid
                        metric[i] = info[i]

        self._next_hop = next_hop
        self._metric = metric
        self.print_routes()
        self._lock.release()

    def print_routes(self):
        """
        print route tables
        :return: nothing
        """
        n = 30
        _logger.info("*"*n)
        _logger.info("next_hop: {}".format(self._next_hop))
        _logger.info("metric: {}".format(self._metric))
        _logger.info("*"*n)
