#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald core beans definition

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

# Standard library
import time

# import herald module to use constants
import herald

import pyb

# ------------------------------------------------------------------------------

def gen_uuid():
    """
    :return uuid of a message 32 random hexadecimal chars
    """
    res = ''
    for i in range(0,32):
        res += hex(pyb.rng() % 16)[2:].upper()
    return res

class Message(object):
    """
    Represents a message to be sent
    """
    def __init__(self, subject, content=None):

        self._subject = subject
        self._content = content
        
        self._headers = {}
        self._headers[herald.MESSAGE_HERALD_VERSION] = herald.HERALD_SPECIFICATION_VERSION
        self._headers[herald.MESSAGE_HEADER_TIMESTAMP] = int(time.time() * 1000) 
        self._headers[herald.MESSAGE_HEADER_UID] = gen_uuid()
        
        self._metadata = {}  

    def __str__(self):
        return "{0} ({1})".format(self._subject, self.uid)

    @property
    def subject(self):
        return self._subject

    @property
    def content(self):
        return self._content

    @property
    def timestamp(self):
        return self._headers[herald.MESSAGE_HEADER_TIMESTAMP]

    @property
    def uid(self):
        return self._headers[herald.MESSAGE_HEADER_UID]

    @property
    def headers(self):
        return self._headers
    
    @property    
    def metadata(self):
        return self._metadata

    def add_header(self, key, value):
        self._headers[key] = value
        
    def get_header(self, key):
        if key in self._headers:
            return self._headers[key]       
        return None

    def remove_header(self, key):
        if key in self._headers:
            del self._headers[key]

    def set_content(self, content):
        self._content = content
        
    def add_metadata(self, key, value):
        self._metadata[key] = value
        
    def get_metadata(self, key):
        if key in self._metadata:
            return self._metadata[key]
        return None
        
    def remove_metadata(self, key):
        if key in self._metadata:
            del self._metadata[key]
            
            
class MessageReceived(Message):

    def __init__(self, uid, subject, content, sender_uid, reply_to, access,
                 timestamp=None, extra=None):
        Message.__init__(self, subject, content)
        self._headers[herald.MESSAGE_HEADER_UID] = uid
        self._headers[herald.MESSAGE_HEADER_SENDER_UID] = sender_uid
        self._headers[herald.MESSAGE_HEADER_REPLIES_TO] = reply_to
        self._access = access
        self._extra = extra
        self._headers[herald.MESSAGE_HEADER_TIMESTAMP] = timestamp

    def __str__(self):
        return "{0} ({1}) from {2}".format(self._subject, self.uid,
                                           self.sender)

    def set_sender(self, sender):
        self._headers[herald.MESSAGE_HEADER_SENDER_UID] = sender

    @property
    def access(self):
        return self._access

    @property
    def reply_to(self):
        return self._headers[herald.MESSAGE_HEADER_REPLIES_TO]

    @property
    def sender(self):
        return self._headers[herald.MESSAGE_HEADER_SENDER_UID]

    @property
    def extra(self):
        return self._extra

    def set_access(self, access):
        self._access = access
        
    def set_extra(self, extra):
        self._extra = extra