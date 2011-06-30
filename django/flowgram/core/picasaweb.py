from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from flowgram import localsettings
from flowgram.core import log

import gdata.photos.service

gd_client = gdata.photos.service.PhotosService()

@login_required
def callback(request):
    picasaweb_token = request.GET['token']
    gd_client.auth_token = picasaweb_token
    gd_client.UpgradeToSessionToken()
    temp_token = str(gd_client.auth_token)
    picasaweb_token = temp_token[temp_token.index('token=')+6:]
    
    request.session['picasaweb_token'] = picasaweb_token
    
    response = HttpResponse("<script type=\"text/javascript\">window.close();</script>")
    response.set_cookie("have_picasaweb_auth_token", "1")
    return response