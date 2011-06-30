def create(object):
    from django.http import HttpResponse
    from django.utils import simplejson

    return HttpResponse(simplejson.dumps(object, ensure_ascii=False), mimetype='text/javascript')
