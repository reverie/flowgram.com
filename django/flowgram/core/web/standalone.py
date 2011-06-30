from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from flowgram import localsettings
from flowgram.core import controller, encode, helpers, log, models, permissions, webhelpers
from flowgram.core.require import require


@require('GET', ['enc=json', 'directory_name', 'page_name=index'], ['authorized'])
def standalone_page(request, enc, directory_name, page_name):
    template_path = 'standalone/' + directory_name + '/' + page_name + '.html'
    return helpers.req_render_to_response(
        request,
        template_path,
        {
            
        })