from flowgram.core.response import html_response, json_response, plist_response

response_encoders = {
    'html': html_response,
    'json': json_response,
    'plist': plist_response,
}


def create(enc, status, object):
    if status == 'ok':
        object = {
            'error': 0,
            'body': object,
        }
    else:
        object['error'] = 1

    return response_encoders[enc].create(object)
