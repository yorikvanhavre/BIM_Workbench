"""This script converts the computer iterpretable listing ifcXML XSD into a list
of non-abstract children of IfcProduct"""

import xml.sax

class IfcElementHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.elements = []

    def startElement(self, name, attrs):
        if name == "xs:element"  and "substitutionGroup" in attrs:
            self.elements.append({
                "name": attrs["name"],
                "abstract": True if "abstract" in attrs else False,
                "parent": attrs["substitutionGroup"][len("ifc:"):]
            })

    def endDocument(self):
        elements = []
        for element in self.elements:
            if element["abstract"]:
                continue
            if self.is_an_ifcproduct(element):
                elements.append(element["name"])
        self.elements = elements

    def is_an_ifcproduct(self, element):
        if element["parent"] == "IfcProduct":
            return True
        else:
            for parent in self.elements:
                if parent["name"] == element["parent"]:
                    return self.is_an_ifcproduct(parent)
        return False

xsd_path = "IFC4_ADD2.xsd"
handler = IfcElementHandler()
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
parser.parse(xsd_path)
for element in handler.elements:
    print(element)
