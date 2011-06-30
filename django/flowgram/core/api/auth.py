from django.conf import settings

from flowgram.core.require import require
from flowgram.core.response import data_response


@require('POST', ['enc=json', 'username', 'password', 'remember:boolean'])
def ajax_login(request, enc, user, password, remember):
    from django.contrib import auth
    from flowgram.core.helpers import get_post_token_value

    username = user.username

    user = auth.authenticate(username=username, password=password)
    assert(user)
    auth.login(request, user)
    request.session[settings.PERSISTENT_SESSION_KEY] = remember

    return data_response.create(
        enc,
        'ok',
        {
            'username': username,
            'post_token': get_post_token_value(request),
            'session_id': request.COOKIES[settings.SESSION_COOKIE_NAME]
        })
