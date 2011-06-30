"""Mostly deprecated. Some functions will move to api.py, then this will disappear."""
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from flowgram.core.models import UserProfile, Flowgram, Comment, Tag
from flowgram.core.models import View
from flowgram.localsettings import FEATURE

def login(request):
    from django.contrib.auth import authenticate
    from django.contrib.auth import login as django_login
    try:
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
    except:
        return HttpResponse("ERROR: username/password POST variables missing")
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            django_login(request, user)
            return HttpResponse("OK")
            #return HttpResponse("OK: "+request.COOKIES.get('sessionid', ''))
        else:
            return HttpResponse("ERROR: account is disabled")
    else:
        return HttpResponse("ERROR: username/password combination incorrect")

# method = 'F0D' means Flex, zero-download player.
def record_view(flowgram, user, method):
	from flowgram.core import controller
	if user.is_anonymous():
		View.objects.create(flowgram_id=flowgram.id, method=method)
	else:
		View.objects.create(flowgram_id=flowgram.id, user_id=user.id, method=method)
		
	flowgram.views += 1
	flowgram.save(invalidate_cache=False)

def register_view(request):
    flowgram_id = request.POST.get("FGID", "")
    flowgram = get_object_or_404(Flowgram, pk=flowgram_id)
    method = request.POST.get("method", "")
    record_view(flowgram, request.user, method)

    return HttpResponse('OK')
