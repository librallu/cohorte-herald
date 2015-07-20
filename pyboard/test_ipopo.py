from ipopo import ComponentFactory, Provides, Requires, \
    Validate, Invalidate, Instantiate, Property, print_ipopo_state, \
    RemoteObject, ipopo_exported


@ComponentFactory('led-pyboard-factory')
@Property('_name', 'led.name', 'pyboard led')
@Provides('pyboard.led.ledService')
@Instantiate('led.services.ledService')
class Led:

    def __init__(self):
        self._state = None

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
        self._state = True

    def off(self):
        self._state = False


@ComponentFactory('generic_sensor')
@Property('_id', 'sensor.id', '[TODO] NODE UUID')
@Requires('_store', 'store.services.storeService')
@Instantiate('sensor.services.sensorService')
class Sensor:

    def __init__(self):
        pass

    @Validate
    def start(self):
        print('linked with storage')

    @Invalidate
    def stop(self):
        print('unlinked with storage')

    def run(self):
        pass


if __name__ == '__main__':
    # shows the internal state of micro-iPOPO
    # and checks if the components are correctly declared with
    # the correct properties
    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    # shows that the remote object call a special method when
    # a method is called.
    # We can get arguments as well
    rem = RemoteObject()
    rem.foo()
    rem.foo2('bar')
    rem.foo3('bar', test='hello', answer=42)
