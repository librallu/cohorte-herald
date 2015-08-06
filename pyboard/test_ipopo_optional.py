from ipopo import ComponentFactory, Provides, Requires, \
    Validate, Invalidate, Instantiate, Property, print_ipopo_state, \
    RemoteObject, ipopo_exported, service_rpc_string, call_service, \
    service_name_from_id, BindField, UnbindField

import ipopo
from xmlrpc import *



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
    print_ipopo_state()
    print('exported: {}'.format(ipopo_exported()))

    ipopo.component_execution()

    print('trying injecting a service required:')
    ipopo.add_service('service.test', 'DISTANT PEER')

    ipopo.component_execution()

    print('suppress the service required:')
    ipopo.remove_service('service.test', 'DISTANT PEER')

    ipopo.component_execution()
