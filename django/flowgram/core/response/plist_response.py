def create(object):
    from django.http import HttpResponse
    from django.utils import simplejson

    return HttpResponse(encode(object), mimetype='application/x-plist')


# HELPERS-------------------------------------------------------------------------------------------


import re


ESCAPE = re.compile(r'[&<>]')
ESCAPE_ASCII = re.compile(r'([\\"/&<>]|[^\ -~])')
ESCAPE_DCT = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '&#x%04x;' % (i,))


def encode(obj):
    return ''.join([
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n',
        '<plist version="1.0">\n',
        encode_object(obj),
        '</plist>\n',
    ])


def encode_object(obj):
    if isinstance(obj, basestring):
        return encode_basestring(obj)
    elif obj is True:
        return '<true/>\n'
    elif obj is False:
        return '<false/>\n'
    elif isinstance(obj, (int, long)):
        return encode_int(obj)
    elif isinstance(obj, float):
        return encode_float(obj)
    elif isinstance(obj, (list, tuple)):
        output = ['<array>\n']
        output.extend([encode_object(item) for item in obj if item is not None])
        output.append('</array>\n')
        return ''.join(output)
    elif isinstance(obj, dict):
        output = ['<dict>\n']
        output.extend(['<key>%s</key>\n%s' % (str(ESCAPE_ASCII.sub(escape_string, key)),
                                              encode_object(obj[key])) \
                           for key in obj.keys() if obj[key] is not None])
        output.append('</dict>\n')
        return ''.join(output)


def encode_basestring(obj):
    return '<string>%s</string>\n' % str(ESCAPE_ASCII.sub(escape_string, obj))


def encode_float(obj):
    return '<real>%s</real>\n' % str(obj)


def encode_int(obj):
    return '<integer>%s</integer>\n' % str(obj)


def escape_string(match):
    s = match.group(0)
    try:
        return ESCAPE_DCT[s]
    except KeyError:
        return '&#x%04x;' % (ord(s),)
