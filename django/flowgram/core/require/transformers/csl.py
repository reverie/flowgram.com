# A comma-separated-list transformer.

def from_string(request, string):
    if not string:
        return (None, [])
    return (None, string.split(','))
