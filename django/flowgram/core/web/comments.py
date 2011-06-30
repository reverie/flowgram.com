from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from flowgram import localsettings
from flowgram.core import controller, encode, helpers, log, models, permissions
from flowgram.core.require import require
from flowgram.core.response import data_response, error_response


# TODO(westphal): Add add method to API.
# TODO(westphal): Convert referencing code to use the API instead.
@require('POST', ['enc=json', 'flowgram_id', 'text'], ['login'])
def add_comment(request, enc, flowgram, text):
    if not text:
        # TODO(westphal): Drop support for XML.
        if enc == 'xml':
            return HttpResponse('No comment text')
        else:
            return error_response.create(enc, 'No comment text')
    comment = models.Comment.objects.create(
        owner=request.user if request.user.is_authenticated() else None,
        flowgram=flowgram,
        text=text)
    controller.record_stat(request, 'add_comment_website', '0', comment.id)
    if localsettings.FEATURE['notify_fw']:
        controller.store_fgcomented_event({'commentor': request.user,
                                           'fg_id': flowgram.id,
                                           'eventCode': 'FG_COMMENTED'})
            
    # TODO(westphal): Drop support for XML.
    if enc == 'xml':
        return HttpResponse(helpers.render_comment_to_xml(comment), mimetype="text/xml")
    else:
        return data_response.create(enc, 'ok', encode.comment.to_dict(comment))


# TODO(westphal): Add delete method to API.
# TODO(westphal): Convert referencing code to use the API instead.
@require('GET', ['enc=html', 'comment_id'], ['login'])
def delete_comment(request, enc, comment_id):
    comment = get_object_or_404(models.Comment, id=comment_id)

    if not permissions.can_edit(request.user, comment.flowgram):
        log.sec_req(request, "User tried to delete comment on flowgram %s." % (comment.flowgram.id))
        raise Http404

    comment.delete()

    controller.record_stat(request, 'del_comment_website', '0', comment_id)
    return helpers.go_back(request)
