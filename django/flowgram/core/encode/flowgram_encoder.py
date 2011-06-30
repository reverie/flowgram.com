def to_dict(flowgram, deep=True, user=None):
    from flowgram.core import encode, helpers, models, permissions

    user_rating = -1
    if user and user.is_authenticated():
        try:
            user_rating = float(models.Rating.objects.get(user=user, flowgram=flowgram).value) / 2
        except models.Rating.DoesNotExist:
            pass

    output = {
        'id': flowgram.id,

        'avg_rating': flowgram.avg_rating,
        'background_audio': encode.audio.to_dict(flowgram.background_audio) \
                                if flowgram.background_audio \
                                else None,
        'background_audio_loop': flowgram.background_audio_loop,
        'background_audio_volume': flowgram.background_audio_volume,
        'can_edit': permissions.can_edit(user, flowgram) \
                        if user and user.is_authenticated() \
                        else False,
        'description':flowgram.description,
        'num_comments': models.Comment.objects.filter(flowgram=flowgram).count(),
        'num_ratings': flowgram.num_ratings,
        'num_views': flowgram.views,
        'owner_name': helpers.get_display_name(flowgram.owner),
        'owner_url': str(flowgram.owner.get_profile().url()),
        'owner_username': flowgram.owner.username,
        'public':flowgram.public,
        'sent_owner_done_email': flowgram.sent_owner_done_email,
        'tag_list': sorted([tag.name for tag in models.Tag.objects.filter(flowgram=flowgram)]),
        'title':flowgram.title,
        'user_rating': user_rating,
    }
    
    pages = models.Page.objects.filter(flowgram=flowgram).order_by('position')

    if deep:
        output['pages'] = [encode.page.to_dict(page) for page in pages]
    else:
        output['pages'] = [{'id': page.id, 'duration': page.duration} for page in pages]

    return output
