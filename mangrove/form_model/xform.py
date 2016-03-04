import xml.etree.ElementTree as ET

class Xform(object):

    def __init__(self, xform):
        ET.register_namespace('', 'http://www.w3.org/2002/xforms')
        self.root_node = ET.fromstring(xform)

    def get_body_node(self):
        return self.root_node._children[1]

    def equals(self, another_xform):
        another_xform_str = ET.tostring(another_xform.root_node)\
            .replace(_instance_node(another_xform.root_node), _instance_node(self.root_node))
        return ET.tostring(self.root_node) == another_xform_str


def get_node(node, field_code):
    for child in node:
        if child.tag.endswith('repeat'):
            for inner_child in child:
                if 'ref' in inner_child.attrib and inner_child.attrib['ref'].endswith(field_code):
                    return inner_child

        if 'ref' in child.attrib and child.attrib['ref'].endswith(field_code):
            return child


def _instance_node(node):
    return _child_node(_child_node(_child_node(node, 'head'), 'model'), 'instance')._children[0].attrib['id']


def _child_node(node, tag):
    for child in node:
        if child.tag.endswith(tag):
            return child