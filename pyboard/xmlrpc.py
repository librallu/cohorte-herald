

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
