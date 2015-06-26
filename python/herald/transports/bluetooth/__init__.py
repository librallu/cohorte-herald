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

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------

CONTENT_TYPE_JSON = "application/json"
""" MIME type: JSON data """

# ------------------------------------------------------------------------------

ACCESS_ID = "bluetooth"
"""
Access ID used by the Bluetooth transport implementation
"""

# ------------------------------------------------------------------------------

SERVICE_BLUETOOTH_DIRECTORY = "herald.bluetooth.directory"
"""
Specification of the Bluetooth transport directory
"""

SERVICE_BLUETOOTH_RECEIVER = "herald.bluetooth.receiver"
"""
Specification of the Bluetooth transport servlet (reception side)
"""

SERVICE_BLUETOOTH_TRANSPORT = "herald.bluetooth.transport"
"""
Specification of the Bluetooth transport implementation (sending side)
"""

BLUETOOTH_DISCOVERY_SERVICE = "herald.transports.bluetooth.discovery"
"""
Service discovery for bluetooth
"""