from ipopo import ComponentFactory, Provides, Requires, \
    Validate, Invalidate, Instantiate, Property, print_ipopo_state, \
    RemoteObject, ipopo_exported, service_rpc_string, call_service, \
    service_name_from_id

import ipopo
from xmlrpc import *

@ComponentFactory('led-pyboard-factory')
@Property('_name', 'led.name', 'pyboard led')
@Provides('pyboard.led.ledService')
@Provides('pyboard.led.ledService2')
@Instantiate('led.services.ledService')
class Led:

    def __init__(self):
        self._state = None
        self._name = None

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

    def off(self):
        print("LED SET TO OFF")
        self._state = False

    def run(self):
        print('LED RUNNING')


@ComponentFactory('generic_sensor')
@Property('_id', 'sensor.id', '[TODO] NODE UUID')
@Provides('pyboard.testRequire')
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
        print('SENSOR RUNNING')


if __name__ == '__main__':
    # # shows the internal state of micro-iPOPO
    # # and checks if the components are correctly declared with
    # # the correct properties
    # print_ipopo_state()
    # print('exported: {}'.format(ipopo_exported()))
    #
    # # shows that the remote object call a special method when
    # # a method is called.
    # # We can get arguments as well
    # rem = RemoteObject()
    # rem.foo()
    # rem.foo2('bar')
    # rem.foo3('bar', test='hello', answer=42)
    #
    # # trace of step3 answer
    # print('STEP 3 ANSWER')
    # res = []
    # for service in ipopo_exported():
    #     service_name = service_name_from_id(service)
    #     res.append(service_rpc_string(service_name, '[TODO UID]'))
    # content = str(res)
    # print(content)
    #
    # # rpc call for led on
    # on_message = """
    #     <?xml version='1.0'?>
    #     <methodCall>
    #         <methodName>service_0.on</methodName>
    #         <params>
    #         </params>
    #     </methodCall>
    # """
    # call_service(*extract_request_info(on_message))

    # test ipopo state
    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    # test if properties can be accessed
    print('{}  ---- if it is "pyboard led", ok'.format(ipopo._class_binding['led.services.ledService']._name))

    # adding a service
    print('trying injecting a service required:')
    ipopo.add_service('store.services.storeService', 'DISTANT PEER', 'service_42')

    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    ipopo.component_execution()

    # trying to access to the imported field
    ipopo._class_binding['sensor.services.sensorService']._store.store(42)

    # removing added service
    ipopo.remove_service('store.services.storeService', 'DISTANT PEER')

    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    ipopo.component_execution()

