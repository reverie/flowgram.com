def from_string(request, string):
    return (None, bool(string.lower() == 'true'))
