#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Herald HTTP transport implementation

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

import ujson as json

import herald

def json_converter(obj):
    """
    Converts sets to list during JSON serialization
    """
    if isinstance(obj, (set, frozenset)):
        return tuple(obj)

    raise TypeError

def to_json(msg):
    """
    Returns a JSON string representation of this message
    """
    result = {}

    # headers
    result[herald.MESSAGE_HEADERS] = {}        
    if msg.headers is not None:
        for key in msg.headers:
            result[herald.MESSAGE_HEADERS][key] = msg.headers.get(key) or None        
    
    # subject
    result[herald.MESSAGE_SUBJECT] = msg.subject
    # content
    if msg.content is not None:
        if isinstance(msg.content, str):
            # string content
            result[herald.MESSAGE_CONTENT] = msg.content
        else:
            result[herald.MESSAGE_CONTENT] = 'ERROR extracting content'
    
    # metadata
    result[herald.MESSAGE_METADATA] = {}        
    if msg.metadata is not None:
        for key in msg.metadata:
            result[herald.MESSAGE_METADATA][key] = msg.metadata.get(key) or None
            
    return json.dumps(result, default=herald.utils.json_converter)


def from_json(json_string):
    """
    Returns a new MessageReceived from the provided json_string string
    """
    # parse the provided json_message
    try:            
        parsed_msg = json.loads(json_string)            
    except ValueError as ex:            
        # if the provided json_message is not a valid JSON
        return None
    except TypeError as ex:
        # if json_message not string or buffer
        return None
    herald_version = None
    # check if it is a valid Herald JSON message
    if herald.MESSAGE_HEADERS in parsed_msg:
        if herald.MESSAGE_HERALD_VERSION in parsed_msg[herald.MESSAGE_HEADERS]:
            herald_version = parsed_msg[herald.MESSAGE_HEADERS].get(herald.MESSAGE_HERALD_VERSION)                         
    if herald_version is None or herald_version != herald.HERALD_SPECIFICATION_VERSION:
        print("Herald specification of the received message is not supported!")
        return None   
    # construct new Message object from the provided JSON object    
    msg = herald.beans.MessageReceived(uid=(parsed_msg[herald.MESSAGE_HEADERS].get(herald.MESSAGE_HEADER_UID) or None), 
                          subject=parsed_msg[herald.MESSAGE_SUBJECT], 
                          content=None, 
                          sender_uid=(parsed_msg[herald.MESSAGE_HEADERS].get(herald.MESSAGE_HEADER_SENDER_UID) or None), 
                          reply_to=(parsed_msg[herald.MESSAGE_HEADERS].get(herald.MESSAGE_HEADER_REPLIES_TO) or None), 
                          access=None,
                          timestamp=(parsed_msg[herald.MESSAGE_HEADERS].get(herald.MESSAGE_HEADER_TIMESTAMP) or None) 
                          )                           
    # set content
    try:
        if herald.MESSAGE_CONTENT in parsed_msg:
            parsed_content = parsed_msg[herald.MESSAGE_CONTENT]                              
            if parsed_content is not None:
                if isinstance(parsed_content, str):
                    msg.set_content(parsed_content)
                else:
                    print('error')
                    raise Exception('internal error')
    except KeyError as ex:
        print('internal error 2')
    # other headers
    if herald.MESSAGE_HEADERS in parsed_msg:
        for key in parsed_msg[herald.MESSAGE_HEADERS]:
            if key not in msg._headers:
                msg._headers[key] = parsed_msg[herald.MESSAGE_HEADERS][key]         
    # metadata
    if herald.MESSAGE_METADATA in parsed_msg:
        for key in parsed_msg[herald.MESSAGE_METADATA]:
            if key not in msg._metadata:
                msg._metadata[key] = parsed_msg[herald.MESSAGE_METADATA][key] 
                       
    return msg