#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Bluetooth transport implementation

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

# Herald HTTP
from . import ACCESS_ID, SERVICE_BLUETOOTH_RECEIVER, SERVICE_BLUETOOTH_TRANSPORT, \
    CONTENT_TYPE_JSON

# Herald Core
from herald.exceptions import InvalidPeerAccess
import herald
import herald.beans as beans
import herald.utils as utils

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Requires, Provides, \
    Property, BindField, Validate, Invalidate, Instantiate, RequiresBest
from pelix.utilities import to_str
import pelix.utilities
import pelix.threadpool
import pelix.misc.jabsorb as jabsorb

# Standard library
import json
import logging
import time

import bluetooth

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory('herald-bluetooth-transport-factory')
@RequiresBest('_probe', herald.SERVICE_PROBE)
@Requires('_directory', herald.SERVICE_DIRECTORY)
@Requires('_local_recv', SERVICE_BLUETOOTH_RECEIVER)
@Provides((herald.SERVICE_TRANSPORT, SERVICE_BLUETOOTH_TRANSPORT))
@Property('_access_id', herald.PROP_ACCESS_ID, ACCESS_ID)
@Instantiate('herald-bluetooth-transport')
class HttpTransport(object):
    """
    Bluetooth sender for Herald.
    """

    def __init__(self):
        """
        Sets up the transport
        """
        # Herald Core directory
        self._directory = None

        # Debug probe
        self._probe = None

        # Properties
        self._access_id = ACCESS_ID

        # Local UID
        self.__peer_uid = None