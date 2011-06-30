##
# Copyright Flowgram Inc. 2007, all rights reserved.
#
# @author Brian Westphal, Andrew Badr
##

from django.utils.html import escape
from flowgram import localsettings

def url_for_page_thumbnail(page_id):
    """Gets the URL for a flowgram page thumbnail."""
    return 'http://%s/%s_150_100.jpg' % \
               (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_THUMB], page_id)
    #return "".join(["/api/getthumb/", str(page_id), "/"])

def url_for_playing_flowgram(flowgram_id):
    """Gets the URL for a playing a flowgram."""
    return '/p/' + str(flowgram_id)

def url_for_flowgram_details(flowgram):
    return '/fg/' + flowgram.id

def url_for_user(user):
    return '/' + user.username

def html_link(url, text):
    return '<a href="%s">%s</a>' % (url, escape(text))

def link_to_user(user):
    return html_link(url_for_user(user), user.username)

def link_to_flowgram_details(fg):
    return html_link(url_for_flowgram_details(fg), fg.title)
