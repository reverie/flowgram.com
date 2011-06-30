def create(enc, status, form):
    from flowgram.core.response import data_response

    output = dict((field, errors) for field, errors in form.errors.iteritems())

    return data_response.create(enc, 'error', output)
