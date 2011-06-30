from django.http import Http404, HttpResponse
from django.template.loader import render_to_string

from flowgram import localsettings
from flowgram.core import controller, encode, helpers, log, models
from flowgram.core.controllers import pages
from flowgram.core.require import require
from flowgram.core.response import data_response, error_response


@require('POST', ['url', 'html'], ['login'])
def add_page(request, url, html):
    if not url.startswith('http://') and not url.startswith('https://'):
        return helpers.redirect(url, 'This type of page cannot be added to a flowgram.')

    user = request.user
    title = helpers.get_title(request)

    (flowgram, page) = pages.add_page(user, url, html, title)

    log.action('add_page created page with ID %s for Flowgram with ID %s by user %s' % \
                   (page.id, flowgram.id, user.username))
    return helpers.redirect(url, 'Page added to your Flowgram "%s"' % flowgram.title)


@require('GET', ['page_id'], ['view_page'])
def get_page(request, page):
    # If the page was deleted.
    if not page.flowgram_id:
        raise Http404
    
    return HttpResponse(controller.page_contents(page))


@require('POST', ['flowgram_id', 'page_ids:csl', 'to_index:int'], ['edit_flowgram'])
def move_pages(request, flowgram, move_page_ids, to_index):
    pages = models.Page.objects.filter(flowgram=flowgram).order_by('position')
    all_page_ids = [page.id for page in pages]

    # Creating the sorted array of page ids.
    sorted_page_ids = []
    index = 0
    appended = False
    for page_id in all_page_ids:
        if index == to_index:
            for move_page_id in move_page_ids:
                sorted_page_ids.append(move_page_id)
            appended = True
        
        if not page_id in move_page_ids:
            sorted_page_ids.append(page_id)
        
        index += 1

    if not appended:
        for move_page_id in move_page_ids:
            sorted_page_ids.append(move_page_id)

    # Updating the positions for all pages.
    index = 0
    for page_id in sorted_page_ids:
        page = pages[all_page_ids.index(page_id)]
        if page.position != index:
            page.position = index
            page.save()
        index += 1


@require('POST', ['flowgram_id', 'page_ids:csl'], ['edit_flowgram'])
def remove_pages(request, flowgram, page_ids):
    for page_id in page_ids:
        page = models.Page.objects.get(id=page_id)
        page.flowgram = None
        page.save()


@require('POST', ['enc=json', 'flowgram_id', 'content'], ['edit_flowgram'])
def save_custom_page(request, enc, flowgram, content):
    page_id = request.POST.get('page_id', '')
    page = models.Page.objects.get(id=page_id) if page_id else None

    user = flowgram.owner

    if page:
        # If editing an existing page.

        # Checking to make sure the page belongs to the specified Flowgram.
        if not page.flowgram == flowgram:
            return error_response.create(
                enc,
                'The specified page does not belong to the specified Flowgram.')

        html = render_to_string('blankpages/view.html', {'html': content,
                                                         'user': user})
        controller.set_page_contents(page, html, sethl=True)

        # This try..except block is used for legacy support (previous versions did not save a
        # separate CustomPage object).
        try:
            custom_page = models.CustomPage.objects.get(page=page)
            custom_page.content = content
            custom_page.save()
        except models.CustomPage.DoesNotExist:
            models.CustomPage.objects.create(page=page, content=content)

        controller.make_thumbnail(page)

        return data_response.create(enc, 'ok', encode.page.to_dict(page))
    else:
        # If creating a new page.

        html = render_to_string('blankpages/view.html', {'html': content,
                                                         'user': user})
        
        title = "%s's custom Flowgram page" % user
        page = models.Page.objects.create(title=title, source_url='')
        page = controller.create_page_to_flowgram(flowgram, page, html)

        page.source_url = '%sapi/getpage/%s/' % (localsettings.my_URL_BASE, page.id)
        page.is_custom = True
        page.save()

        models.CustomPage.objects.create(page=page, content=content)

        return data_response.create(enc, 'ok', encode.page.to_dict(page))


@require('POST',
         ['page_id', 'description', 'duration:int', 'fade_in:boolean', 'fade_out:boolean',
              'max_highlight_id_used:int', 'title', 'transition_type:int'],
         ['edit_page'])
def save_page(request, page, description, duration, fade_in, fade_out, max_highlight_id_used, title, transition_type):
    page.description = description
    page.duration = duration
    page.fade_in = fade_in
    page.fade_out = fade_out
    page.max_highlight_id_used = max_highlight_id_used
    page.title = title
    page.transition_type = transition_type
    page.save()
