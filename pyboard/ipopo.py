import pyb  # for randomness
from xmlrpc import create_answer
"""
A component can have following decorators :

- componentFactory : indicates the name of the component
- validate method : called when the component is valid
- invalidate method : called when the component is invalid
- provides : provides a service
- requires : requires a service for being validated
- property : defines a property for the service

Components are represented by classes with methods in it.

Services are represented by strings.

TODO:

 - add methods/attributes in object for require & property

"""

# ===== INTERNAL CLASSES =====

class ObservableSet:
    """
    Represents a set object that can
    notify callbacks when a change occurs.
    """

    def __init__(self):
        self._data = set()
        self._listeners_add = set()
        self._listeners_del = set()

    def __repr__(self):
        return str(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, elt):
        return elt in self._data

    def add_listener_add(self, f):
        """
        :param f: function that take an
        element in parameter
        """
        self._listeners_add.add(f)

    def add(self, value):
        """
        add value to add to the dict
        :param value: value to add
        """
        for f in self._listeners_add:
            f(value)
        self._data.add(value)

    def add_listener_del(self, f):
        """
        :param f: function that take an
        element in parameter
        """
        self._listeners_del.add(f)

    def remove(self, value):
        """
        :param value: delete value from dict
        """
        for f in self._listeners_del:
            f(value)
        self._data.remove(value)


# ===== GLOBAL VARIABLES =====

# services provided in the application
_external_services = ObservableSet()
# _external_services = set()

# component name -> class
_class_binding = {}

# temporary variable for exploring components
_ipopo_explorer = {}

_component_info = {}

_id_counter = 0

_internal_services = {}


def get_name(input_class):
    try:
        return input_class.ipopo_component_name
    except AttributeError:
        raise Exception('ERROR inspecting component : \
        Are you sure that you used the decorator @Instantiate when declaring your component ?')

# ===== DECORATORS =====


def ComponentFactory(factory_name):
    """
    adds a field _ipopo_factory_name with name in the component.
    :param factory_name: name of the factory
    """
    def class_builder(original_class):
        print('componentFactory call {}'.format(_ipopo_explorer))
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

        if len(_component_info[name]['requires']) == 0:
            _component_info[name]['active'] = True
        return new_class
    return class_builder


def Instantiate(name):
    """
    instantiate component as name
    :param name:
    :return:
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
        _component_info[name]['active'] = False

        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Validate(function):
    print('validate call')
    _ipopo_explorer['validate'] = function
    return function


def Invalidate(function):
    _ipopo_explorer['invalidate'] = function
    return function


def Provides(service):
    """
    adds field _ipopo_internal_services with a set of services
    provided.
    It will also add
    :param service:
    :return:
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
    def class_builder(original_class):
        new_class = original_class
        name = get_name(new_class)

        _component_info[name]['requires'].add((variable_name, service_name, optional))
        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Property(variable, prop_name, value):
    def class_builder(original_class):
        new_class = original_class
        name = get_name(new_class)

        _component_info[name]['property'].add((variable, prop_name, value))
        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def service_name_from_id(id):
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
        print('\t- active:{}'.format(_component_info[name]['active']))
    print('-'*30)


def is_component_can_start(component):
    """
    :param component:
    :return: True if component can start, false elsewhere
    """
    services_required = _component_info[component]['requires']
    for i in services_required:
        if i not in _external_services:
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
    return _internal_services[service]

class RemoteObject:
    """
    Represents a remote object and make messages in the network to call them
    then waits for the response.
    :return:
    """

    def __init__(self):
        pass

    def __getattr__(self, item):
        def foo(*args, **kwargs):
            print('{} called with parameters {}, {}'.format(item, args, kwargs))
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
            return create_answer(result)
        else:
            print('error: component does not have method {}'.format(method))
    else:
        print('error: service with id {} does not exist'.format(service_id))
