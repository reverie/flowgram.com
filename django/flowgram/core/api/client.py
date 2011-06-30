from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

from flowgram import localsettings
from flowgram.core import avatar, controller, encode, helpers, log, models
from flowgram.core.compoundfile import CompoundFile
from flowgram.core.require import require
from flowgram.core.response import data_response


NOT_FOUND = 999999


# TODO(westphal): This operation is going to be pretty expensive, so we need to come up with a good
#                 solution for this in the longer-term.
@require('GET', ['enc=html', 'flowgram_id'])
def download_for_offline(request, enc, flowgram):
    compound_file = CompoundFile()
    
    # Adding the Flowgram metadata.
    flowgram_json = str(simplejson.dumps(encode.flowgram_encoder.to_dict(flowgram, True, None),
                                         ensure_ascii=True).encode('utf-8'))
    compound_file.add('flowgram_meta.json', flowgram_json)

    # Adding background audio if any.
    if flowgram.background_audio:
        (audio_content, content_type) = helpers.download_url(
            'http://%s/%s.flv' % (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_AUDIO],
                                  flowgram.background_audio.id),
            use_unicode=False)
        compound_file.add('audio_%s.flv' % flowgram.background_audio.id, audio_content)

    # Adding the avatar.
    try:
        (avatar_image, content_type) = helpers.download_url(
            'http://%s/api/getfgavatar-32/%s/' % (localsettings.MASTER_DOMAIN_NAME, flowgram.id),
            use_unicode=False)
        compound_file.add('avatar', avatar_image)
    except helpers.DownloadException:
        pass

    images = {}

    # Adding data for each page.
    pages = models.Page.objects.filter(flowgram=flowgram)
    for page in pages:
        # Adding the page's HTML.
        page_html = str(controller.page_contents(page).encode('utf-8'))
        page_html = process_html_for_image_downloading(page_html, images)
        page_html = process_css_for_image_downloading(page_html, images)
        compound_file.add('page_%s.html' % page.id, page_html)

        # Adding the page's thumbnail image.
        try:
            (thumbnail_data, content_type) = helpers.download_url(
                'http://%s/%s_150_100.jpg' % (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_THUMB],
                                              page.id),
                use_unicode=False)
            compound_file.add('thumb_%s.jpg' % page.id, thumbnail_data)
        except helpers.DownloadException:
            pass

        # Adding the page's audio file(s).
        audio = models.Audio.objects.filter(page=page)
        for audio_item in audio:
            (audio_content, content_type) = helpers.download_url(
                'http://%s/%s.flv' % (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_AUDIO],
                                      audio_item.id),
                use_unicode=False)
            compound_file.add('audio_%s.flv' % audio_item.id, audio_content)

        # Adding the page's CSS file(s).
        css = models.GetCssRequest.objects.filter(page=page)
        for css_item in css:
            (css_content, content_type) = helpers.download_url(
                'http://%s/css/%s/' % (localsettings.MASTER_DOMAIN_NAME, css_item.id),
                use_unicode=False)
            css_content = process_css_for_image_downloading(css_content, images)
            compound_file.add('css_%s.css' % css_item.id, css_content)

    for filename in images.keys():
        compound_file.add(filename, images[filename])

    response = HttpResponse(compound_file.to_string(), 'application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s.flowgram"' % \
                                          (flowgram.title or 'untitled')
    #response = HttpResponse(compound_file.to_string(), 'text/plain')
    return response


def find_first(content, terms, offset):
    first_index = NOT_FOUND
    first_term = None

    for term in terms:
        index_of_term = content.find(term, offset)
        if index_of_term >= 0 and index_of_term < first_index:
            first_index = index_of_term
            first_term = term

    return (first_index, first_term)


@require(None, ['enc=json'])
def get_app_init_data(request, enc):
    from flowgram.core.helpers import get_post_token_value

    if request.user.is_authenticated():
        return data_response.create(
            enc,
            'ok',
            {
                'username': request.user.username,
                'post_token': get_post_token_value(request),
                'session_id': request.COOKIES[settings.SESSION_COOKIE_NAME]
            })
    else:
        set_cookie_needed = False
        
        if not request.COOKIES.has_key(settings.SESSION_COOKIE_NAME):
            request.session.save()
            request.COOKIES[settings.SESSION_COOKIE_NAME] = request.session.session_key
            set_cookie_needed = True

        response = data_response.create(
            enc,
            'ok',
            {
                'username': '',
                'post_token': get_post_token_value(request),
            })

        if set_cookie_needed:
            response.set_cookie(settings.SESSION_COOKIE_NAME,
                                request.session.session_key,
                                max_age=None,
                                expires=None,
                                domain=settings.SESSION_COOKIE_DOMAIN,
                                path=settings.SESSION_COOKIE_PATH,
                                secure=settings.SESSION_COOKIE_SECURE or None)

        return response


def get_extension_from_content_type(content_type):
    if content_type == 'image/jpeg':
        return 'jpg'
    elif content_type == 'image/gif':
        return 'gif'
    elif content_type == 'image/png':
        return 'png'
    return ''


def process_css_for_image_downloading(css, images):
    replace = []

    search_css = css.lower()
    offset = 0
    
    index_of_image_property = find_first(search_css, ['background', 'list-style'], offset)[0]
    while index_of_image_property < NOT_FOUND:
        offset = index_of_image_property + 1

        (index_of_next_part, next_part_type) = \
            find_first(search_css, ['url(', ';', '}'], index_of_image_property)
        if next_part_type == 'url(':
            index_of_closing_paren = search_css.find(')', index_of_next_part)
            src = css[index_of_next_part + 4:index_of_closing_paren]
            if src[0] == '"' or src[0] == "'":
                src = src[1:-1]

            if src not in images:
                skip = False
                try:
                    (image_data, content_type) = helpers.download_url(src, use_unicode=False)
                    skip = type(image_data) == type(u'')
                except helpers.DownloadException:
                    skip = True

                if not skip:
                    extension = get_extension_from_content_type(content_type)
                    filename = 'image_%d.%s' % (len(images.keys()), extension)

                    replace.append((src, filename))
                    images[filename] = image_data

        index_of_image_property = find_first(search_css, ['background', 'list-style'], offset)[0]

    for r in replace:
        css = css.replace(r[0], '{{fg_placeholder_%s}}' % r[1])

    return css


def process_html_for_image_downloading(html, images):
    replace = []

    # This assumes that a base URL tag will always be present -- it should, because we put one in.
    base_url = helpers.determine_base_url('/', html)

    search_html = html.lower()
    offset = 0
    index_of_image_tag = find_first(search_html, ['<img', '<input'], offset)[0]
    while index_of_image_tag < NOT_FOUND:
        offset = index_of_image_tag + 1

        (index_of_next_part, next_part_type) = find_first(search_html, ['>', 'src="'], index_of_image_tag)
        if next_part_type == 'src="':
            index_of_closing_quotes = search_html.find('"', index_of_next_part + 5)
            src = html[index_of_next_part + 5:index_of_closing_quotes]

            download_src = helpers.get_absolute_url(src, base_url)
            if download_src not in images:
                skip = False
                try:
                    (image_data, content_type) = helpers.download_url(download_src, use_unicode=False)
                    skip = type(image_data) == type(u'')
                except helpers.DownloadException:
                    skip = True

                if not skip:
                    extension = get_extension_from_content_type(content_type)
                    filename = 'image_%d.%s' % (len(images.keys()), extension)

                    replace.append((src, filename))
                    images[filename] = image_data

        index_of_image_tag = find_first(search_html, ['<img', '<input'], offset)[0]

    for r in replace:
        html = html.replace(r[0], '{{fg_placeholder_%s}}' % r[1])

    return html


@require('POST', ['enc=json', 'flowgram_id'])
def send_editbar_done_email(request, enc, flowgram):
    from flowgram.core.mail import toolbar_done

    toolbar_done(flowgram, request.user)
    log.action('flowgram %s done by %s ' % (flowgram.id, request.user.username))
    return data_response.create(
        enc,
        'ok',
        {
            'user': request.user.username,
            'flowgram': flowgram.title,
        })
