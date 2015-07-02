"""
Main application on PyBoard

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

# automata import
import automata
from utils import to_json, from_json

# pins declarations
photo_pin = 'X12'
led_pin = 'X11'

# constants declaration
HELLO_MESSAGE = b'[[[HELLO]]]'
DELIMITER = ':'

# bluetooth connection initialization
uart = pyb.UART(1, 38400)


def set_led(value):
    """
    set the led to a given value
    :param value: True for ON, False for OFF
    :return: None
    """
    if value:
        pyb.Pin(led_pin, pyb.Pin.OUT_PP).high()
    else:
        pyb.Pin(led_pin, pyb.Pin.OUT_PP).low()


def get_photo_value():
    """
    :return: photoresistor value as a string
    """
    return str(pyb.ADC(photo_pin).read())


def to_string(msg):
    """
    Take a str and returns the same object
    or take a bytes object and transform it
    to a string object (useful for comparisons)
    :param msg: message to transform to a string
    :return: resulted string
    """
    if type(msg) is bytes:
        msg = str(msg)
        msg = msg[2:]
        return msg[:-1]
    else:
        return msg


def put_message(msg):
    """
    put a bluetooth message to the peer.
    It adds correct delimiters
    :param msg: string message
    :return: None
    """
    msg = to_string(msg)
    print("sending:")
    print(str(len(msg))+DELIMITER+msg)
    uart.write(str(len(msg))+DELIMITER+msg)


def get_message():
    """
    :return: a string containing a new message
    or None if any messages arrived.
    """
    if not uart.any():
        return
    msg = uart.read()
    # print('incoming:')
    # print(msg)
    automata.read(to_string(msg))
    if not automata.any_message():
        return
    msg = automata.get_message()
    print("received:")
    print(msg)
    if to_string(msg) == to_string(HELLO_MESSAGE):
        put_message(HELLO_MESSAGE)
    else:
        return msg


def display_message(bean):
    """
    Displays message in bean
    :param bean: bean to display
    :return: Nothing
    """
    print('='*20)
    print('subject:'+bean.subject)
    print('sender:'+bean.sender)
    print('-'*20)
    if bean.content is not None:
        print('content:'+bean.content)
    print('='*20)


def manage_message(msg, uid):
    """
    Extract useful information in the message
    and do something if necessary
    :param msg: message got
    :param uid: node uid for the pyboard
    :return: Nothing
    """
    print('herald message received in {}:'.format(uid))
    # bean is of type MessageReceived
    bean = from_json(msg)
    display_message(bean)
    if bean.subject == 'herald/directory/discovery/step1':
        print('** SENDING STEP 2 MESSAGE **')

# ---------- MAIN LOOP ------------

automata = automata.SerialAutomata()


def gen_node_uid():
    """
    :return: string representing the node UID of the pyboard
    Format like "f07569ba-77ab-4f01-a041-c86c6b58c3cd"
    """

    def gen_rand_hexa():
        return hex(pyb.rng() % 16)[2:]

    res = ''
    for i in range(0, 8):
        res += gen_rand_hexa()
    res += '-'
    for j in range(0,3):
        for i in range(0, 4):
            res += gen_rand_hexa()
        res += '-'
    for i in range(0, 12):
        res += gen_rand_hexa()
    return res

uid = gen_node_uid()

while True:
    msg = get_message()
    if msg:
        manage_message(msg, uid)
