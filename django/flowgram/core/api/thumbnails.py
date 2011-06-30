from django.http import Http404
from django.views.decorators.cache import cache_control

from flowgram import localsettings
from flowgram.core import log, models, s3
from flowgram.core.require import require


@cache_control(max_age=86400)
@require('GET', ['flowgram_id', 'width:int', 'height:int'], ['view_flowgram'])
def get_fg_thumb_by_dims(request, flowgram, width, height):
    pages = models.Page.objects.filter(flowgram=flowgram).order_by('position')[:1]
    
    # TODO(westphal): Make this point to a default thumbnail.
    if not len(pages):
        log.info("get_fg_thumb_by_dims called on flowgram with no pages: flowgram_id %s" % flowgram_id)
        raise Http404

    return redirect_to_page_thumb_page_by_dims(request, pages[0], width, height)


@cache_control(max_age=86400)
@require('GET', ['page_id'], ['view_page'])
def get_thumb(request, page):
    return s3.redirect_to_key(localsettings.S3_BUCKET_THUMB, page.small_thumb_filename())


@cache_control(max_age=86400)
@require('GET', ['page_id', 'width:int', 'height:int'], ['view_page'])
def get_thumb_by_dims(request, page, width, height):
    return redirect_to_page_thumb_page_by_dims(request, page, width, height)


# Helpers ------------------------------------------------------------------------------------------


def redirect_to_page_thumb_page_by_dims(request, page, width, height):
    filename = "%s_%d_%d.jpg" % (page.id, width, height)
    return s3.redirect_to_key(localsettings.S3_BUCKET_THUMB, filename)
