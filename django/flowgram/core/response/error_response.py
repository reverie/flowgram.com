def create(enc, message):
    from flowgram.core.response import data_response

    # The template field is only used for enc=html.
    return data_response.create(enc, 'error', {'template': '500.html',
                                               'message': message})
