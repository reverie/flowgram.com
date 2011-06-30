from django.views.decorators.vary import vary_on_headers

from flowgram import localsettings
from flowgram.core import controller, helpers, webhelpers
from flowgram.core.decorators import analytics_check_anon_create
from flowgram.core.require import require


@analytics_check_anon_create
@require('GET', ['enc=html'], ['login'])
def create_easy(request, enc):
    (flowgram, new) = controller.get_working_flowgram(request.user)

    hash_parts = ['%s-%s' % (key, request.GET[key]) for key in sorted(request.GET.keys())]
    
    controller.record_stat(request, 'view_create_website', '0', '')

    return helpers.redirect("/r/%s/%s" % (flowgram.id, '__'.join(hash_parts)))

    
@vary_on_headers('User-Agent')
@require('GET', ['enc=html'], ['login'])
def create_toolbar_continue(request, enc):
    (browser, version) = webhelpers.get_brower_and_version(request)
    return helpers.req_render_to_response(request,
                                          "create/create_continue.html",
                                          {'domain_name': localsettings.MASTER_DOMAIN_NAME, 
                                           'browser': browser,
                                           'browser_version': version})


@vary_on_headers('User-Agent')
@require('GET', ['enc=html'], ['login'])
def create_toolbar_landing(request, enc):
    (browser, version) = webhelpers.get_brower_and_version(request)
    return helpers.req_render_to_response(request,
                                          "create/toolbar_landing.html",
                                          {'domain_name': localsettings.MASTER_DOMAIN_NAME, 
                                           'browser': browser,
                                           'browser_version': version})
