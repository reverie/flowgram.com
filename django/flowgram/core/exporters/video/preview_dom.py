import sys, traceback
from xml.dom import minidom, Node


def display_dom(tag, tabs):
    attributes = []
    if tag.attributes:
        for attribute in tag.attributes.keys():
            attributes.append('%s="%s"' % (attribute, tag.getAttribute(attribute)))

    print '%s<%s %s>' % (tabs, tag.tagName, ' '.join(attributes))
    for child_tag in tag.childNodes:
        if child_tag.nodeType == Node.ELEMENT_NODE:
            display_dom(child_tag, tabs + '  ')
    print '%s</%s>' % (tabs, tag.tagName)


filename = sys.argv[1]
storage_dir = sys.argv[2]

try:
    document = minidom.parse('%s%s' % (storage_dir, filename))
    display_dom(document.firstChild, '')
except Exception, e:
    print 'There was a problem parsing the XML in the specified file: %s' % str(e)
