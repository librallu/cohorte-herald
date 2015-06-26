#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Bluetooth scanner module

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
    Validate, Invalidate, Instantiate, Property, Provides
import logging
import herald.utils
import threading
import bluetooth


# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-bluetooth-discovery-factory")
@Provides(herald.transports.bluetooth.BLUETOOTH_DISCOVERY_SERVICE)
@Property('_interval', 'time_interval', 3)
@Property('_discovery_duration', 'discovery_duration', 5)
@Property('_filter', 'filter', ['PYBOARD'])
@Instantiate('herald-bluetooth-discovery-test')
class Discovery:
    """
    A simple component that asks for a remote service each time interval
    """

    def __init__(self):
        # private objects
        self._thread = None
        self._lock = None           # for mutex
        self._devices_names = None  # map: MAC -> name
        self._add_listeners = None  # callbacks when a new peer appears
        self._del_listeners = None  # callbacks when a peer disappears

        # properties
        self._interval = None
        self._filter = None
        self._discovery_duration = None

    @Validate
    def validate(self, _):
        """
        when all the requirements are satisfied.
        :param _: context
        :return: nothing
        """
        self._add_listeners = []
        self._del_listeners = []
        self._devices_names = dict()
        self._lock = threading.Lock()
        self._thread = herald.utils.LoopTimer(self._interval,
                                              self._search_devices)
        self._thread.start()

    @Invalidate
    def invalidate(self, _):
        """
        when some requirements are unsatisfied
        :param _: context
        :return: nothing
        """
        self._thread.cancel()

    def listen_new(self, f):
        """
        add a listener for new elements
        :param f: callback with a mac parameter
        :return: nothing
        """
        self._add_listeners.append(f)

    def listen_del(self, f):
        """
        add a listener for deleted elements in
        the bluetooth network
        :param f: callback with a mac parameter
        :return: nothing
        """
        self._del_listeners.append(f)

    def _check_differences(self, old, new):
        """
        checks differences between old and new neighbourhood.
        launch listener call if some peers showed up or disappeared
        :param old: old peer set
        :param new: new peer set
        :return: nothing
        """
        for i in old.difference(new):
            for f in self._del_listeners:
                f(i)
        for i in new.difference(old):
            for f in self._add_listeners:
                f(i)

    def _search_devices(self):
        """
        update attributes with the different bluetooth pairs known in the
        neighbourhood
        """
        try:
            devices = bluetooth.discover_devices(
                duration=self._discovery_duration,
                lookup_names=True)
            with self._lock:
                old = self._devices_names
                self._devices_names = dict()
                for i in devices:
                    if i[1] in self._filter:
                        self._devices_names[i[0]] = i[1]
                self._check_differences(set(old), set(self._devices_names))
        except bluetooth.btcommon.BluetoothError:
            self._devices_names = dict()

    def devices_set(self):
        """
        :return: set of devices detected.
        """
        return set(self._devices_names)

    def clean_devices(self):
        """
        clean known devices.
        !!! This method should be used only if there is a
        detected exception BluetoothError.
        """
        with self._lock:
            self._devices_names = dict()
