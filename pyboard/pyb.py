# mock module to allow pyb methods in pycharm


class UART:
    def __init__(self, a, b):
        pass

    def any(self):
        pass

    def read(self):
        pass

    def write(self, a):
        pass


class Pin:
    def __init__(self, a, b):
        pass

    def high(self):
        pass

    def low(self):
        pass

    @property
    def OUT_PP(self):
        pass


class ADC:
    def __init__(self, a):
        pass

    def read(self):
        pass


def rng():
    return 42