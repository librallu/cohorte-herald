
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


### TODO : STEPS

 1.

 2.

 3.

 4.
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

# component list
_waiting_components = ObservableSet()
_active_components = ObservableSet()

# external services provided
_external_services = ObservableSet()


# ===== DECORATORS =====

def validate(function):
    return function


def invalidate(function):
    return function


def provides(original_class, service):
    print('service provided: {}'.format(service))
    return original_class


def requires(original_class, service):
    print('service required: {}'.format(service))
    return original_class


def property(original_class, variable, name, value):
    print('new property: {}, {}, {}'.format(variable, name, value))
    return original_class
