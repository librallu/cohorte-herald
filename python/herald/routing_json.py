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
    Validate, Invalidate, Instantiate, Requires, Property
import herald
import logging
import herald.routing_constants
import pelix.remote
import json

try:
    # Python 3
    import urllib.parse as urlparse

except ImportError:
    # Python 2
    import urlparse

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-info-factory")
@Provides(herald.routing_constants.ROUTING_JSON)  # for getting messages of type reply
@Provides(['pelix.http.servlet'])
@Requires('_routing', herald.routing_constants.ROUTING_INFO)  # for sending messages
@Requires('_hellos', herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)  # for metrics
@Property('_path', 'pelix.http.path', "/routing")
@Property('_reject', pelix.remote.PROP_EXPORT_REJECT, ['pelix.http.servlet', herald.SERVICE_DIRECTORY_LISTENER])
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
        self._hellos = None

        # local objects
        self._path = None

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

    def _html_neighbours(self):
        """
        :return: html code for neighbours
        """
        neighbours = ""
        for i in self.get_json_neighbours():
            neighbours += """
                <tr>
                    <td>{0}</td>
                    <td>{1} secs</td>
                </tr>
            """.format(i, self.get_json_neighbours()[i])

        return """
        <table border="1" style="width:100%">
            <tr>
                <th>Neighbour UID</th>
                <th>Metric</th>
            </tr>
            {}
        </table>
        """.format(neighbours)

    def _make_html(self):
        return """
        <html>
            <head>
                <title>{0}</title>
            </head>
            <body>
                <h1>Routing information</h1>

                <h2>Neighbours</h2>
                {1}

                <script type="text/javascript">
                    setInterval('window.location.reload()', 2000);
                </script>
            </body>
        </html>
        """.format("routing information", self._html_neighbours())

    @staticmethod
    def _make_json():
        return "{'msg': 'hello world !'}"

    def do_GET(self, request, response):
        """
        Handle a GET
        :param request: input request
        :param response: output request
        :return: nothing
        """
        query = request.get_path()[len(self._path)+1:].split('/')
        action = query[0].lower()
        if action == "html":  # if html ask
            content = self._make_html()
            response.send_content(200, content, mime_type="text/html")
        else:  # JSON ask
            content = self._make_json()
            response.send_content(200, content, mime_type="text/json")

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