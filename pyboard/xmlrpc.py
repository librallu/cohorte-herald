

def extract_answer(xml_string):
    """
    parse xml_string representing herald xmlrpc response
    and extract int and string arguments.
    :param xml_string: input string
    :return: list of parsed values (int or string)
    """
    values = xml_string.split('<value>')
    typed_values = [i.split('</value>')[0] for
                    i in values
                    if len(i.split('</value>')) > 1]
    res = []
    for i in typed_values:
        if len(i.split('<int>')) > 1:  # if int variable
            res.append(int(i.split('<int>')[1].split('</int>')[0]))
        elif len(i.split('<string>')) > 1:  # if string variable
            res.append(i.split('<string>')[1].split('</string>')[0])

    return res


def create_answer(value_list):
    """
    generate xml string for the answer
    :param value_list: input list of values
    :return: generated xml string
    """
    res = "<?xml version='1.0'?>"
    res += "<methodResponse><params>"
    for i in value_list:
        if isinstance(i, int):
            res += '<param><value><int>{}</int></value></param>'.format(i)
        elif isinstance(i, str):
            res += '<param><value><string>{}</string></value></param>'.format(i)

    res += "</params></methodResponse>"
    return res


def extract_request_info(request_content):
    """
    extract information from request
    :param request_content: content of the request
    :return: tuple (a,b)
        - a: method name
        - b: list of args

    examples:
        <?xml version='1.0'?>
        <methodCall>
            <methodName>service_29.ping</methodName>
            <params>
                <param><value><int>42</int></value></param>
                <param><value><string>Hello world !</string></value></param>
            </params>
        </methodCall>

        returns (service_29.ping, [42])
    """
    method = request_content.split('<methodName>')[1].split('</methodName>')[0]
    values = request_content.split('<value>')
    typed_values = [i.split('</value>')[0] for
                    i in values
                    if len(i.split('</value>')) > 1]
    res = []
    for i in typed_values:
        if len(i.split('<int>')) > 1:  # if int variable
            res.append(int(i.split('<int>')[1].split('</int>')[0]))
        elif len(i.split('<string>')) > 1:  # if string variable
            res.append(i.split('<string>')[1].split('</string>')[0])
    return method, res



def create_request(request_info):
    res = "<?xml version='1.0'?>"
    res += "<methodCall>"
    res += "<methodName>{}</methodName>".format(request_info[0])
    res += "<params>"
    for arg in request_info[1]:
        if isinstance(arg, str):
            res += "<param><value><string>{}</string></value></param>".format(arg)
        elif isinstance(arg, int):
            res += "<param><value><int>{}</int></value></param>".format(arg)
        else:
            res += "<param><value><unknown>{}</unknown></value></param>".format(arg)
    res += "</params>"
    res += "</methodCall>"
    return res


if __name__ == '__main__':
    # s1 = """
    # <?xml version='1.0'?>
    #     <methodResponse>
    #     <params>
    #         <param>
    #             <value><int>78</int></value>
    #         </param>
    #         <param>
    #             <value><string>hello world !</string></value>
    #         </param>
    #     </params>
    # </methodResponse>"""
    # print(extract_answer(s1))
    # print(create_answer(extract_answer(s1)))
    # print(create_request(('hello', ['hello', 42])))
    s2 = """
        <?xml version='1.0'?>
        <methodCall>
            <methodName>service_29.ping</methodName>
            <params>
                <param><value><int>42</int></value></param>
                <param><value><string>Hello world !</string></value></param>
            </params>
        </methodCall>
    """
    print(extract_request_info(s2))
