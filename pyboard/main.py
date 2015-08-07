
from herald import extract_herald_message, manage_message, put_message, uid
from ipopo import component_execution, init_ipopo
from serial_herald_message import *



from components import *


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


def wait_for_message(message_checker):
    """
    blocking call to get a message
    :return: message received
    """
    while True:
        msg = extract_herald_message()
        if msg and message_checker(msg):
            return msg
        elif msg:
            print("-- MANAGE MESSAGE PASS MESSAGE"+msg.subject)
            manage_message(msg)


def fire_content_to(content, subject, destination):
    """
    ipopo interface to send content to a destination

    :param content: content to send
    :param subject: subject for the message
    :param destination: destination for the message
    """
    put_message(
        SerialHeraldMessage(
            subject=subject,
            sender_uid=uid,
            original_sender=uid,
            final_destination=destination,
            content=content,
        ).to_automata_string(), encapsulate=False
    )

def main():
    """
    main loop of microNode
    """

    # creating internal state of pyboard
    print('iPOPO initialization')
    init_ipopo(wait_for_message, fire_content_to)
    # while True:
    #     ipopo.print_ipopo_state()
    #     pyb.delay(2000)

    # main loop
    print('starting main loop')
    while True:
        msg = extract_herald_message()
        if msg:
            manage_message(msg)
        component_execution()


if __name__ == '__main__':
    main()
