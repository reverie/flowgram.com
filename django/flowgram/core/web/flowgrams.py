from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape

from flowgram import localsettings
from flowgram.core import cached_sets, controller, helpers, permissions, webhelpers
from flowgram.core.require import require


# Convert to use AJAX/API.
@require(None, ['enc=html', 'flowgram_id'], ['edit_flowgram'])
def delete_flowgram(request, enc, flowgram):
    if request.method == 'POST':
        list_page = flowgram.owner.get_profile().url()
        helpers.add_bad_message(request, "Flowgram \"%s\" was deleted" % flowgram.title)
        flowgram.delete()
        return HttpResponseRedirect('/you/')
    else:
        return helpers.req_render_to_response(request, 'dialogs/delete_fg.html', {'fg': flowgram})


# Convert to use AJAX/API.
# TODO(westphal): Protect output in general.
@require('POST', ['enc=html', 'flowgram_id', 'description='], ['edit_flowgram'])
def edit_flowgram_description(request, enc, flowgram, description):
    flowgram.description = description
    flowgram.save()
    return HttpResponse(escape(flowgram.description))


# Convert to use AJAX/API.
@require('POST', ['enc=html', 'flowgram_id', 'title='], ['edit_flowgram'])
def edit_flowgram_title(request, enc, flowgram, title):
    flowgram.title = title or controller.DEFAULT_FG_TITLE
    flowgram.save()
    return HttpResponse(escape(flowgram.title))


@require('GET', ['enc=html', 'flowgram_id'], ['authorized', 'view_flowgram'])
def share_flowgram(request, enc, flowgram):
    return helpers.req_render_to_response(
        request,
        'flowgram/share_flowgram.html',
        {'fg': flowgram})


@require('GET', ['enc=html', 'flowgram_id'], ['authorized', 'view_flowgram'])
def show_flowgram(request, enc, flowgram):
    can_edit = permissions.can_edit(request.user, flowgram)
    context = {
        'fg': flowgram,
         'can_edit': can_edit,
         'subs_active': localsettings.FEATURE['subscriptions_fw'],
         'show_delete': can_edit,
         'active': 'you' if request.user == flowgram.owner else 'browse',
         'mostviewed': cached_sets.most_viewed()[:6],
         'send_to_details': localsettings.FEATURE['send_to_details']
    }
    context.update(webhelpers.get_flowgram_stats(flowgram))
    controller.record_stat(request, 'view_flowgram_det_website', '0', flowgram.id)
    return helpers.req_render_to_response(
        request,
        'flowgram/show_flowgram.html',
        context)
