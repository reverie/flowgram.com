from flowgram.facebook import minifb

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from flowgram import localsettings
from flowgram.core import helpers, controller, log
from flowgram.core.models import *

FACEBOOK_API_SECRET_MINIFB = minifb.FacebookSecret(localsettings.FACEBOOK_API_SECRET)

# functions

def login_url():
    return "http://www.facebook.com/login.php?api_key=%s&v=1.0" % localsettings.FACEBOOK_API_KEY

def require_auth(view):
    def protected_view(request, *args, **kwargs):
        if 'facebook_token' in request.session:
            facebook_token = request.session['facebook_token']
        else:
            facebook_token = None

        if not facebook_token:
            return HttpResponse("<script>top.location = \"%s\";</script>" % login_url())

        return view(request, *args, **kwargs)

    return protected_view

# url callbacks

@login_required
def callback(request):
    arguments = minifb.validate(FACEBOOK_API_SECRET_MINIFB, request.GET)
    auth_token = arguments["auth_token"]
    
    result = minifb.call("facebook.auth.getSession", localsettings.FACEBOOK_API_KEY, FACEBOOK_API_SECRET_MINIFB, auth_token=auth_token)
    facebook_token = result["session_key"]
    request.session['facebook_token'] = facebook_token

    response = HttpResponse("<script>window.close();</script>")

    response.set_cookie("have_facebook_auth_token", "1")
    
    return response

@require_auth
@login_required
def albums_import(request):
    facebook_token = request.session['facebook_token']
    
    try:
        albums = minifb.call("facebook.photos.getAlbums", localsettings.FACEBOOK_API_KEY, FACEBOOK_API_SECRET_MINIFB, session_key=facebook_token)
    except minifb.FacebookError, e:
        if e.error_code == 102:
            return HttpResponse("<script>top.location = \"%s\";</script>" % login_url())
        raise
    
    html = "<div id=\"status\"></div>";
    html += "<ul>";

    for album in albums:
        html += "<li>" \
                    "<a onclick=\"return importPhotos('/facebook/create_fg_from_aid/?aid=" + \
                        str(album["aid"]) + "', '" + str(album["aid"]) + "');\" href=\"javascript:void(0);\">" + \
                        album["name"] + \
                    "</a>" \
                    "<span class=\"photoImportStatus\" id=\"status_" + str(album["aid"]) + "\"></span>" \
                "</li>"

    html += "</ul>";
    
    response = helpers.req_render_to_response(request, 'facebook/albums.html', {'html' : html})
    return response

@require_auth
@login_required
def create_fg_from_aid(request):
    facebook_token = request.session['facebook_token']
    
    try:
        photos = minifb.call("facebook.photos.get", localsettings.FACEBOOK_API_KEY, FACEBOOK_API_SECRET_MINIFB, session_key=facebook_token, aid=request.GET["aid"])
    except minifb.FacebookError, e:
        if e.error_code == 102:
            return HttpResponse("<script>top.location = \"%s\";</script>" % login_url())
        raise
    
    fg, new = controller.get_working_flowgram(request.user)
    
    for photo in photos:
        title = photo["caption"]
        link = photo["src_big"]
        
        if title == "":
            title = "photo"
        
        html = "<html><head><title>%s</title>" \
                    "<style>@import url(\"/media/css/photo_importers.css\");</style>" \
                "</head><body><img src=\"%s\" /></body></html>" % (title, link)

        page = Page(title=title, source_url=link)
        page = controller.create_page_to_flowgram(fg, page, html)

    return HttpResponse("")
