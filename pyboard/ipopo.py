import pyb  # for randomness
import xmlrpc
from herald import wait_for_message, fire_content_to
# def wait_for_message(msg):
#     return """
#     <?xml version='1.0'?>
#         <methodResponse>
#         <params>
#             <param>
#                 <value><int>78</int></value>
#             </param>
#             <param>
#                 <value><string>hello world !</string></value>
#             </param>
#         </params>
#     </methodResponse>"""

"""
A component can have following decorators :

- componentFactory : indicates the name of the component
- validate method : called when the component is valid
- invalidate method : called when the component is invalid
- BindField : called when a field is bound (used when a component have a require optional)
- UnbindField : called when a field is unbound (used when a component have a require optional)
- provides : provides a service
- requires : requires a service for being validated
- property : defines a property for the service

Components are represented by classes with methods in it.

Services are represented by strings.

"""

# ===== GLOBAL VARIABLES =====

# services provided in the application
# external service name -> Peer UUID list
_external_services = {}

# component name -> class
_class_binding = {}

# temporary variable for exploring components
_ipopo_explorer = {}

_component_info = {}

_id_counter = 0

_internal_services = {}

# service name -> service provider -> service spec
_service_name_spec = {}


def get_name(input_class):
    """
    return component name from a python class

    :param input_class: python class
    :return: component name
    """
    try:
        return input_class.ipopo_component_name
    except AttributeError:
        raise Exception('ERROR inspecting component : \
        Are you sure that you used the decorator @Instantiate when declaring your component ?')


def get_external_service_uuid(name):
    """
    get an external service provider for name

    :param name: service name
    :return: peer uuid providing the service, None elsewhere
    """
    if name in _external_services:
        return _external_services[name][0]
    else:
        return None


def get_provided_services():
    res = []
    for name in _component_info:
        if _component_info[name]['active']:
            for i in _component_info[name]['provides']:
                res.append(service_name_from_id(i))
    return res

def get_best_service_provider(name):
    """
    return the best service provider for a service name

    :param name: service name
    :return: best service provider uuid

        - 'local' if provided in local
        - UUID string if external service
        - None if there is no known service provider
    """
    if name in get_provided_services():
        return 'local'
    else:
        return get_external_service_uuid(name)


def add_service_name_binding(svc, provider, name):
    """
    adds in ipopo service name binding

    :param svc: specification
    :param provider: service provider
    :param name: service name
    """
    if provider not in _service_name_spec:
        _service_name_spec[provider] = {}
    _service_name_spec[provider][svc] = name


def get_service_name_binding(svc, provider):
    """
    return name for service provided by provider.

    :param svc: specification
    :param provider: service provider
    :return: service name None if any
    """
    if provider not in _service_name_spec:
        return None
    if svc not in _service_name_spec[provider]:
        return None
    return _service_name_spec[provider][svc]


def add_service(service, provider, name):
    """
    adds a service provided by an external peer

    :param service: service provided
    :param provider: service provider
    :param name: service name
    :return: True if added, False if it already exists
    """
    if service in _external_services:
        if provider not in _external_services[service]:
            _external_services[service].append(provider)
        else:
            return False
    else:
        _external_services[service] = [provider]

    add_service_name_binding(service, provider, name)

    # in this case check if some components can start or bind services
    for name in _component_info:
            for req in _component_info[name]['requires']:
                if req[1] == service:
                    if not _component_info[name]['active']:
                        print('add_service leads to a component starting test {}'.format(name))
                        start_component(name)
                    else:
                        if not getattr(_class_binding[name], req[0]):
                            print('add_service leads to bind a field: {} in {}'.format(req[0], name))
                            # make the binding
                            setattr(_class_binding[name], req[0], RemoteObject(provider, name))
                            # call the bind field if exists
                            if req[0] in _component_info[name]['bind_field']:
                                print('in {}, field {} bound'.format(name, req[0]))
                                method = _component_info[name]['bind_field'][req[0]]
                                method(_class_binding[name])
    return True


def remove_component(name):
    """
    remove component from app

    :param name: component name
    """
    before = get_provided_services()

    _component_info[name]['active'] = False

    # call invalidate
    _component_info[name]['invalidate'](_class_binding[name])

    after = get_provided_services()

    # TODO check if provided services need to be stopped
    # if before != after, some services are stopped.
    # So we need to check if it invalidate other internal components
    # and send a message through the network to inform peers


def remove_service(service, provider):
    """
    removes a service provided by an external peer

    :param service: service provided
    :param provider: service provider
    :return: True if deleted, False if it doesn't exist
    """
    if service not in _external_services:
        return False
    if provider not in _external_services[service]:
        return False
    _external_services[service].remove(provider)

    # in this case, check if some components must stop
    for name in _component_info:
        if _component_info[name]['active']:
            for req in _component_info[name]['requires']:
                if req[1] == service:
                    if req[2]:  # if require optional
                        # TODO add check if it is possible to change the bound field with an other
                        # TODO service
                        print('remove_service leads to a unbind field')
                        setattr(_class_binding[name], req[0], None)
                        method = _component_info[name]['unbind_field'][req[0]]
                        method(_class_binding[name])
                    else:
                        print('remove_service leads to a component stop {}'.format(name))
                        remove_component(name)

    return True


def start_component(name):
    """
    starts the component with name name if possible.

    :param name: name of the component
    :return: True if the component is started, False elsewhere

    """
    # For each require in the component info
    for require in _component_info[name]['requires']:
        # if the require is not optional
        if not require[2]:
            # if the require is not satisfied
            # stop the process because some requires are missing
            if not get_best_service_provider(require[1]):
                return False

    _component_info[name]['active'] = True

    # add properties to the component
    for prop in _component_info[name]['property']:
        # _class_binding[name].prop[0] = prop[2]
        setattr(_class_binding[name], prop[0], prop[2])

    # add required fields if needed
    for req in _component_info[name]['requires']:
        service_provider = get_best_service_provider(req[1])
        if not service_provider:
            setattr(_class_binding[name], req[0], None)
        else:
            svc_name = get_service_name_binding(req[1], service_provider)
            setattr(_class_binding[name], req[0], RemoteObject(service_provider, svc_name))

    # call validate
    _component_info[name]['validate'](_class_binding[name])

    print('component {} started'.format(name))
    return True


# ===== DECORATORS =====


def ComponentFactory(factory_name):
    """
    adds a field _ipopo_factory_name with name in the component.

    :param factory_name: name of the factory

    """
    def class_builder(original_class):
        # print('componentFactory call {}'.format(_ipopo_explorer))
        new_class = original_class
        name = get_name(new_class)

        # create fields in component info
        _component_info[name]['factory'] = factory_name

        # rebinds class with name
        _class_binding[name] = new_class()

        # finds validate and invalidate decorators
        # fields = [getattr(new_class, method) for method in dir(new_class)
        #           if callable(getattr(new_class, method))]
        # for field in fields:
        #     if 'ipopo_kind' in dir(field):
        #         if field.ipopo_kind == 'validate':
        #             _component_info[name]['validate'] = field
        #         elif field.ipopo_kind == 'invalidate':
        #             _component_info[name]['invalidate'] = field
        _component_info[name]['validate'] = _ipopo_explorer.get('validate', None)
        _component_info[name]['invalidate'] = _ipopo_explorer.get('invalidate', None)
        _component_info[name]['bind_field'] = _ipopo_explorer.get('bind_field', {})
        _component_info[name]['unbind_field'] = _ipopo_explorer.get('unbind_field', {})

        start_component(name)

        return new_class
    return class_builder


def Instantiate(name):
    """
    instantiate component as name

    :param name: name of component

    """
    def class_builder(original_class):
        new_class = original_class
        # add factory_name in new_class
        new_class.ipopo_component_name = name

        # create fields in component info
        _component_info[name] = {}
        _component_info[name]['provides'] = set()
        _component_info[name]['requires'] = set()
        _component_info[name]['property'] = set()
        _component_info[name]['factory'] = name+'_factory'
        _component_info[name]['validate'] = None
        _component_info[name]['invalidate'] = None
        _component_info[name]['bind_field'] = {}
        _component_info[name]['unbind_field'] = {}
        _component_info[name]['active'] = False

        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Validate(function):
    """
    Decorator that Tells the function is the component validate function

    :param function: input function

    """
    _ipopo_explorer['validate'] = function
    return function


def Invalidate(function):
    """
    Decorator that Tells the function is the component invalidate function

    :param function: input function

    """
    _ipopo_explorer['invalidate'] = function
    return function


def BindField(require_var):
    """
    Decorator that Tells the function is the bindField Function

    :param require_var: variable name of field injected
    """
    def decorator(function):
        if 'bind_field' not in _ipopo_explorer:
            _ipopo_explorer['bind_field'] = {require_var: function}
        else:
            _ipopo_explorer['bind_field'][require_var] = function
        return function
    return decorator


def UnbindField(require_var):
    """
    Decorator that Tells the function is the unbindField Function

    :param require_var: variable name of field injected
    """
    def decorator(function):
        if 'unbind_field' not in _ipopo_explorer:
            _ipopo_explorer['unbind_field'] = {require_var: function}
        else:
            _ipopo_explorer['unbind_field'][require_var] = function
        return function
    return decorator


def Provides(service):
    """
    adds field _ipopo_internal_services with a set of services
    provided.

    :param service: Service to provide

    """
    def class_builder(original_class):
        global _id_counter
        new_class = original_class
        name = get_name(new_class)

        # add service to component info
        _component_info[name]['provides'].add(_id_counter)

        _internal_services[service] = _id_counter
        if '_ipopo_provides' in dir(new_class):
            new_class._ipopo_provides.add(_id_counter)
        else:
            new_class._ipopo_provides = set([service])
        _id_counter += 1

        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Requires(variable_name, service_name, optional=False):
    """
    Tells that the component requires other services to run

    :param variable_name: variable to be injected
    :param service_name: name of the service
    :param optional: if True, component don't need service

    """
    def class_builder(original_class):
        new_class = original_class
        name = get_name(new_class)

        _component_info[name]['requires'].add((variable_name, service_name, optional))
        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Property(variable, prop_name, value):
    """
    Tells that the component have the property

    :param variable: variable name
    :param prop_name: property name
    :param value: initial value of the variable

    """
    def class_builder(original_class):
        new_class = original_class
        name = get_name(new_class)

        _component_info[name]['property'].add((variable, prop_name, value))
        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def service_name_from_id(id):
    """
    return the service name from it's id

    :param id: service id
    :return: service name
    """
    for i in _internal_services:
        if _internal_services[i] == id:
            return i
    return None


def print_ipopo_state():
    """
    For debug use only: print local variables information
    """
    print('='*30)
    print('external_services: {}'.format(_external_services))
    print('internal_services:')
    for i in _internal_services:
        print('\t{}->{}'.format(i, _internal_services[i]))
    print('~'*10)
    for name in _class_binding:
        component = _class_binding[name]
        print('{} ({}):'.format(component.ipopo_component_name, _component_info[name]['factory']))
        print('\t- provides {}'.format(_component_info[name]['provides']))
        print('\t- requires {}'.format(_component_info[name]['requires']))
        print('\t- property {}'.format(_component_info[name]['property']))
        print('\t- validate:{}'.format(_component_info[name]['validate']))
        print('\t- invalidate:{}'.format(_component_info[name]['invalidate']))
        print('\t- bind:{}'.format(_component_info[name]['bind_field']))
        print('\t- unbind:{}'.format(_component_info[name]['unbind_field']))
        print('\t- active:{}'.format(_component_info[name]['active']))
    print('-'*30)


def is_component_can_start(component):
    """
    :param component:
    :return: True if component can start, false elsewhere
    """
    services_required = _component_info[component]['requires']
    for i in services_required:
        if not get_best_service_provider(i):
            return False
    return True

def is_component_active(component):
    """
    :param component:
    :return: true if component is active
    """
    return _component_info[component]['active']

def ipopo_exported():
    """
    :return: list of exported services
    """
    res = []
    for name in _class_binding:
        if is_component_active(name):
            res.extend(_component_info[name]['provides'])
    return res

def get_local_service_id(service):
    """
    return id from service name
    :param service: service name
    :return: service id
    """
    return _internal_services[service]

class RemoteObject:
    """
    Represents a remote object and make messages in the network to call them
    then waits for the response.
    """

    def __init__(self, service_provider, svc_name):
        self.service_provider = service_provider
        self.svc_name = svc_name

    def __str__(self):
        return 'Remote_Service_uuid({})'.format(self.service_provider)

    def __getattr__(self, item):
        def foo(*args, **kwargs):
            # construct request xml string
            method_name = self.svc_name+'.'+item
            xml_request = xmlrpc.create_request((method_name, args))
            print('RPC sending:{}'.format(xml_request))
            fire_content_to(xml_request, 'herald/rpc/xmlrpc', self.service_provider)

            # send the request through micro herald
            # if it receives other message, send it to herald
            # wait to receive the answer
            def checker(msg):
                return msg.subject == 'herald/rpc/xmlrpc/reply'

            xml_answer = wait_for_message(checker).content

            # extract the answer
            return xmlrpc.extract_answer(xml_answer)

            print('{}: {} called with parameters {}, {}'.format(
                self.service_provider,
                item,
                args,
                kwargs))
        return foo


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
    for j in range(0, 3):
        for i in range(0, 4):
            res += gen_rand_hexa()
        res += '-'
    for i in range(0, 12):
        res += gen_rand_hexa()
    return res



def service_rpc_string(service, uid):
    """
    return service prc string

    :param service: service name
    :param uid: uid of microNode
    :return: rpc string

    """
    return {
        'specifications': ['python:/'+service],
        'peer': '{}'.format(uid),
        'configurations': ('herald-xmlrpc',),
        'uid': '{}'.format(uid),
        'properties': {
            'herald.rpc.peer': '{}'.format(uid),
            'endpoint.framework.uuid': '{}'.format(uid),
            'herald.rpc.subject': 'herald/rpc/xmlrpc',
            'objectClass': [service],
            'instance.name': service,
            'service.imported': True,
            'service.imported.configs': ('herald-xmlrpc',),
            'endpoint.service.id': get_local_service_id(service),
            'service.ranking': 0
        },
        'name': 'service_{}'.format(get_local_service_id(service))
    }



def call_service(service_string, params=[]):
    """
    Calls a service available from the service string

    :param service_string: example: "service_29.ping"
    :param params: parameter list for call
    :return: XML string for result

    """
    string_start = service_string.split('.')[0]
    service_id = int(string_start.split('_')[1])
    method = '.'.join(service_string.split('.')[1:])
    # find component that have required service id
    print('service id: {}, method: {}'.format(service_id, method))
    required_component = None
    for name in _class_binding:
        component = _class_binding[name]
        if service_id in _component_info[name]['provides']:
            required_component = component
    if required_component is not None:
        if method in dir(required_component):
            # result = getattr(required_component, method)(required_component, *params)
            result = getattr(required_component, method)(*params)
            return xmlrpc.create_answer(result)
        else:
            print('error: component does not have method {}'.format(method))
    else:
        print('error: service with id {} does not exist'.format(service_id))



def component_execution():
    """

    execute components if they are active and define a run method
    """
    for name in _component_info:
        if _component_info[name]['active']:
            if 'run' in dir(_class_binding[name]):
                _class_binding[name].run()