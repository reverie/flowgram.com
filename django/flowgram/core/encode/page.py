def to_dict(page, deep=True):
    from flowgram import urlbuilder
    from flowgram.core import controller, encode, models

    audio = models.Audio.objects.filter(page=page)

    output = {
        'id':page.id,

        'description':page.description,
        'duration':page.duration or 0,
        'fade_in': bool(page.fade_in),
        'fade_out': bool(page.fade_out),
        'has_audio': bool(audio.count()),
        'is_custom': bool(page.is_custom),
        'max_highlight_id_used': page.max_highlight_id_used,
        'position': page.position,
        'processing_status': page.get_loading_status(),
        'source_url': page.source_url,
        'thumb_ready': bool(page.thumb_path),
        'thumb_url': urlbuilder.url_for_page_thumbnail(page.id),
        'title': page.title,
        'transition_type': page.transition_type,

        # Returning the flowgram_title if available because adding a page can sometimes change the
        # title of a Flowgram, (i.e. if there was no previous title).
        'flowgram_title': page.flowgram and page.flowgram.title or controller.DEFAULT_FG_TITLE,
    }
    
    if deep:
        output['audio_list'] = [encode.audio.to_dict(audio_item) for audio_item in audio]

        highlights = models.Highlight.objects.filter(page=page).order_by('-time')
        output['highlight_list'] = [encode.highlight.to_dict(hl) for hl in highlights]

        if page.is_custom:
            # This try..except block is used for legacy support (previous versions did not save a
            # separate CustomPage object).
            try:
                output['content'] = models.CustomPage.objects.get(page=page).content
            except models.CustomPage.DoesNotExist:
                # TODO(westphal): Add support for extracting legacy content information.
                output['content'] = ''

    return output
