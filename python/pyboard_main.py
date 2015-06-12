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
import pyboard_automata

# pins declarations
photo_pin = 'X12'
led_pin = 'X11'
HELLO_MESSAGE = b'[[[HELLO]]]'
SEPARATOR = b'|||'

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

def put_message(msg):
    uart.write(msg+SEPARATOR)

def get_message():
    if not uart.any():
        return
    msg = uart.read()
    automata.read(msg)
    if not automata.any_message():
        return
    msg = automata.get_message()
    if msg == HELLO_MESSAGE:
        put_message(HELLO_MESSAGE)
    else:
        return msg



automata = pyboard_automata.SerialAutomata(SEPARATOR)
while True:
    #  send_photo()
    print(get_message())
    pyb.delay(200)