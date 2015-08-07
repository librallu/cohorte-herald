"""
micronode xmlrpc file.
"""

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
    if value_list is None:
        value_list = []
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

    :param request_content: content of the request
    :return: tuple (a,b)
        - a: method name
        - b: list of args
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
    """
    create request string in xml with request info parameter
    :param request_info: request information (methodName, argument value list)
    :return: xml string
    """
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


def extract_service_description(content_string):
    """
    extracts content from string received with a service
    description message

    :param content_string:
    :return:
    """
    content_object = eval(content_string)
    res = []
    for i in content_object:
        res.append(
            {
                'uuid': i['peer'],
                'spec': i['properties']['objectClass'][0],
                'name': i['name']
            }
        )
    return res


if __name__ == '__main__':
    s1 = """
    <?xml version='1.0'?>
        <methodResponse>
        <params>
            <param>
                <value><int>78</int></value>
            </param>
            <param>
                <value><string>hello world !</string></value>
            </param>
        </params>
    </methodResponse>"""
    print(extract_answer(s1))
    print(create_answer(extract_answer(s1)))
    print(create_request(('hello', ['hello', 42])))
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

    mac = "ADRESSE MAC"
    uid = "DISTANT UID"

    content = """[{'uid':'86006913-0197-56a2-d8f7-0e490f54617a','properties':
    {'service.ranking':0,'herald.rpc.subject':'herald/rpc/xmlrpc','objectClass':
    ['pyboard.led.ledService'],'herald.rpc.peer':
    '86006913-0197-56a2-d8f7-0e490f54617a','instance.name':
    'pyboard.led.ledService','service.imported':True,
    'service.imported.configs':('herald-xmlrpc',),
    'endpoint.framework.uuid':'86006913-0197-56a2-d8f7-0e490f54617a',
    'endpoint.service.id':0},'name':'service_0','specifications':
    ['python:/pyboard.led.ledService'],'configurations':('herald-xmlrpc',),
    'peer':'86006913-0197-56a2-d8f7-0e490f54617a'}]"""

    print(extract_service_description(content))
