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
import datetime

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-hellos-factory")
@Provides(herald.SERVICE_LISTENER)  # for getting messages of type reply
@Provides(herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)  # for metrics
@Requires('_herald', herald.SERVICE_HERALD_INTERNAL)  # for sending messages
@Requires('_directory', herald.SERVICE_DIRECTORY)  # for getting neighbours
@Property('_filters', herald.PROP_FILTERS, ['herald/routing/reply/*'])
@Property('_hello_delay', 'hello_delay', 3)
@Property('_hello_timeout', 'hello_timeout', 10)
@Property('_granularity', 'metric_granularity', .03)
@Instantiate('herald-routing-hellos')
class Hellos:
    """
    Herald Routing Hello sender Daemon

    It's purpose is to send every period of time hello messages to
    neighbours to measure the distance from them (latency).
    It tells the SendRoad daemon if there is any changes
    in the connections with neighbours.

    possible improvements
    ---------------------

     - keep the current asking uid for checking if
       the peer don't respond to an other message.
    """

    def __init__(self):
        """
        Sets up members
        """
        # remote objects
        self._herald = None
        self._directory = None

        # private objects
        self._neighbours = None     # metric information
        self._lock = None           # for mutex
        self._loop_thread = None    # looping thread
        self._active = None         # True if looping thread active
        self._last_ask = None       # peer uid -> datetime
        self._routers = None        # peer set that are routers

    @Validate
    def validate(self, context):
        """
        When all requirements are satisfied
        :param context:
        :return: nothing
        """
        self._neighbours = {}
        self._routers = set()
        self._last_ask = {}
        self._lock = threading.Lock()
        self._active = True
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
        self._neighbours.clear()
        self._loop_thread.join()  # wait for looping thread to stop current iteration

    def _extract_info_from_reply(self, peer_uid, subject):
        """
        extract from a message content informations about peer
        :param peer_uid: sender uid
        :param subject: message subject
        :return: nothing
        """
        info = subject.split('/')
        router = None
        if len(info) >= 4:
            router = info[3]
        if router == 'R':
            self._routers.add(peer_uid)
            # _logger.info("new router: {}".format(peer_uid))
        else:
            if peer_uid in self._routers:
                self._routers.remove(peer_uid)
            # _logger.info("No new router: {}".format(peer_uid))

    def herald_message(self, herald_svc, message):
        """
        An Herald reply message has been received.
        It measures delay between sending and answer receiving.
        """
        herald.routing_constants.print_message(_logger, message)
        sender_uid = message.sender
        if sender_uid in self._last_ask:
            self._change_metric(sender_uid, self._time_between(self._last_ask[sender_uid]))
            self._lock.acquire()
            del self._last_ask[sender_uid]
            self._extract_info_from_reply(sender_uid, message.subject)
            self._lock.release()

    def get_neighbour_metric(self, neighbour):
        """
        returns a neighbour metric
        :param neighbour: given neighbour
        :return: known metric (latency) from neighbour None if there is no connection
        """
        if neighbour not in self._neighbours or self._neighbours[neighbour] > self._hello_timeout:
            return None
        return self._neighbours[neighbour]

    def get_neighbours(self):
        """
        returns all the information known about neighbours
        :return: a dict object with neighbour UID as key and metric as value

        potential bug: return value is a reference with an internal object.
        """
        return self._neighbours

    def is_reachable(self, neighbour):
        """
        :param neighbour: neighbour to check
        :return: return true if neighbour is reachable, false elsewhere
        """
        return neighbour in self._neighbours and self._neighbours[neighbour] < self._hello_timeout

    def get_neighbours_routers(self):
        """
        :return: known neighbours that are routers
        """
        return self._routers

    def _send_hello(self, target, msg):
        """
        Send a message to a given target
        :param target: target for the message
        :param msg: message to send
        :return: nothing
        """
        self._last_ask[target.uid] = datetime.datetime.now()
        self._herald.fire(target, msg)

    def _change_metric(self, peer_uid, new_value):
        """
        change the metric of a given pair for a given value.
        It changes the value if it's greater than _hello_timeout
        or if the absolute difference is greater than _granularity.
        :param peer_uid: peer to set the metric
        :param new_value: new metric value
        :return: nothing
        """
        # _logger.info("changing metric for {} to {}".format(peer_uid, new_value))
        if peer_uid in self._neighbours:
            if abs(new_value-self._neighbours[peer_uid]) >= self._granularity or new_value >= self._hello_timeout:
                self._neighbours[peer_uid] = new_value
        else:
            self._neighbours[peer_uid] = new_value
        # _logger.info("new granularity : {}".format(self._neighbours[peer_uid]))

    @staticmethod
    def _time_between(old_time):
        """
        return time in seconds between old time and now
        :param old_time: time to check with now
        :return: difference of time
        """
        return (datetime.datetime.now()-old_time).total_seconds()

    def _loop(self):
        """
        main loop of the hellos sender daemon.
        It stops when the _active method is set to false
        and the current iteration is over.
        :return: nothing
        """
        while self._active:
            # send a message for each entry in the directory
            for target in self._directory.get_peers():
                if target.uid not in self._last_ask:
                    # we don't send messages if we are waiting for one
                    self._send_hello(target, Message('herald/routing/hello/'))
                    # _logger.info("hello sent to {}".format(target))
                elif self._time_between(self._last_ask[target.uid]) > self._hello_timeout:
                    # in this case, we have the timeout elapsed
                    self._change_metric(target.uid, self._hello_timeout)
                    self._send_hello(target, Message('herald/routing/hello/'))
                    # _logger.info("hello sent to {}".format(target))
            # wait a moment
            time.sleep(self._hello_delay)
