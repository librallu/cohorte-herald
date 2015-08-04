
Bluetooth
=========

Cette partie présente le transport bluetooth présent dans *Herald*.



Beans
-----

.. autoclass:: herald.transports.bluetooth.beans.BluetoothAccess
    :members:
    :special-members:





Bluetooth Manager
-----------------

.. autoclass:: herald.transports.bluetooth.bluetooth_manager.BluetoothManager
    :members:
    :special-members:




Communication Set
-----------------

.. autoclass:: herald.transports.bluetooth.communication_set.CommunicationSet
    :members:
    :special-members:




Connection
----------

.. autoexception:: herald.transports.bluetooth.connection.NotValid
    :members:

.. autoclass:: herald.transports.bluetooth.connection.Connection
    :members:
    :special-members:



Directory
---------


.. autoclass:: herald.transports.bluetooth.directory.BluetoothDirectory
    :members:
    :special-members:


Discovery
---------

.. autoclass:: herald.transports.bluetooth.discovery.Discovery
    :members:
    :special-members:





Serial Automata
---------------

.. autoclass:: herald.transports.bluetooth.serial_automata.SerialAutomata
    :members:
    :special-members:



Serial Herald Message
---------------------


.. automethod:: herald.transports.bluetooth.serial_herald_message.to_string

.. automethod:: herald.transports.bluetooth.serial_herald_message.to_bluetooth_message

.. automethod:: herald.transports.bluetooth.serial_herald_message.gen_uuid

.. autoclass:: herald.transports.bluetooth.serial_herald_message.MessageReader
    :members:
    :special-members:

.. autoclass:: herald.transports.bluetooth.serial_herald_message.SerialHeraldMessage
    :members:
    :special-members:



Transport
---------

.. autoclass:: herald.transports.bluetooth.transport.BluetoothTransport
    :members:
    :special-members:

