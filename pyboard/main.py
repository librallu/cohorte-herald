
from herald import extract_herald_message, manage_message
from ipopo import component_execution


def main():
    """
    main loop of microNode
    """

    # creating internal state of pyboard
    print('iPOPO initialization')
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
