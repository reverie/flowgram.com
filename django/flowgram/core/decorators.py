from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.http import urlquote
from flowgram.localsettings import fg_INTERNAL_IPS, FEATURE
from flowgram.core import controller

# TODO(andrew): rename/think/factor these

def authorized(view_func):
    """Allows access if request comes from an internal IP *OR* the user is logged in."""
    login_url = settings.LOGIN_URL
    @wraps(view_func)
    def _check_ip(request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR', '')
        if (ip in fg_INTERNAL_IPS) or request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, urlquote(request.get_full_path())))
    @wraps(view_func)
    def _yes(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return not FEATURE['required_login_browse'] and _yes or _check_ip 


def internal(view_func):
    """Allows access only if the request comes from an internal IP."""
    @wraps(view_func)
    def _check_ip(request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR', '')
        if ip in fg_INTERNAL_IPS:
            return view_func(request, *args, **kwargs)
        raise Http404
    return _check_ip


def analytics_check_anon_create(view_func):
    """Check if it is anonymous click create."""
    @wraps(view_func)
    def _check_anon_create(request, *args, **kwargs):
        if request.user.is_anonymous():
            controller.record_stat(request, 'view_create_website', '0', '')
        return view_func(request, *args, **kwargs)
    return _check_anon_create

