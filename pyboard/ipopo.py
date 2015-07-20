import pyb #  for randomness
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

# component name -> class
_class_binding = {}

_component_info = {}


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
        new_class = original_class
        name = get_name(new_class)

        # create fields in component info
        _component_info[name]['factory'] = factory_name

        # rebinds class with name
        _class_binding[name] = new_class

        # finds validate and invalidate decorators
        fields = [getattr(new_class, method) for method in dir(new_class)
                  if callable(getattr(new_class, method))]
        for field in fields:
            if 'ipopo_kind' in dir(field):
                if field.ipopo_kind == 'validate':
                    _component_info[name]['validate'] = field
                elif field.ipopo_kind == 'invalidate':
                    _component_info[name]['invalidate'] = field
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
    function.ipopo_kind = 'validate'
    return function


def Invalidate(function):
    function.ipopo_kind = 'invalidate'
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
        new_class = original_class
        name = get_name(new_class)

        # add service to component info
        _component_info[name]['provides'].add(service)

        # rebinds class with name
        _class_binding[name] = new_class
        return new_class
    return class_builder


def Requires(variable_name, service_name):
    def class_builder(original_class):
        new_class = original_class
        name = get_name(new_class)

        _component_info[name]['requires'].add((variable_name, service_name))
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


def print_ipopo_state():
    """
    For debug use only: print local variables information
    """
    print('='*30)
    print('external_services: {}'.format(_external_services))
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