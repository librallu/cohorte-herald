#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald Remote Services discovery

:author: Thomas Calmant
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

# Herald
import herald.beans as beans
import herald.remote

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Requires, Provides, \
    Property, Instantiate
import pelix.remote.beans

# Standard library
import logging

# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory(herald.remote.FACTORY_DISCOVERY)
@Provides(pelix.remote.SERVICE_EXPORT_ENDPOINT_LISTENER)
@Provides((herald.SERVICE_LISTENER, herald.SERVICE_DIRECTORY_LISTENER))
@Requires('_directory', herald.SERVICE_DIRECTORY)
@Requires('_herald', herald.SERVICE_HERALD)
@Requires('_dispatcher', pelix.remote.SERVICE_DISPATCHER)
@Requires('_registry', pelix.remote.SERVICE_REGISTRY)
@Property('_filters', herald.PROP_FILTERS, ['herald/rpc/discovery/*'])
@Instantiate('herald-remote-discovery')
class HeraldDiscovery(object):
    """
    Remote services discovery and notification using Herald
    """
    def __init__(self):
        """
        Sets up the component
        """
        # Herald
        self._herald = None
        self._directory = None

        # Herald messages filters
        self._filters = []

        # Pelix Remote Services
        self._dispatcher = None
        self._registry = None

        # private attributes
        self._known_peers = set()

    def _dump_endpoint(self, endpoint):
        """
        Converts an ExportEndpoint bean to a dictionary.

        :param endpoint: An ExportEndpoint bean
        :return: A dictionary
        """
        dump = {key: getattr(endpoint, key)
                for key in ("uid", "configurations", "name", "specifications")}

        # Send import-side properties
        dump['properties'] = endpoint.make_import_properties()
        dump['peer'] = self._directory.local_uid
        return dump

    def _dump_endpoints(self, endpoints):
        """
        Converts a list of ExportEndpoint beans to a list of dictionaries

        :param endpoints: A list of endpoints
        :return: A list of dictionaries
        """
        return [self._dump_endpoint(endpoint) for endpoint in endpoints]

    def _load_endpoint(self, endpoint_dict):
        """
        Make an ImportEndpoint bean from the result of a call to
        _dump_endpoint()

        :param endpoint_dict: The result of a call to _dump_endpoint(),
                              sent over Herald
        :return: An ImportEndpoint bean
        :raise KeyError: Incomplete dump
        """
        # print("+"*25+endpoint_dict+"+"*25)
        # print(type(endpoint_dict))
        return pelix.remote.beans.ImportEndpoint(
            endpoint_dict['uid'],
            endpoint_dict['peer'],
            endpoint_dict['configurations'],
            endpoint_dict['name'],
            endpoint_dict['specifications'],
            endpoint_dict['properties'])

    def __subject(self, kind):
        """
        Prepares a subject for Herald discovery

        :param kind: Kind of discovery message
        :return: A subject string that can be handled by Herald Discovery
        """
        return '/'.join(('herald', 'rpc', 'discovery', kind))

    def __send_message(self, kind, content, group='all'):
        """
        Fires a discovery message to all peers

        :param kind: Kind of discovery message
        :param content: Content of the message
        :param group: group to send the message (default: all)
        """
        msg = beans.Message(self.__subject(kind), content)
        # add the original sender
        msg.add_header('original_sender', self._directory.local_uid)
        self._herald.fire_group(group, msg)

    def __register_endpoints(self, peer_uid, endpoints_dicts):
        """
        Registers a list of endpoints

        :param peer_uid: UID of the peer providing the services
        :param endpoints_dicts: A list of endpoint description dictionaries
        """
        for endpoint_dict in endpoints_dicts:
            try:
                endpoint = self._load_endpoint(endpoint_dict)
                self._registry.add(endpoint)
            except KeyError as ex:
                _logger.error("Unreadable endpoint from %s: missing %s",
                              peer_uid, ex)

    @staticmethod
    def _original_sender(message):
        """
        Returns the original sender of the message
        :param message:
        :return:
        """
        origin = message.get_header('original_sender')
        if origin is not None:
            return origin
        return None

    def herald_message(self, herald_svc, message):
        """
        An Herald message has been received
        """
        kind = message.subject.rsplit('/', 1)[1]
        if kind == 'contact':
            # First contact
            # Check if we know the sending peer
            # # (peer discovery process)

            sender = self._original_sender(message)
            if sender is None:
                print('INFO: discovery/herald_message: \
                    original_sender=None, setting to {}'.format(message.sender))
                sender = message.sender

            if sender in self._known_peers:
                # In this case, we have already seen this message
                # so it will not do anything with this message
                print("INFO: already known peer: {}".format(sender))
                return
            # note that we have seen the sender
            self._known_peers.add(sender)

            # Register the new endpoints
            self.__register_endpoints(message.sender, message.content)

            # Reply with the whole list of our exported endpoints
            endpoints = self._dump_endpoints(self._dispatcher.get_endpoints())
            # print("SENDER: ".format(message.sender))
            if message.sender is not None:
                herald_svc.reply(message, endpoints, self.__subject("add"))

        # elif kind == 'add' and message.sender in self._directory:
        elif kind == 'add':
            # New endpoint available on a known peer
            # => Register the new endpoints
            if isinstance(message.content, str):
                message.set_content(eval(message.content))
            self.__register_endpoints(message.sender, message.content)
        elif kind == 'remove':
            # The message only contains the UID of the endpoint
            self._registry.remove(message.content['uid'])
        elif kind == 'update':
            # Update the endpoint
            endpoint_uid = message.content['uid']
            new_properties = message.content['properties']
            self._registry.update(endpoint_uid, new_properties)
        else:
            _logger.debug("Unknown kind of discovery event: %s", kind)

    def peer_registered(self, peer, group='all'):
        """
        A new peer has been registered in Herald: send it a contact information

        :param peer: The new peer
        :param group: inform the destination to broadcast the message if it
            is a router in the group 'group'
        """
        # Send a contact message, with our list of endpoints
        endpoints = self._dump_endpoints(self._dispatcher.get_endpoints())
        msg = beans.Message(self.__subject('contact'), endpoints)
        msg.add_header('group', group)
        msg.add_header('original_sender', self._directory.local_uid)
        self._herald.fire(peer, msg)

    def peer_updated(self, peer, access_id, data, previous):
        """
        An access to a peer have been updated: ignore
        """
        pass

    def peer_unregistered(self, peer):
        """
        All accesses to a peer have been lost: forget about it

        :param peer: The lost peer
        """
        self._registry.lost_framework(peer.uid)

    def endpoints_added(self, endpoints):
        """
        Multiple endpoints have been created

        :param endpoints: A list of ExportEndpoint beans
        """
        self.__send_message('add', self._dump_endpoints(endpoints))

    def endpoint_updated(self, endpoint, _):
        """
        An endpoint has been updated

        :param endpoint: An updated ExportEndpoint bean
        :param _: Previous value of the endpoint properties
        """
        self.__send_message('update',
                            {"uid": endpoint.uid,
                             "properties": endpoint.make_import_properties()})

    def endpoint_removed(self, endpoint):
        """
        An endpoint has been removed
        """
        self.__send_message('remove', {"uid": endpoint.uid})
