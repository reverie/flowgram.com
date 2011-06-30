def check(request, method_args, transformed_values):
    from django.contrib.auth import REDIRECT_FIELD_NAME
    from django.utils.http import urlquote

    from flowgram import settings
    from flowgram.core.require import RedirectException

    if not request.user.is_authenticated():
        raise RedirectException('%s?%s=%s' % (settings.LOGIN_URL, 
                                              REDIRECT_FIELD_NAME,
                                              urlquote(request.get_full_path())))

    return True
