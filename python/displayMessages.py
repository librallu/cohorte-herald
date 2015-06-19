#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Display incomming messages component

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
    Instantiate, Property

import herald


@ComponentFactory("herald-display-messages-factory")
@Provides(herald.SERVICE_LISTENER)
@Property('_filters', herald.PROP_FILTERS, ['*'])
@Instantiate('herald-display-messages')
class FireServer:
    """
    A simple component that have a function that returns the number
    of usages of this function.
    """

    def __init__(self):
        # properties
        self._filters = None

    def herald_message(self, herald_svc, message):
        """
        A herald message has been received !
        :param herald_svc:
        :param message:
        :return:
        """
        print('---- RECEIVED -----')
        print('subject: {}'.format(message.subject))
        print('=== content:')
        print(message.content)
        print('=== header: ')
        print(message.headers)
        print('=== metadata')
        print(message.metadata)
        print('--------------------')
