from django.http import HttpResponse, HttpResponseRedirect

from flowgram import localsettings
from flowgram.core import controller, models
from flowgram.core.require import require


# TODO(westphal): Convert to AJAX/JSON.
@require('POST', ['enc=html', 'flowgram_id', 'tag_name'], ['login', 'view_flowgram'])
def add_tag(request, enc, flowgram, tag_name):
    tag_name = tag_name.strip()
    
    (tag, null) = models.Tag.objects.get_or_create(adder=request.user,
                                                   flowgram=flowgram,
                                                   name=tag_name)
    
    controller.record_stat(request, 'add_tag_website', '0', flowgram.id)
    
    if localsettings.FEATURE['notify_fw']:
        controller.store_fgtagged_event({'current_user': request.user,
                                         'fg_id': flowgram.id,
                                         'eventCode': 'FG_TAGGED'})

    return HttpResponse(tag.name)


# TODO(westphal): Convert to AJAX/JSON.
@require(None, ['enc=html', 'flowgram_id', 'tag_name'], ['login'])
def delete_tag(request, enc, flowgram, tag_name):
    models.Tag.objects.filter(flowgram=flowgram, name=tag_name).delete()
    controller.record_stat(request, 'del_tag_website', '0', flowgram.id)
    return HttpResponseRedirect(flowgram.url())
