import Sofa
import SofaRuntime
import xml.dom.minidom
import json


def generate_node_attributes(schema):
    node = Sofa.Core.Node("node")
    for data in node.getDataFields():
        if not data.isReadOnly() or data.getName() == "dt":
            use = ""
            if data.isRequired():
                use = """use="required" """
            if data.getName() == "name":
                use = """use="required" """
            schema += f"""<xs:attribute name="{data.getName()}" type="xs:string" {use}/>"""
    return schema


def generate_sofa_components(schema, json_str):
    schema += """<!-- SOFA Components -->"""

    j = json.loads(json_str)
    for component in j:
        schema += f"""<xs:element name="{component["className"]}" minOccurs="0" maxOccurs="unbounded">"""

        schema += """<xs:complexType><xs:sequence/>"""

        has_template = False
        for _, creator in component["creator"].items():
            if creator["class"]["templateName"] != "":
                has_template = True

        if has_template:
            schema += f"""<xs:attribute name="template" type="xs:string"/>"""

        data_set = set()
        for _, creator in component["creator"].items():
            for data in creator["object"]["data"]:
                data_set.add(data["name"])
        for data in data_set:
            schema += f"""<xs:attribute name="{data}" type="xs:string"/>"""

        schema += """<xs:anyAttribute processContents="lax"/>"""

        schema += """</xs:complexType>"""

        schema += f"""</xs:element>"""
    return schema


def generate_node(schema, json_str):
    schema += """
<xs:element name="Node">
<xs:complexType>
<xs:sequence>
<!-- Node can contain other Nodes --><xs:element ref="Node" minOccurs="0" maxOccurs="unbounded"/>
<!-- Allow any other element --><xs:any minOccurs="0" maxOccurs="unbounded" processContents="lax"/>"""
    schema = generate_sofa_components(schema, json_str)
    schema += f"""\n</xs:sequence>"""
    schema = generate_node_attributes(schema)
    schema += """
</xs:complexType>
</xs:element>
"""
    return schema


def generate_xml_schema(json_str):
    schema = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">"""

    schema = generate_node(schema, json_str)

    schema += """</xs:schema>"""

    schema = schema.replace('\n', ' ').replace('\r', '')
    dom = xml.dom.minidom.parseString(schema)

    return dom.toprettyxml(indent="    ")


def main():
    xsd_filename = "sofa.xsd"
    with open(xsd_filename, "w") as f:
        SofaRuntime.importPlugin("Sofa.Component")
        json_str = Sofa.Core.ObjectFactory.dump_json()
        f.write(generate_xml_schema(json_str))


if __name__ == "__main__":
    main()