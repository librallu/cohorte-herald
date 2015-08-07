from ipopo import ComponentFactory, Provides, Requires, \
    Validate, Invalidate, Instantiate, Property, print_ipopo_state, \
    RemoteObject, ipopo_exported, service_rpc_string, call_service, \
    service_name_from_id, BindField, UnbindField, init_ipopo

import ipopo
from xmlrpc import *
import serial_herald_message


@ComponentFactory('test-factory')
@Requires('_service', 'service.test', optional=True)
@Instantiate('test')
class Test:

    def __init__(self):
        self._service = None

    @Validate
    def start(self):
        print('=== TEST STARTED === ')

    @Invalidate
    def stop(self):
        print('=== TEST STOPPED ===')

    def run(self):
        print('=== TEST RUNNING with service {} ==='.format(self._service))
        if self._service:
            self._service.store(42)
        else:
            print('*'*5 + ' NO SERVICE AVAILABLE')

    @BindField('_service')
    def bind_service(self):
        print('=== SERVICE BOUND ===')

    @UnbindField('_service')
    def unbind_service(self):
        print('=== SERVICE UNBOUND ===')

if __name__ == '__main__':

    def wait_for_message(msg):

        return serial_herald_message.SerialHeraldMessage(
            subject='herald/rpc/xmlrpc',
            sender_uid='DISTANT PEER',
            original_sender='DISTANT PEER',
            final_destination='LOCAL PEER',
            content = """
                    <?xml version='1.0'?>
                        <methodResponse>
                        <params>
                            <param>
                                <value><int>78</int></value>
                            </param>
                            <param>
                                <value><string>hello world !</string></value>
                            </param>
                        </params>
                    </methodResponse>"""
        )

    init_ipopo(wait_for_message, lambda a, b, c: None)
    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    ipopo.component_execution()

    print('trying injecting a service required:')
    ipopo.add_service('service.test', 'DISTANT PEER', 'service_42')

    ipopo.component_execution()

    print('suppress the service required:')
    ipopo.remove_service('service.test', 'DISTANT PEER')

    ipopo.component_execution()
