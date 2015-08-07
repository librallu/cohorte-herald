#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald use case LED and sensor

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
    Validate, Invalidate, Instantiate, Property, Requires, Provides
import logging

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-generic-storage-factory")
@Provides('sensor.generic.storage')
@Property("_export", "service.exported.interfaces", "*")
@Instantiate('herald-generic-storage')
class PybTest:

    def __init__(self):
        self._values = None

    @Validate
    def validate(self, _):
        self._values = []

    @Invalidate
    def invalidate(self, _):
        self._values = None

    def store(self, value):
        self._values.append(value)
        print('NEW VALUE STORED: {}'.format(value))
        print('VALUES: {}'.format(self._values))