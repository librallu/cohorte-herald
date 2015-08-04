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


class NeighbourInformation:
    """
    Class that contains informations about a known peer uid:

     - it's metric (float)
     - it's last ask (datetime)
     - if it is a router (boolean)
    """

    def __init__(self):
        """
        Init attributes
        """
        self._data = {}
        self._lock = threading.Lock()   # for mutex

    def add_uid(self, uid, metric=None, last_ask=None, router=None):
        """
        adds or replace uid data in the neighbourInformation
        """
        self._data[uid] = {
            'metric': metric,
            'last_ask': last_ask,
            'router': router
        }

    def change_field(self, uid, name, value):
        """
        :param uid: peer uid
        :param name: name of the field
        :param value: new value for name
        """
        with self._lock:
            if uid not in self._data:
                self.add_uid(uid)
            self._data[uid][name] = value

    def get_field(self, uid, name):
        """
        Gets the value of the field *name* for *uid*

        :param uid: peer uid
        :param name: name of the field
        :return: value of the field
        """
        return self._data[uid][name]

    def del_uid(self, uid):
        """
        Delete uid from neighbourInformation.
        Does nothing if uid not existing.
        """
        with self._lock:
            if self.exists(uid):
                del self._data[uid]

    def exists(self, uid):
        """
        :return: True if uid exists in information, False elsewhere
        """
        return uid in self._data

    def clear(self):
        """
        Removes all elements in data
        """
        with self._lock:
            self._data.clear()

    def neighbours_set(self, field=None):
        """
        return a set of neighbours.
        It is possible to specify a field name
        to extract only elements that are not None

        :param field: field to get non null info
        :return: set of neighbours uid
        """
        if field is None:
            return set(self._data)
        data = set()
        for i in self._data:
            if self._data[i][field] is not None:
                data.add(i)
        return data


@ComponentFactory("herald-routing-hellos-factory")
@Provides(herald.SERVICE_LISTENER)  # for getting messages of type reply
@Provides(herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)  # for metrics
@Requires('_herald', herald.SERVICE_HERALD_INTERNAL)  # for sending messages
@Requires('_directory', herald.SERVICE_DIRECTORY)  # for getting neighbours
@Property('_filters', herald.PROP_FILTERS, ['herald/routing/reply/*'])
@Property('_hello_delay', 'hello_delay', 5)
@Property('_hello_timeout', 'hello_timeout', 12)
@Property('_granularity', 'metric_granularity', .00003)
@Instantiate('herald-routing-hellos')
class Hellos:
    """
    Herald Routing Hello sender Daemon

    It's purpose is to send every period of time hello messages to
    neighbours to measure the distance from them (latency).
    It tells the SendRoad daemon if there is any changes
    in the connections with neighbours.

    possible improvements:

     - keep the current asking uid for checking if
       the peer don't respond to an other message.
       e.g.

        - if a hello message is sent at time 0.
        - an other hello message is sent at time 5 because the peer doesn't respond
        - the peer responds to the first hello message at time 6.
        - in the current implementation, the metric will be 1 (6-5) but the real
          metric should be 6 (6-0)

    GET_NEIGHBOURS_AVAILABLE provides :

    - get_neighbour_metric(neighbour)
    - get_neighbours()
    - is_reachable(neighbour)
    - get_neighbours_routers()
    - change_metric(peer_uid, new_value)
    - set_not_reachable(neighbour)
"""

    def __init__(self):
        """
        Sets up members
        """
        # remote objects
        self._herald = None
        self._directory = None

        # private objects
        self._neighbours = None     # uid -> NeighbourInfo
        self._lock = None           # for mutex
        self._loop_thread = None    # looping thread
        self._active = None         # True if looping thread active

        # Properties
        self._hello_timeout = None
        self._granularity = None
        self._hello_delay = None

    @Validate
    def validate(self, context):
        """
        When all requirements are satisfied

        :param context:
        :return: nothing
        """
        self._neighbours = NeighbourInformation()
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
        # wait for looping thread to stop current iteration
        self._loop_thread.join()

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
        if router == 'R':  # if it is a router
            self._neighbours.change_field(peer_uid, 'router', True)
            # _logger.info("router detected : {}".format(peer_uid))
        else:
            self._neighbours.change_field(peer_uid, 'router', False)
            # _logger.info("a non router detected : {}".format(peer_uid))

    def herald_message(self, herald_svc, message):
        """
        An Herald reply message has been received.
        It measures delay between sending and answer receiving.
        """
        sender_uid = message.sender
        # if sender_uid have a last_ask existing
        if sender_uid in self._neighbours.neighbours_set(field='last_ask'):
            old_time = self._neighbours.get_field(sender_uid, 'last_ask')
            delay = self._time_between(old_time)
            # we compute the new metric for sender_uid
            self.change_metric(sender_uid, delay)
            # we delete the field last_ask because we have now our answer
            self._neighbours.change_field(sender_uid, 'last_ask', None)
            # we set the field router if it's a router
            self._extract_info_from_reply(sender_uid, message.subject)

    def get_neighbour_metric(self, neighbour):
        """
        returns a neighbour metric

        :param neighbour: given neighbour
        :return: known metric (latency) from neighbour
            None if there is no connection

        """
        # if we know a metric for the neighbour
        if neighbour in self._neighbours.neighbours_set(field='metric'):
            metric = self._neighbours.get_field(neighbour, 'metric')
            # if it is superior to the timeout
            # return None (no link)
            if metric >= self._hello_timeout:
                return None
            return metric
        return None

    def get_neighbours(self):
        """
        returns all the information known about neighbours

        :return: a set object with neighbour UID
        """
        return self._neighbours.neighbours_set(field='metric')

    def is_reachable(self, neighbour):
        """
        :param neighbour: neighbour to check
        :return: return true if neighbour is reachable, false elsewhere
        """
        if neighbour in self._neighbours.neighbours_set(field='metric'):
            metric = self._neighbours.get_field(neighbour, 'metric')
            return metric is not None and metric < self._hello_timeout
        else:
            return False

    def get_neighbours_routers(self):
        """
        :return: known neighbours that are routers
        """
        res = set()
        for i in self._neighbours.neighbours_set(field='router'):
            if self._neighbours.get_field(i, 'router'):
                if self._neighbours.get_field(i, 'metric') is not None:
                    res.add(i)
        return res

    def _send_hello(self, target, msg):
        """
        Send a message to a given target

        :param target: target for the message
        :param msg: message to send
        :return: nothing
        """
        self._neighbours.change_field(target, 'last_ask', datetime.datetime.now())
        try:
            self._herald.fire(target, msg)
        except herald.exceptions.NoTransport:  # no more link
            self.set_not_reachable(target.uid)

    def change_metric(self, peer_uid, new_value):
        """
        change the metric of a given pair for a given value.
        It changes the value if it's greater than _hello_timeout
        or if the absolute difference is greater than _granularity.

        :param peer_uid: peer to set the metric
        :param new_value: new metric value
        :return: nothing
        """
        if peer_uid in self._neighbours.neighbours_set(field='metric'):
            old_value = self._neighbours.get_field(peer_uid, 'metric')
            diff = abs(new_value-old_value)
            if diff >= self._granularity or new_value >= self._hello_timeout:
                self._neighbours.change_field(peer_uid, 'metric', new_value)
        else:
            self._neighbours.change_field(peer_uid, 'metric', new_value)

    def set_not_reachable(self, peer_uid):
        """
        set a pair not reachable in neighbourhood.

        :param peer_uid: peer to set
        :return: nothing
        """
        self._neighbours.del_uid(peer_uid)

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
                if target.uid not in waiting_for:
                    # we don't send messages if we are waiting for one
                    self._send_hello(target.uid, Message('herald/routing/hello/'))
                    # _logger.info("hello sent to {}".format(target))
            # deleting known peers if timeout exceeded
            waiting_for = self._neighbours.neighbours_set(field='last_ask')
            for target in waiting_for:
                ask_time = self._neighbours.get_field(target, 'last_ask')
                if self._time_between(ask_time) > self._hello_timeout:
                    # in this case, we have the timeout elapsed
                    self.set_not_reachable(target)
                    # _logger.info("hello sent to {}".format(target))
            # deleting peers which are not in our directory
            for peer in self.get_neighbours():
                if peer not in {i.uid for i in self._directory.get_peers()}:
                    self.set_not_reachable(peer)
            # wait a moment
            time.sleep(self._hello_delay)
