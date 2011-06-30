from datetime import datetime

from django.http import HttpResponse
from flowgram import localsettings
from flowgram.core import controller, encode, helpers, log, models, permissions
from flowgram.core.require import require
from flowgram.core.response import data_response


# TODO(westphal): Make this return a standard response.
def can_edit_fg(request, flowgram_id):
    try:
        log.debug('[can_edit_fg flowgram_id: %s]' % flowgram_id)
        flowgram = models.Flowgram.objects.get(id=flowgram_id)
        log.debug('(1 %s)' % request.user.username)
    except models.Flowgram.DoesNotExist:
        return HttpResponse('0 fg does not exist')

    log.debug('(2)')
    if permissions.can_edit(request.user, flowgram):
        log.debug('(3)')
        return HttpResponse('1')
    else:
        log.debug('(4)')
        return HttpResponse('0 user can\'t edit')


@require('POST', ['title='], ['login'])
def create_flowgram(request, title):
    flowgram = controller.new_flowgram(request.user, title)
    controller.set_working_flowgram(request.user, flowgram)

    log.debug("Action log: create_flowgram %s for %s" % (flowgram.id, request.user.username))

    return data_response.create(request.POST.get('enc', 'json'),
                                'ok',
                                encode.flowgram_encoder.to_dict(flowgram, True, request.user))


@require(None, ['flowgram_id'], ['edit_flowgram'])
def delete_flowgram(request, flowgram):
    log.action('delete_flowgram %s' % flowgram.id)
    flowgram.delete()


@require('GET',
         ['enc=json', 'flowgram_id', 'page_size:int', 'page_number:int=-1', 'last_comment_id='])
def get_comments_paginated(request, enc, flowgram, page_size, page_number, last_comment_id):
    """Gets the comments for a Flowgram, paginated.  Optional parameters: page_number (starts at 1)
    and last_comment_id (the ID of the last comment already received for this Flowgram) are
    mutually exclusive."""
    
    comments = models.Comment.objects.filter(flowgram=flowgram).order_by('-created_at')
    num_comments = comments.count()

    if page_number >= 0:
        # If page_number is specifed (where page 1 is the earliest comments).
         
        comments = comments[min(0, num_comments - page_size * page_number):\
                            num_comments - page_size * (page_number - 1)]
    elif last_comment_id:
        # If last_comment_id is specified, returning only comments after the last comment.
        
        last_comment = comments.get(id=last_comment_id)
        comments = comments.filter(created_at__gt=last_comment.created_at)[:page_size]
    else:
        # If neither page_number or last_comment_id are specified, return the most recent page.

        comments = comments[:page_size]
        
    return data_response.create(
        enc,
        'ok',
        {
            'num_comments': num_comments,
            'comments': [encode.comment.to_dict(comment) for comment in comments]
        })


@require('GET', ['flowgram_id', 'working_flowgram:boolean=false'], ['view_flowgram'])
def get_fg(request, flowgram, working_flowgram):
    if working_flowgram:
        controller.set_working_flowgram(request.user, flowgram)
        
    return data_response.create(request.GET.get('enc', 'json'),
                                'ok',
                                encode.flowgram_encoder.to_dict(flowgram, True, request.user))


def get_working_fg(request):
    enc = helpers.get(request, 'enc', 'json')
    if not request.user.is_authenticated():
        return error_response.create(enc, 'Login required')
    return data_response.create(enc, 'ok', controller.get_working_flowgram(request.user)[0].id)


@require('POST', ['flowgram_id', 'title', 'enc=json'], ['view_flowgram'])
def save_as(request, flowgram, title, enc):
    new_fg = controller.copy_flowgram(request.user, flowgram)
    new_fg.title = title
    new_fg.save()
    
    return data_response.create(enc, 'ok', new_fg.id)


@require('POST',
         ['flowgram_id', 'description', 'public:boolean', 'title', 'sent_owner_done_email:boolean', 
              'background_audio_loop:boolean', 'background_audio_volume:int', 'tags:csl='])
def save_flowgram(request, flowgram, description, public, title, sent_owner_done_email, \
                      background_audio_loop, background_audio_volume, tags):
    if permissions.can_edit(request.user, flowgram):
        flowgram.description = description
        if public and not flowgram.public:
            flowgram.published_at = datetime.now()
        flowgram.public = public
        flowgram.title = title
        flowgram.sent_owner_done_email = sent_owner_done_email
        flowgram.background_audio_loop = background_audio_loop
        flowgram.background_audio_volume = background_audio_volume
        flowgram.save()
    
    if localsettings.FEATURE['subscriptions_fw']:
        data = {'fg_id': flowgram.id,
                'eventCode': 'FG_MADE'}
        data['active'] = 'make_active' if public else 'make_inactive'
        controller.store_fgmade_event(data)

    if request.POST.has_key('tags'):
        controller.set_tags(request.user, flowgram, tags)
        if localsettings.FEATURE['subscriptions_fw']:
            controller.store_fgtagged_event({'current_user': request.user,
                                            'fg_id': flowgram.id,
                                            'eventCode': 'FG_TAGGED'})


@require('POST', ['flowgram_id', 'rating:float'], ['view_flowgram'])
def save_rating(request, flowgram, rating):
    rating = int(rating * 2)

    try:
        existingRating = models.Rating.objects.get(user=request.user, flowgram=flowgram)
        flowgram.total_rating += rating - existingRating.value
        existingRating.value = rating
        existingRating.save()
    except models.Rating.DoesNotExist:
        models.Rating.objects.create(user=request.user, flowgram=flowgram, value=rating)
        flowgram.total_rating += rating
        flowgram.num_ratings += 1

    # TODO(westphal): Don't calculate this on-the-fly, use a service to do this in the background.
    #                 This will be important if there's a bunch of DB servers.
    # Divide by zero should not be possible because num_ratings is incremented prior to this
    # operation.
    flowgram.avg_rating = float(flowgram.total_rating) / flowgram.num_ratings / 2
    flowgram.save()


@require('POST', ['flowgram_id'], ['edit_flowgram'])
def set_working_flowgram(request, flowgram):
    controller.set_working_flowgram(request.user, flowgram)
