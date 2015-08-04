
import pyb
from ipopo import *
from xmlrpc import *

# automata import
import automata
from serial_herald_message import *

from components import *



# bluetooth connection initialization
uart = pyb.UART(1, 38400)

# define node uid for the pyboard
uid = gen_node_uid()
# use mac address of the bluetooth module (fixed)
mac = '20:14:03:19:88:23'
# automata for reading bluetooth flow
automata = automata.SerialAutomata()


def get_message_uart():
    """
    :return: new message as a string from uart, None if
        there are no new messages
    """
    if uart.any():
        message = to_string(uart.read())
        while uart.any():  # for getting entire message
            message += to_string(uart.read())
        print('UART RECEIVED: {}'.format(message))
        return message
    return None


def set_led(value):
    """
    set the led to a given value

    :param value: True for ON, False for OFF
    :return: None

    """
    if value:
        pyb.Pin(led_pin, pyb.Pin.OUT_PP).high()
    else:
        pyb.Pin(led_pin, pyb.Pin.OUT_PP).low()


def get_photo_value():
    """
    :return: photoreceptor value as a string
    """
    return str(pyb.ADC(photo_pin).read())


def put_message(message, encapsulate=True):
    """
    put a bluetooth message to the peer.
    It doesn't add delimiters because
    it is supposed to be done by the
    Reader object.

    :param message: string message
    :return: None

    """
    output = to_string(message)
    if encapsulate:
        output = str(len(message))+DELIMITER+to_string(message)
    print('uart sending: {}'.format(output))
    uart.write(output)


def hello_callback():
    """
    called when a hello message appears.
    It will simply send back a hello message

    :return: Nothing

    """
    put_message(HELLO_MESSAGE)


def compress_msg(message, no_spaces=False):
    """
    removes new lines, tabs and spaces in a message

    :param message: message to be compressed
    :return: new message (compressed)

    """
    message = message.replace('\n', '')
    message = message.replace('\t', '')
    if not no_spaces:
        message = message.replace(' ', '')
    return message


def get_step2_response(request):
    """
    :param request: SerialHeraldMessage object of the request
    :return: step2 response (SerialHeraldMessage object)
    """
    content = '''
    {
        "accesses": {"bluetooth": " '''+mac+''' "},
        "name": " '''+uid+''' ",
        "node_name": " '''+uid+''' ",
        "node_uid": " '''+uid+''' ",
        "groups": {},
        "app_id": "<herald-legacy>",
        "uid": " '''+uid+''' ",
    }
    '''
    content = compress_msg(content)

    return SerialHeraldMessage(
        subject='herald/directory/discovery/step2',
        sender_uid=uid,
        original_sender=uid,
        final_destination=request.original_sender,
        content=content,
        reply_to=request.message_uid
    ).to_automata_string()


def get_step3_response(request, group='all'):
    """
    :param request: SerialHeraldMessage object of the request
    :return: step3 response (SerialHeraldMessage object)
    """
    res = []
    for service in ipopo_exported():
        service_name = service_name_from_id(service)
        res.append(service_rpc_string(service_name, uid))
    content = str(res)
    content = compress_msg(content)

    subject = 'herald/rpc/discovery/add'

    return SerialHeraldMessage(
        subject=subject,
        sender_uid=uid,
        original_sender=uid,
        final_destination=request.original_sender,
        content=content,
        reply_to=request.message_uid,
        group=group
    ).to_automata_string()


def get_contact_answer(request):
    # TODO add services exported by peer
    return get_step3_response(request)


def get_rpc_answer(request):
    """
    :param request: SerialHeraldMessage object of the request
    :return: xmlrpc response (SerialHeraldMessage object)
    """
    # content = '''
    # <?xml version='1.0'?>
    #     <methodResponse>
    #     <params>
    #         <param>
    #             <value><int>78</int></value>
    #         </param>
    #     </params>
    # </methodResponse>
    # '''
    content = call_service(*extract_request_info(request.content))
    print("responding request with {}".format(content))
    content = compress_msg(content, no_spaces=True)

    return SerialHeraldMessage(
        subject='herald/rpc/xmlrpc/reply',
        sender_uid=uid,
        original_sender=uid,
        final_destination=request.original_sender,
        content=content,
        reply_to=request.message_uid
    ).to_automata_string()



def get_routing_answer(request):
    """
    :param request: SerialHeraldMessage object of the routing hello request
    :return: response for hello request
    """
    return SerialHeraldMessage(
        subject='herald/routing/reply/N/',
        sender_uid=uid,
        original_sender=uid,
        final_destination=request.original_sender,
        content='micronode',
        reply_to=request.message_uid
    ).to_automata_string()


def manage_message(message):
    """
    Extract useful information in the message
    and do something if necessary

    :param message: message received
    :return: Nothing

    """
    print('herald message received:')
    print(message)
    # bean is of type MessageReceived
    if message.subject == 'herald/directory/discovery/step1':
        print('** SENDING STEP 2 MESSAGE **')
        put_message(get_step2_response(message), encapsulate=False)
    elif message.subject == 'herald/directory/discovery/step3':
        print('** SENDING ADD MESSAGE TO ADD PYBOARD SERVICES')
        put_message(get_step3_response(message), encapsulate=False)
    elif message.subject == 'herald/rpc/xmlrpc':
        print('** SENDING RESPONSE MESSAGE TO XMLRPC MESSAGE')
        put_message(get_rpc_answer(message), encapsulate=False)
    elif to_string(message.subject) == to_string('herald/routing/hello/'):
        print('** RESPONDING TO ROUTING HELLO MESSAGE')
        put_message(get_routing_answer(message), encapsulate=False)
    elif to_string(message.subject) == to_string('herald/rpc/discovery/add'):
        put_message(get_contact_answer(message), encapsulate=False)
    elif to_string(message.subject) == to_string('herald/rpc/discovery/contact'):
        put_message(get_contact_answer(message), encapsulate=False)
    else:
        print('** UNMATCHED MESSAGE: {}'.format(message.subject))


# herald message handlers
reader = MessageReader(automata, hello_callback)

def extract_herald_message():
    """
    :return: new herald message if any, None elsewhere
    """
    # get message from uart
    new_message = get_message_uart()
    if new_message:
        automata.read(new_message)
    # pass it to the message reader
    msg = reader.read()
    return msg


def main():
    """
    main loop of microNode
    """

    # creating internal state of pyboard
    print('iPOPO initialization')
    # while True:
    #     print_ipopo_state()
    #     pyb.delay(2000)

    # main loop
    print('starting main loop')
    while True:
        msg = extract_herald_message()
        if msg:
            manage_message(msg)


if __name__ == '__main__':
    main()
