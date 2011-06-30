def create(object):
    from django.http import HttpResponse
    from django.template.loader import render_to_string

    return HttpResponse(render_to_string(object.get('template', '500.html'), object),
                        mimetype='text/html')
