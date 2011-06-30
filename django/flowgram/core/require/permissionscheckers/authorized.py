def check(request, method_args, transformed_values):
    """Allows access if the request comes from an internal IP,  the user is logged in, or the
       feature flag required_login_browse is not set."""
    from django.contrib.auth import REDIRECT_FIELD_NAME
    from django.utils.http import urlquote

    from flowgram import localsettings, settings
    from flowgram.core.require import RedirectException

    if request.user.is_authenticated() or not localsettings.FEATURE['required_login_browse']:
        return True

    ip = request.META.get('REMOTE_ADDR', '')
    if ip in localsettings.fg_INTERNAL_IPS:
        return True
    
    raise RedirectException('%s?%s=%s' % (settings.LOGIN_URL, 
                                          REDIRECT_FIELD_NAME,
                                          urlquote(request.get_full_path())))
