from ipopo import ComponentFactory, Provides, \
    Validate, Invalidate, Instantiate, Property

import pyb

# pins declarations
photo_pin = 'X12'
led_pin = 'X11'


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


@ComponentFactory('led-pyboard-factory')
@Property('_name', 'led.name', 'pyboard led')
@Provides('pyboard.led.ledService')
@Instantiate('led.services.ledService')
class Led:

    def __init__(self):
        self._state = False

    @Validate
    def start(self):
        self.on()

    @Invalidate
    def stop(self):
        self.off()

    def get_name(self):
        return self.get_name

    def get_state(self):
        return self._state

    def on(self):
        print("LED SET TO ON")
        self._state = True
        set_led(self._state)

    def off(self):
        print("LED SET TO OFF")
        self._state = False
        set_led(self._state)

    def toggle(self):
        print('LED TOGGLING')
        if self._state:
            self.off()
        else:
            self.on()
