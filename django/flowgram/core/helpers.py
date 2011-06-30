from datetime import datetime
import sys, cgi, re

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from flowgram import localsettings
from flowgram.core.response import data_response, error_response

DEFAULT_UA = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'

SORT_CRITERION_IO_MAP = {'modified': '-modified_at',
                         'popular': '-views',
                         'title': 'title',
                         'author': 'owner'}

class DownloadException(Exception): 
    pass

def convert_sort_criterion(input_criterion, default):
    return SORT_CRITERION_IO_MAP.get(input_criterion, default)


def delete_blank_flowgrams(flowgrams):
    from flowgram.core import controller, models

    for flowgram in flowgrams:
        if flowgram.title==controller.DEFAULT_FG_TITLE and \
               flowgram.description==controller.DEFAULT_FG_DESCRIPTION:
            num_pages = models.Page.objects.filter(flowgram=flowgram).count()
            num_comments = models.Comment.objects.filter(flowgram=flowgram).count()
            if not (num_pages or num_comments):
                flowgram.delete()


def get(request, name, default_value=None):
    method_args = request_or_object.GET \
        if request_or_object.method == 'GET' \
        else request_or_object.POST
    return method_args.get(name, default_value)


def get_badge_view_level(num_flowgram_views):
    from flowgram import settings as fg_settings

    # Getting the highest level badge of "number of Flowgram views" achieved.
    for level in fg_settings.BADGE_VIEW_LEVELS:
        if num_flowgram_views > level:
            return str(level)

    return ''


def get_category_bestof_fgs():
    from flowgram.core import cached_sets, models
    
    return [(cached_sets.get_featured(category), models.feat_fullname[category]) \
                for category in models.FEATURED_CATEGORIES]


def get_display_name(user):
    return user.first_name or user.username
    

def get_post_token_value(request):
    from django.contrib.csrf.middleware import _make_token
    from flowgram.core import log
    
    try:
        session_id = request.COOKIES[settings.SESSION_COOKIE_NAME]
    except KeyError:
        log.critical("get_post_token found no sessionid for authenticated user %s" % request.user)
        return error_response.create(get(request, 'enc', 'json'), 'Session cookie required')

    return _make_token(session_id)


def get_title(request_or_object):
    from flowgram.core import controller

    try:
        # Trying a request type first.
        
        method_args = request_or_object.GET \
            if request_or_object.method == 'GET' \
            else request_or_object.POST

        title = method_args.get('title', controller.DEFAULT_PAGE_TITLE)
        return title.replace('\n', ' ').replace('\r', ' ')[:100]
    except:
        # Trying an object type (such as Flowgram or Page) if request fails.

        return request_or_object.title or controller.DEFAULT_PAGE_TITLE


def set_modified(model_object):
    model_object.modified_at = datetime.now()
    model_object.save()


def sort_flowgrams(flowgrams, sort_criterion):
    flowgrams.sort(lambda x, y: cmp(x.title, y.title))

    if sort_criterion == '-modified_at':
        flowgrams.sort(lambda x, y: cmp(x.modified_at, y.modified_at))
    elif sort_criterion == '-views':
        flowgrams.sort(lambda x, y: cmp(x.views, y.views))
    elif sort_criterion == 'owner':
        flowgrams.sort(lambda x, y: cmp(x.owner, y.owner))

    return flowgrams


def stackTrace():
    output = []
    depth = 1
    try:
        while True:
            output.append(sys._getframe(depth).f_code.co_name)
            depth += 1
    except:
        return " ".join(output)

emailPattern = re.compile('(?:"[^"]*"\s+)?<([^>]+)>')
def get_email_addresses_from_comma_separated_string(addresses):
    addresses = emailPattern.sub(r'\1', addresses)
    addresses = addresses.split(',')
    return [address.strip() for address in addresses]

def req_render_to_response(request, template, context={}):
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    rc = RequestContext(request)
    return render_to_response(template, context, context_instance=rc)

def go_back(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/you/'))

def add_good_message(request, text):
    msg = '<span class="success_message">'+text+'</span>'
    request.session.create_message(message=msg)

def add_bad_message(request, text):
    msg = '<span class="error_message">'+text+'</span>'
    request.session.create_message(message=msg)

def build_flat_xml_object(name, fields):
    from BeautifulSoup import BeautifulStoneSoup, NavigableString, Tag
    from django.utils.html import escape
    soup = BeautifulStoneSoup()
    obj = Tag(soup, name)
    soup.insert(0, obj)
    for name, value in fields:
        tag = Tag(soup, name)
        tag.insert(0, NavigableString(escape(value)))
        obj.insert(0, tag)
    return unicode(soup)

def render_comment_to_xml(comment):
    from django.utils import dateformat
    from django.conf import settings
    fields = []
    fields.append(("id", comment.id))
    fields.append(("username", comment.owner.username))
    fields.append(("avatar", comment.owner.get_profile().avatar_32()))
    fields.append(("created", dateformat.format(comment.created_at, settings.DATE_FORMAT)))
    fields.append(("bodytext", comment.text))
    return build_flat_xml_object("comment", fields)

def url_base(url):
    from urlparse import urlparse
    base = []
    parsed = urlparse(url)
    base.append(parsed[0])
    base.append('://')
    base.append(parsed[1])
    base.append(parsed[2][:parsed[2].rfind('/')+1])
    return ''.join(base)

def proxy_tail(url):
    from urlparse import urlparse
    tail = urlparse(url)[2]
    return tail[tail.find('/', 2)+1:]

# TODO(andrew): replace with regex
def ifind(s, sub):
    # not really case in-sensitive, just upper and lower
    lower = s.find(sub.lower())
    upper = s.find(sub.upper())
    if ((lower < upper) and (lower != -1)) or upper == -1:
        return lower
    return upper

def insert_in_head(html, string):
    """Inserts a given string at the beginning of html's HEAD tag"""
    # find the HTML tag or give up
    html_loc = ifind(html, '<html')
    has_html = html_loc != -1
    if not has_html: 
        return html
    # if there's no head tag, add it
    has_head = ifind(html, '<head') != -1
    if not has_head: 
        html_loc = ifind(html, '<html')
        html_tag_end = html.find('>', html_loc)+1
        html = html[:html_tag_end]+'<head></head>'+html[html_tag_end:]
    # finally, insert string
    head_loc = ifind(html, '<head')
    head_tag_end = html.find('>', head_loc)+1
    html = html[:head_tag_end]+string+html[head_tag_end:]
    return html



# _mkdir copied from the web (andrew)
import os
os.umask(0002) #so that on dreamhost our other accounts can access it
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        if tail:
            os.mkdir(newdir)
    
from flowgram.localsettings import my_URL_BASE
from django.template.loader import render_to_string


def redirect(next, msg=None):
    """An HTML document that alerts `msg`, then redirects to `next`. Used for quick-add response. 
    """
    meta_tag = '<meta http-equiv="REFRESH" content="0;url=%s">' % next
    if msg:
        msg = msg.replace("'", "\\'")
        return HttpResponse("<html><head>%s</head><body><script>alert('%s');</script></body></html>" % (meta_tag, msg))
    return HttpResponse("<html><head>%s</head><body></body></html>" % (meta_tag))


def is_down_for_maintenance(request):
    """Determines whether or not the site should be down for maintenance."""
    return localsettings.fg_DOWN_FOR_MAINTENANCE and \
           not request.META.get('REMOTE_ADDR', '') in localsettings.fg_INTERNAL_IPS


def download_url(url, fake_cookies=None, use_unicode=True):
    import urllib2
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', DEFAULT_UA)]
    
    if fake_cookies:
        opener.addheaders = [('Cookie', fake_cookies)]

    urlReader = None
    try:
        try:
            urlReader = opener.open(url)
        except (ValueError, urllib2.URLError):
            print("Failed attempt to load file: %s" % url)
            raise DownloadException
            
        # Handles redirects
        url = urlReader.geturl()

        # Checking the MIME type
        contentType = urlReader.info().get('content-type', '')

        return (html_from_urlopen(urlReader, use_unicode), contentType)
    finally:
        if urlReader:
            urlReader.close()
        opener.close()
        

enc_re = re.compile('<meta\s+http-equiv="content-type"\s+content="text\/html;\s*charset=([^"]+)">', re.I)
def html_from_urlopen(r, use_unicode=True):
    """
    Input: a response returned from urllib2.urlopen
    Output: the HTML as a correctly decoded unicode object
    """
    html = r.read()

    # Try using header info    
    if r.info().has_key('content-type'):
        ct = r.info().get('content-type')
        if ct:
            null, opts = cgi.parse_header(ct)
            enc = opts.get('charset')
            if enc:
                try:
                    return unicode(html, enc)
                except UnicodeDecodeError:
                    pass
    
    # Try using info from HTML
    match = enc_re.search(html)
    if match:
        enc = match.groups()[0]
        try:
            return unicode(html, enc)
        except UnicodeDecodeError:
            pass
                
    # Default            
    return unicode(html, "windows-1252", errors='replace') if use_unicode else html

googleDocIframePattern = re.compile(r'RawDocContents\?docID=([^&]*)[^"]*', re.I)
def check_for_google_docs_iframe(html, url):
    match = googleDocIframePattern.search(html)
    if match:
        base_url = determine_base_url(url, html)
        url = 'RawDocContents?docID=%s&justBody=false&revision=_latest&editMode=false&strip=true' % \
                  match.group(1)
        return ('%s%s' % (base_url, url), True)
    return (url, False)


def parts_from_url(url, html):
    base_url = determine_base_url(url, html)

    protocol = None
    domain = None
    path = None

    if url.find('//') >= 0:
        (protocol, url) = url.split('//', 1)
        if url.find('/') >= 0:
            (domain, path) = url.split('/', 1)
            path = '/' + path
        else:
            domain = url
    elif url.startswith('/'):
        path = url
    else:
        path = '/' + url

    base_protocol = None
    base_domain = None
    if base_url.find('//') >= 0:
        (base_protocol, base_url) = base_url.split('//', 1)
        if base_url.find('/') >= 0:
            base_domain = base_url.split('/', 1)[0]
        else:
            base_domain = base_url

    protocol = protocol or base_protocol
    domain = domain or base_domain

    return {'protocol': protocol,
            'domain': domain,
            'path': path}


def remove_brightcove_player(html):
    search_html = html.lower()
    index_of_viewer_param = html.find('admin.brightcove.com/viewer')
    if index_of_viewer_param < 0:
        return html

    index_of_prior_object_tag_start_index = search_html.rfind('<object', 0, index_of_viewer_param)
    index_of_prior_object_tag_end_index = search_html.rfind('</object', 0, index_of_viewer_param)
    index_of_next_object_tag_end_index = search_html.find('</object', index_of_viewer_param)
    if index_of_prior_object_tag_start_index >= 0 and index_of_prior_object_tag_end_index >= 0 and index_of_prior_object_tag_end_index > index_of_prior_object_tag_start_index:
        index_of_prior_object_tag_start_index = -1
        index_of_prior_object_tag_end_index = -1
    elif index_of_next_object_tag_end_index < 0:
        index_of_prior_object_tag_start_index = -1
        index_of_prior_object_tag_end_index = -1

    index_of_prior_embed_tag_start_index = search_html.rfind('<embed', 0, index_of_viewer_param)
    index_of_prior_embed_tag_end_index = search_html.rfind('</embed', 0, index_of_viewer_param)
    index_of_next_embed_tag_end_index = search_html.find('</embed', index_of_viewer_param)
    if index_of_prior_embed_tag_start_index >= 0 and index_of_prior_embed_tag_end_index >= 0 and index_of_prior_embed_tag_end_index > index_of_prior_embed_tag_start_index:
        index_of_prior_embed_tag_start_index = -1
        index_of_prior_object_tag_end_index = -1
    elif index_of_next_embed_tag_end_index < 0:
        index_of_prior_embed_tag_start_index = -1
        index_of_prior_object_tag_end_index = -1

    if index_of_prior_object_tag_start_index >= 0 and index_of_prior_embed_tag_start_index < 0 or index_of_prior_object_tag_start_index < index_of_prior_embed_tag_start_index:
        html = html[:index_of_prior_object_tag_start_index] + html[index_of_next_object_tag_end_index + 9:]
    elif index_of_prior_embed_tag_start_index >= 0 and index_of_prior_object_tag_start_index < 0 or index_of_prior_embed_tag_start_index < index_of_prior_object_tag_start_index:
        html = html[:index_of_prior_embed_tag_start_index] + html[index_of_next_embed_tag_end_index + 8:]

    return html


scriptTagPattern = re.compile('<script([^<]|<[^/]|</[^s]|</s[^c]|</sc[^r]|</scr[^i]|</scri[^p]|</scrip[^t]|</script[^>])*?</script>', re.I)
eventHandlerPattern = re.compile('on(mouse(down|up|over|out|move)|(un)?load|(dbl)?click|key(press|down|up))\s*=\s*("([^"]|\\[^])*?"|[^"> \t\n\r]*)', re.I)
def remove_script_tags(html,source_url=None):
    found_brightcove_reference = False

    last_index = 0
    search_html = html
    html = []
    for match in scriptTagPattern.finditer(search_html):
        match_string = match.group(0)
        html.append(search_html[last_index:match.start()])
        if match_string.find('id="fg_bookmarklet"') >= 0:
            html.append(match_string)
        elif source_url and match_string.find('brightcove') >= 0:
            found_brightcove_reference = True
            match_string = match_string.replace('window.location.pathname', '"%s"' % parts_from_url(source_url, search_html)['path'])
            html.append(match_string)
        last_index = match.end()
    html.append(search_html[last_index:])
    html = ''.join(html)

    html = eventHandlerPattern.sub('', html)

    if found_brightcove_reference:
        html = remove_brightcove_player(html)

    return html


def cache_css_files(page, html):
    base_url = determine_base_url(page.source_url, html)
    html = process_link_tags(page, html, base_url)
    html = process_style_tags(page, html, base_url)
    return html

hrefAttribPattern = re.compile('href\s*=\s*"([^"]*)"', re.I)

baseTagPattern = re.compile('<base[^>]+>', re.I)
def determine_base_url(base_url, html):
    last_slash_index = base_url.rfind('/')
    if last_slash_index >= 0:
        base_url = base_url[0:last_slash_index + 1]
    
    match_iter = baseTagPattern.finditer(html)
    for match in match_iter:
        tag = html[match.start():match.end()]
        hrefMatch = hrefAttribPattern.search(tag)
        if hrefMatch and hrefMatch.group(1) != "":
            base_url = hrefMatch.group(1)
            if not base_url.endswith("/"):
                base_url += "/"
    return base_url


def get_absolute_url(src, base_url):
    if src.startswith('/'):
        if src.startswith('//'):
            src = ('http:' if base_url.startswith('http://') else 'https:') + src
        else:
            url_domain = base_url[0:base_url.index("/", base_url.startswith("http://") and 7 or 8)]
            src = url_domain + src
    elif not src.startswith('http://') and not src.startswith('https://'):
        src = base_url + src

    return src


linkTagPattern = re.compile('<link([^/]|/[^>])*?(/>|>(\s*</link>)?)', re.I)
relAttribPattern = re.compile('rel\s*=\s*"([^"]*)"', re.I)
typeAttribPattern = re.compile('type\s*=\s*"([^"]*)"', re.I)
mediaAttribPattern = re.compile('media\s*=\s*"([^"]*)"', re.I)
def process_link_tags(page, html, base_url):
    from flowgram.core.models import GetCssRequest
    from flowgram.queueprocessors.getcssrequestprocessor import get_absolute_import_url
    output = []
    
    offset = 0
    match_iter = linkTagPattern.finditer(html)

    for match in match_iter:
        tag = html[match.start():match.end()]
        relMatch = relAttribPattern.search(tag)
        typeMatch = typeAttribPattern.search(tag)
        hrefMatch = hrefAttribPattern.search(tag)
        mediaMatch = mediaAttribPattern.search(tag)

        media_ok = True
        if mediaMatch and not mediaMatch.group(1).lower().count("screen"):
            media_ok = False

        if media_ok and (relMatch and relMatch.group(1).lower().count("stylesheet") or \
                typeMatch and typeMatch.group(1).lower().count("text/css") or \
                hrefMatch and hrefMatch.group(1).lower().endswith(".css")):
            # Calculating the absolute URL of the CSS file.
            import_url = unescape_html(get_absolute_import_url(hrefMatch.group(1), base_url))
            
            # Creating a request to fetch the linked CSS file.
            request = GetCssRequest.objects.create(url=import_url, page=page)

            output.append(html[offset:match.start()])
            output.append('<link rel="stylesheet" type="text/css" href="%s" />' % request.calculate_local_url())
            
            offset = match.end()
    
    output.append(html[offset:len(html)])

    return "".join(output)    
    
styleAttribPattern = re.compile('style\s*=\s*"([^"]*)"', re.I)
styleTagPattern = re.compile('<style([^<]|<[^/]|</[^s]|</s[^t]|</st[^y]|</sty[^l]|</styl[^e]|</style[^>])*?</style>', re.I)
def process_style_tags(page, html, base_url):
    from flowgram.queueprocessors.getcssrequestprocessor import process_css_file, process_expression

    # Processing style tags.
    
    output = []
    
    offset = 0
    match_iter = styleTagPattern.finditer(html)
    for match in match_iter:
        tag = html[match.start():match.end()]
        tag = process_css_file(page, tag, base_url)
        
        output.append(html[offset:match.start()])
        output.append(tag)
        
        offset = match.end()
    
    output.append(html[offset:len(html)])

    html = "".join(output)

    # Processing style attributes.

    output = []
    
    offset = 0
    match_iter = styleAttribPattern.finditer(html)
    for match in match_iter:
        attribute = html[match.start():match.end()]
        attribute = process_expression(page, attribute, base_url)
        
        output.append(html[offset:match.start()])
        output.append(attribute)
        
        offset = match.end()
    
    output.append(html[offset:len(html)])

    return "".join(output)

class qs_list(object):
    """
    A list-like object which includes the additional _clone and replaced count method of QuerySets. 
    This is necessary for passing a list to the object_list generic view, which usually expects
    a QuerySet.
    """
    def __init__(self, *args):
        self.l = list(*args)
    def __getattr__(self, attr):
        return self.l.__getattr__(attr)
    def __iter__(self, *args):
        return self.l.__iter__(*args)
    def __getitem__(self, *args):
        item = self.l.__getitem__(*args)
        if isinstance(item, list):
            return qs_list(item)
    def _clone(self):
        return self
    def count(self):
        return len(self.l)

import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
#
# from http://effbot.org/zone/re-sub.htm#unescape-html

def unescape_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def get_id_subdir_path(id):
    return id[0] + "/" + id[1] + "/" + id[2] + "/" + id[3]

##
# Completely strips HTML and XML tags from a string
# This method should allow for single uses of < or > for mathematical expressions
# --Chris
#    
def remove_html_tags(data):
    p = re.compile(r'<[^<]*?>')
    return p.sub('', data)
