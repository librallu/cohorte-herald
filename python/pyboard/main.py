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

# pins declarations
photo_pin = 'X12'
led_pin = 'X11'
HELLO_MESSAGE = b'[[[HELLO]]]'
DELIMITER = ':'

# bluetooth connection initialization
uart = pyb.UART(1, 38400)


# def send_photo():
#     uart.write(str(pyb.ADC(photo_pin).read()))
#     uart.write("\n")
#
#
# def get_message():
#     if not uart.any():
#         return
#     msg = uart.read()
#     print(msg)
#     if msg.upper() == b"ON":
#         pyb.Pin(led_pin, pyb.Pin.OUT_PP).high()
#         print("LED ON")
#     elif msg.upper() == b"OFF":
#         pyb.Pin(led_pin, pyb.Pin.OUT_PP).low()
#         print("LED OFF")

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
    if type(msg) is bytes:
        msg = str(msg)
        msg = msg[2:]
        return msg[:-1]
    else:
        return msg

def put_message(msg):
    msg = to_string(msg)
    print("sending:")
    print(str(len(msg))+DELIMITER+msg)
    uart.write(str(len(msg))+DELIMITER+msg)

def get_message():
    if not uart.any():
        return
    msg = uart.read()
    print('incoming:')
    print(msg)
    automata.read(to_string(msg))
    if not automata.any_message():
        return
    msg = automata.get_message()
    print("automata ok:")
    print(msg)
    if to_string(msg) == to_string(HELLO_MESSAGE):
        put_message(HELLO_MESSAGE)
    else:
        return msg

automata = automata.SerialAutomata()

while True:
    #  send_photo()
    get_message()
    #  pyb.delay(200)
