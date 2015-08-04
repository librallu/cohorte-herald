from automata import *
from serial_herald_message import *
from uuid import uuid4

a = SerialAutomata()
reader=MessageReader(a)
mi = SerialHeraldMessage('a', 'b', 'c', 'd', 'e', reply_to='nope', group='all')
mi.set_uid(str(uuid4()))
print(mi)
print(mi.to_automata_string())
a.read(mi.to_automata_string())

m2 = None
while not m2:
    m2 = reader.read()
print(m2)