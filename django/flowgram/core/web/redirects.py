from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from flowgram import localsettings
from flowgram.core import controller, helpers, models, s3
from flowgram.core.require import require


@require('GET', ['enc=html', 'flowgram_id'], ['view_flowgram'])
def details_redirect(request, enc, flowgram):
    return helpers.req_render_to_response(request, 'flowgram/details_redirect.html', {'fg': flowgram})


@require('GET', ['enc=html', 'flowgram_id'])
def flag_flowgram(request, enc, flowgram):
    from flowgram.core.mail import announce_flag

    announce_flag(request, flowgram)
    helpers.add_good_message(request,
                             "Thanks for your help. An administrator will review this Flowgram.")
    return HttpResponseRedirect(flowgram.url())


@require('GET', ['enc=html', 'css_id'])
def get_css(request, enc, css_id):
    get_css_request = get_object_or_404(models.GetCssRequest, id=css_id)

    if get_css_request.status_code == models.StatusCode.DONE:
        return s3.redirect_to_key(localsettings.S3_BUCKET_CSS, get_css_request.id + ".css")
    else:
        return HttpResponseRedirect(get_css_request.url)


@require('GET', ['enc=html', 'name'])
def goto_quick_link(request, enc, name):
    return HttpResponseRedirect(models.QuickLink.objects.get(name=name).url)


# TODO(westphal): This may not be used anymore, but maybe we should be using it.
@require('GET', ['enc=html', 'sharelink_name'])
def show_shared_flowgram(request, enc, sharelink_name):
    share_link = models.ShareLink.objects.get(name=sharelink_name)
    share_link.clicks += 1
    share_link.save()
    
    return HttpResponseRedirect(share_link.flowgram.url())


@require('GET', ['enc=html', 'username', 'sort_criterion'], ['authorized'])
def view_favorites_redirect(request, enc, username, sort_criterion):
    return HttpResponseRedirect('/%s/favorites/%s/all' % (username, sort_criterion or 'modified'))


@require('GET', ['enc=html', 'username', 'sort_criterion'], ['authorized'])
def view_your_flowgrams_thumb_redirect(request, enc, username, sort_criterion):
    return HttpResponseRedirect('/%s/viewyourflowgramsthumb/%s/all' % \
                                    (username, sort_criterion or 'modified'))


@require('GET', ['enc=html', 'flowgram_id'], ['view_flowgram'])
def widget_play_flowgram(request, enc, flowgram):
    return helpers.req_render_to_response(request, 'flowgram/widget_play_redirect.html', {'fg': flowgram})


@require('GET', ['enc=html'], ['login'])
def you(request, enc):
    controller.record_stat(request, 'view_yourFGs_website', '0', '')
    return HttpResponseRedirect('/%s/viewyourflowgramsthumb' % request.user.username)
