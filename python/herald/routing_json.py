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
    Instantiate, Requires, Property
import herald
import logging
import herald.routing_constants
import pelix.remote

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory("herald-routing-info-factory")
# for getting messages of type reply
@Provides(herald.routing_constants.ROUTING_JSON)
@Provides(['pelix.http.servlet'])
# for sending messages
@Requires('_routing', herald.routing_constants.ROUTING_INFO)
# for metrics
@Requires('_hellos', herald.routing_constants.GET_NEIGHBOURS_AVAILABLE)
@Property('_path', 'pelix.http.path', "/routing")
@Property('_reject', pelix.remote.PROP_EXPORT_REJECT,
          ['pelix.http.servlet', herald.SERVICE_DIRECTORY_LISTENER])
@Instantiate('herald-routing-info')
class RoutingJson:
    """
    Herald routing JSON.

    It's purpose is to send JSON information to a debug interface
    from the routing algorithm.

    For instance, getting the routing table metric and next_hop.
    And also known neighbours with metrics


    ROUTING_JSON provides
    ---------------------

    - get_json_neighbours()
    - get_json_next_hop()
    - get_json_routing()

    Those methods give information about
    the routing algorithm on the router.
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

    def _html_neighbours(self):
        """
        :return: html code for neighbours
        """
        neighbours = ""
        for i in self.get_json_neighbours():
            is_router = i in self._hellos.get_neighbours_routers()
            metric = self.get_json_neighbours()[i]
            neighbours += """
                <tr>
                    <td>{0}</td>
                    <td>{1} secs</td>
                    <td>{2}</td>
                </tr>
            """.format(i, metric, is_router)

        return """
        <table border="1" style="width:100%">
            <tr>
                <th>Neighbour UID</th>
                <th>Metric</th>
                <th>Router?</th>
            </tr>
            {}
        </table>
        """.format(neighbours)

    def _html_peers(self):
        """
        :return: html code for peers
        """
        peers = ""
        for i in self.get_json_routing():
            next_hop = self.get_json_next_hop()[i]
            metric = self.get_json_routing()[i]
            peers += """
            <tr>
                <td>{0}</td>
                <td>{1}</td>
                <td>{2}</td>
            </tr>
            """.format(i, next_hop, metric)

        return """
        <table border="1" style="width:100%">
            <tr>
                <th>Peer UID</th>
                <th>Next Hop</th>
                <th>Metric</th>
            </tr>
            {}
        </table>
        """.format(peers)

    def _make_html(self):
        """
        :return: html page for the current
        state of routing components
        """
        neighbours = self._html_neighbours()
        peers = self._html_peers()
        return """
        <html>
            <head>
                <title>{0}</title>
            </head>
            <body>
                <h1>Routing information</h1>

                <h2>Neighbours</h2>
                {1}

                <h2>Distant peers</h2>
                {2}

                <script type="text/javascript">
                    setInterval('window.location.reload()', 2000);
                </script>
            </body>
        </html>
        """.format("routing information", neighbours, peers)

    def _make_json_neighbours(self):
        """
        :return: json neighbours of router
        """
        neighbour_list = [
            '\t\t{"uid": "' + i + '", "metric": ' +
            str(self.get_json_neighbours()[i]) + '", "router?": ' +
            str(i in self._hellos.get_neighbours_routers()) + '}'
            for i in self.get_json_neighbours()
        ]
        return ",\n".join(neighbour_list)

    def _make_json_distant(self):
        """
        :return: distant peer list of
        router
        """
        distant_list = [
            '\t\t{"uid": "' + i + '", "next": ' +
            str(self.get_json_routing()[i]) + ', "metric": "' +
            str(self.get_json_next_hop()[i]) + '"}'
            for i in self.get_json_routing()
        ]
        return ",\n".join(distant_list)

    def _make_json(self):
        """
        :return: router knowledge in json format string
        """
        return """{\n\t"neighbours": [\n""" + \
               self._make_json_neighbours() + \
               """\n\t],\n\t"distant": [\n""" + \
               self._make_json_distant()+"""\n\t]\n}"""

    def do_GET(self, request, response):
        """
        Handle a GET
        :param request: input request
        :param response: output request
        :return: nothing
        """
        query = request.get_path()[len(self._path)+1:].split('/')
        action = query[0].lower()

        if action == "json":  # JSON ask
            content = self._make_json()
            response.send_content(200, content, mime_type="text/json")
        else:  # if html ask
            content = self._make_html()
            response.send_content(200, content, mime_type="text/html")

    def get_json_routing(self):
        """
        :return: a JSON object (dict) that contains
        the routing table with metrics.
        """
        return self._routing.get_accessible_peers()

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
