import flickrapi

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from flowgram import localsettings


# url callbacks

@login_required
def callback(request):
    f = flickrapi.FlickrAPI(localsettings.FLICKR_API_KEY,
           localsettings.FLICKR_API_SECRET, store_token=False)

    frob = request.GET['frob']
    flickr_token = f.get_token(frob)
    request.session['flickr_token'] = flickr_token

    response = HttpResponse("<script>window.close();</script>")

    response.set_cookie("have_flickr_auth_token", "1")
    return response

