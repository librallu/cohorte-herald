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
    """
    Led manipulator.

    provides:
        - pyboard.led.ledService

    properties:
        - led.name

    """

    def __init__(self):
        self._state = False

    @Validate
    def start(self):
        """
        validate function: switch on the led.
        """
        self.on()

    @Invalidate
    def stop(self):
        """
        invalidate function: switch off the led
        """
        self.off()

    def get_name(self):
        """
        :return: name property
        """
        return self.get_name

    def get_state(self):
        """
        :return: return led state (True if on, False if off)
        """
        return self._state

    def on(self):
        """
        switch on the led
        """
        print("LED SET TO ON")
        self._state = True
        set_led(self._state)

    def off(self):
        """
        switch off the led
        """
        print("LED SET TO OFF")
        self._state = False
        set_led(self._state)

    def toggle(self):
        """
        switch off the led if it is on
        and switch it on if it is off
        """
        print('LED TOGGLING')
        if self._state:
            self.off()
        else:
            self.on()