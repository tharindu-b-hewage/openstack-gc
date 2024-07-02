import xmltodict


def parse_xml(path):
    # Parse the XML file to an string
    with open(path, 'r') as f:
        return xmltodict.parse(f.read())
