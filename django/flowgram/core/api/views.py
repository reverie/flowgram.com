import re

from django.contrib.auth import models as auth_models
from django.http import HttpResponseRedirect

from flowgram import localsettings
from flowgram.core import avatar, controller, encode, fix, helpers, log, models
from flowgram.core.api.auth import ajax_login
from flowgram.core.api.audio import add_audio_fms, clear_audio, delete_audio, \
                                        remove_background_audio, update_audio
from flowgram.core.api.client import download_for_offline, get_app_init_data, \
                                         send_editbar_done_email
from flowgram.core.api.favorites import add_favorite, remove_favorite
from flowgram.core.api.flowgrams import can_edit_fg, create_flowgram, delete_flowgram, \
                                            get_comments_paginated, get_fg, get_working_fg, \
                                            save_as, save_flowgram, save_rating, \
                                            set_working_flowgram
from flowgram.core.api.highlights import clear_highlights, delete_highlight, get_highlighted_page, \
                                             set_page, update_highlight
from flowgram.core.api.importers import file_upload, import_rss
from flowgram.core.api.more_flowgrams import get_favorite_fgs_paginated, get_fgs_paginated, \
                                                 get_more_fgs_paginated
from flowgram.core.api.pages import add_page, get_page, move_pages, remove_pages, \
                                        save_custom_page, save_page
from flowgram.core.api.stats import record_stat, record_bulk_stats
from flowgram.core.api.status_check import check_all
from flowgram.core.api.subscriptions import create_subscription, remove_subscription
from flowgram.core.api.thumbnails import get_fg_thumb_by_dims, get_thumb, get_thumb_by_dims
from flowgram.core.decorators import internal
from flowgram.core.require import require
from flowgram.core.response import data_response


GALLERY_ME_COM_REGEX = re.compile(r'http://gallery\.me\.com/(.*)#(.*)/([^&]*).*')

ANONYMOUS_USERNAME = 'AnonymousUser'
ANONYMOUS_USER_OBJECT = auth_models.User.objects.get_or_create(username=ANONYMOUS_USERNAME)[0]


@require('POST', ['enc=json', 'url=', 'email=', 'sysinfo=', 'comments='])
def add_feedback(request, enc, url, email, sysinfo, comments):
    from flowgram.core.mail import announce_feedback

    feedback = models.Feedback.objects.create(url=url, email=email, sys_info=sysinfo, comments=comments)
    announce_feedback(feedback)

    return data_response.create(enc, 'ok', {})


@require('POST', ['flowgram_id', 'display_in_newest:boolean'], ['staff'])
def admin_display_in_newest(request, flowgram, display_in_newest):
    flowgram.display_in_newest = display_in_newest
    flowgram.save()
    log.action('admin_display_in_newest changed to %s on flowgram.id=%s' % (flowgram.id, display_in_newest))


@require('POST', ['enc=json', 'flowgram_id', 'use_highlight_popups:boolean', 'request_email='])
def export_to_video(request, enc, flowgram, use_highlight_popups, request_email):
    etvr = models.ExportToVideoRequest.objects.create(
        flowgram=flowgram,
        use_highlight_popups=use_highlight_popups,
        request_user=request.user if request.user.is_authenticated() else ANONYMOUS_USER_OBJECT,
        request_email=request_email)
    return data_response.create(enc, 'ok', etvr.id)


@require('GET', ['size:int', 'flowgram_id'], ['view_flowgram'])
def get_fg_avatar(request, size, flowgram):
    profile = flowgram.owner.get_profile()
    return HttpResponseRedirect(avatar.get_url(profile, size))


@require('POST', ['invitees', 'personal_message='], ['login'])
def invite(request, invitees, personal_message):
    from flowgram.core.mail import send_invitations

    invitees = helpers.get_email_addresses_from_comma_separated_string(invitees)

    send_invitations(request.user, invitees, personal_message)

    controller.record_stat(request, 'add_invite_website', '0', '%d invitees' % len(invitees))


# TODO(westphal): This seems to not be used, but verify and delete if possible.
@require('POST', ['error_message'])
def log_error(request, error_message):
    log.error('[web] ' + error_message, request)


# TODO(westphal): Make the read and write combination of status_code transactional.
@internal
@require('POST', ['addpagerequest_id', 'html', 'url'])
def post_queue_add_page(request, addpagerequest_id, html, url):
    """Called by the server-side renderer to finish adding a page."""

    addPageRequest = models.AddPageRequest.objects.get(id=addpagerequest_id)

    # If this page was already completed, don't add it again -- there's a possibility that multiple
    # threads are working on the same page at once.
    if addPageRequest.status_code == models.StatusCode.DONE:
        log.error("Multiple threads processed APR %s" % addPageRequest.id)
        return

    flowgram = addPageRequest.flowgram
    user = flowgram.owner
    title = helpers.get_title(request)

    # Modify the HTML to add base tag etc.
    (html, url) = fix.process_page(html, url)
        
    # Create and save the page:
    page = addPageRequest.page
    page.title = title
    page.save()
    html = helpers.cache_css_files(page, html)
    page = controller.create_page_to_flowgram(flowgram, page, html, do_make_thumbnail=False,
                                                  set_position=False)
    
    # Updating the status code and page
    addPageRequest.status_code = models.StatusCode.DONE
    
    controller.set_page_hl_contents(page, html)
    
    addPageRequest.save()
        
    log.action('post_queue_add_page %s to %s for %s' % (page.id, flowgram.id, user.username))


@require('POST', ['enc=json', 'url', 'flowgram_id'], ['edit_flowgram'])
def queue_add_url(request, enc, url, flowgram):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    match = GALLERY_ME_COM_REGEX.match(url)
    if match:
        (username, gallery, file) = match.groups(0)

        title = 'MobileMe Gallery - %s' % file
        link = 'http://gallery.me.com/%s/%s/%s/web.jpg' % (username, gallery, file)
        
        html = '<html><head><title>%s</title><style>@import url("/media/css/photo_importers.css");</style></head><body><img src="%s" /></body></html>' % \
            (title, link)
    
        page = models.Page.objects.create(title=title, source_url=link)
        page = controller.create_page_to_flowgram(flowgram, page, html)
        
        aprId = '-1'
    else:
        page = models.Page.objects.create(flowgram=flowgram,
                                          owner=request.user,
                                          source_url=url,
                                          position=controller.get_next_position(flowgram))
        
        aprId = models.AddPageRequest.objects.create(flowgram=flowgram, url=url, page=page).id
        
    return data_response.create(enc, 'ok', {'ready': 0,
                                            'error': 0,
                                            'results': encode.page.to_dict(page),
                                            'request_id': aprId})


@require('POST', ['enc=json', 'flowgram_id', 'recipients', 'talking_email:int=0', 'message=', \
                      'from_name=', 'from_email=', 'cc_self:boolean=false', 'subject='])
def share(request, enc, flowgram, recipients, talking_email, message, from_name, from_email, \
              cc_self, subject):
    from flowgram.core.mail import toolbar_share

    toolbar_share(request, flowgram, recipients, message, from_name, from_email, cc_self, subject, \
                      'talking_email' if talking_email else 'share')


# DEPRECATE ASAP------------------------------------------------------------------------------------


# Deprecate and remove asap.
@require('POST', ['flowgram_id', 'public:boolean'], ['edit_flowgram'])
def change_privacy(request, flowgram, public):
    flowgram.public = public
    flowgram.save()

    if localsettings.FEATURE['subscriptions_fw']:
        data = {'fg_id': flowgram.id,
                'eventCode': 'FG_MADE'}
        data['active'] = 'make_active' if public else 'make_inactive'

        controller.store_fgmade_event(data)


# Deprecate and remove asap.
@require('POST', ['enc=json', 'flowgram_id', 'desc'], ['edit_flowgram'])
def set_fg_desc(request, flowgram, desc):
    log.action('set_fg_desc from %s to %s on %s for %s' % (flowgram.description, desc, flowgram.id, request.user.username))
    flowgram.description = desc
    flowgram.save()


# Deprecate and remove asap.
@require('POST', ['enc=json', 'flowgram_id', 'title'], ['edit_flowgram'])
def set_fg_title(request, enc, flowgram, title):
    log.action('set_fg_title from %s to %s on %s for %s' % (flowgram.title, title, flowgram.id, request.user.username))
    flowgram.title = title
    flowgram.save()
