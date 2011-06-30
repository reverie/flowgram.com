from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from flowgram.core import controller, helpers, log, models
from flowgram.core.require import require


@require('POST', ['page_id', 'keep_zero_time_hightlights:boolean=false'], ['edit_page'])
def clear_highlights(request, page, keep_zero_time_hightlights):
    highlights = models.Highlight.objects.filter(page=page)
    if keep_zero_time_hightlights:
        highlights = highlights.exclude(time__lte=1000)
    highlights.delete()

    log.action('clear_highlights on page %s for %s' % (page.id, request.user.username))


@require('POST', ['page_id', 'name'], ['edit_page'])
def delete_highlight(request, page, name):
    get_object_or_404(models.Highlight, page=page, name=name).delete()
    helpers.set_modified(page.flowgram)


@require('GET', ['page_id'])
def get_highlighted_page(request, page):
    try:
        html = controller.page_hl_contents(page)
    except IOError:
        html = controller.page_contents(page)
    return HttpResponse(html)


@require('POST', ['page_id', 'html'], ['edit_page'])
def set_page(request, page, html):
    """Sets the highlighted HTML version of a Page."""
    controller.set_page_hl_contents(page, html)
    log.action('set_page on %s for %s' % (page.id, request.user.username)) 


@require('POST', ['page_id', 'name:int', 'time:int'], ['edit_page'])
def update_highlight(request, page, name, time):
    try:
        # Trying first to update an existing highlight.
        highlight = models.Highlight.objects.get(page=page, name=name)
        highlight.time = time
        highlight.save()
    except models.Highlight.DoesNotExist:
        # Creating a new highlight.
        models.Highlight.objects.create(page=page, name=name, time=time)

        # Updating the max highlight ID used value.
        page.max_highlight_id_used = max(page.max_highlight_id_used, name)
        page.save()

        helpers.set_modified(page.flowgram)
