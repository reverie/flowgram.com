"""
File: fix.py
Authors: Andrew Badr, Yi Ding

Alters the rendered HTML when it is first received from the client, before we save it to disk.
Used like: html, url = process_page(html, url)
"""

import re
from xml.sax.saxutils import unescape
from flowgram.core.helpers import insert_in_head, url_base, remove_script_tags
from flowgram.localsettings import MEDIA_URL
from flowgram.core import log

def process_unrendered_page(html, url):    
    html, url = add_topdog_fix(html, url)
    html, url = add_base(html, url)
    return html, url

def add_topdog_fix(html, url):
    return (insert_in_head(html, '<script type="text/javascript">var top = window;</script>'), url)

#def process_webkinz_page(html, url):
    ## Site specific hacks
    #log.debug('Called process_page on %s' % (url))
    #if url.startswith("http://youtube.com/watch") or url.startswith("http://www.youtube.com/watch"):
        #log.debug('Calling fix_youtube')
        #html, url = fix_youtube_webkinz(html, url)
    #elif url.startswith("http://maps.google.com"):
        #log.debug('Calling fix_google_maps')
        #html, url = fix_google_maps(html, url)
    #elif url.startswith("http://gallery.mac.com/"):
        #log.debug('Calling fix_mac_gallery')
        #html, url = fix_mac_gallery(html, url)
    
    #html, url = remove_self_targets(html, url)
    #html, url = add_base(html, url)
    #html, url = add_base_target(html, url)
    #html, url = add_page_css(html, url)
    
    #return (html, url)

def process_page(html, url):
    # Site specific hacks
    log.debug('Called process_page on %s' % (url))
    if url.startswith("http://youtube.com/watch") or url.startswith("http://www.youtube.com/watch"):
        log.debug('Calling fix_youtube')
        html, url = fix_youtube(html, url)
    elif url.startswith("http://maps.google.com"):
        log.debug('Calling fix_google_maps')
        html, url = fix_google_maps(html, url)
    elif url.startswith("http://gallery.mac.com/"):
        log.debug('Calling fix_mac_gallery')
        html, url = fix_mac_gallery(html, url)
    elif url.startswith("http://www.techcrunch.com/2008/07/03/flowgram-reinvents-the-screencast-1000-beta-invites"):
        html, url = fix_techcrunch_flowgram_article(html, url)
   # elif url == "http://www.flowgram.com/" or url == "http://www.flowgram.com" or url == "http://dev.flowgram.com" or url == "http://dev.flowgram.com/" :
        #log.debug('Calling fix_flowgram_own_homepage')
        #html, url = fix_flowgram(html, url)
    #elif url.startswith("http://www.flowgram.com/fg/"):
       # log.debug('Calling fix_flowgram_widget_fg')
        #html, url = fix_flowgram_widget_fg(html, url)

    html, url = remove_self_targets(html, url)
    html, url = add_base(html, url)
    html, url = add_base_target(html, url)
    html, url = add_page_css(html, url)
    html = remove_script_tags(html, url)
    
    return (html, url)

def html_matcher(s):
    """
    Create a regular expression to match the given string of HTML.
    Quotes are optional, capitalization and spacing ignored.
    """
    s = re.escape(s).replace('"', '"?')
    return re.compile(s, re.IGNORECASE | re.VERBOSE)

targetself_re = html_matcher('target="_self"')
def remove_self_targets(html, url):
    ranges = []
    for targetself in targetself_re.finditer(html):
        start, end = targetself.start(), targetself.end()
        try:
            prev_lt = html.rindex('<', 0, start)
            next_gt = html.index('>', start)
        except ValueError:
            return html, url
        # does this check really tell us anything?:
        in_a_tag = (prev_lt < start < next_gt)
        if not in_a_tag:
            continue
        ranges.append((start, end))
    new_html = []
    last_end = 0
    for start, end in ranges:
        new_html.append(html[last_end:start])
        new_html.append(html[start:end].replace('_self', '_top'))
        last_end = end
    new_html.append(html[last_end:])
    html = ''.join(new_html)
    return html, url

def fix_flowgram(html, url):
    FIREFOX, IE = 0, 1
    
    if html.find('<iframe id="content"') == -1:
        mode = IE
    else:
        mode = FIREFOX
    
    if mode == IE:
        tutorial_video_start = html.find('<div id="homeHeroVideo">') + len('<div id="homeHeroVideo">')
        tutorial_html = '<embed id="mpl" height="276" width="322" flashvars="&file=http://static.flowgram.com/media/swf/homeHero/homepagemovie8a.flv&image=/media/swf/homeHero/screen.png" wmode="opaque" allowfullscreen="true" allowscriptaccess="always" quality="high" name="mpl" style="" src="http://www.flowgram.com/media/swf/jwplayer/player.swf" type="application/x-shockwave-flash"/>'
        altered_html = html[:tutorial_video_start] + tutorial_html + html[tutorial_video_start:]
    else:
        altered_html = html
    return altered_html, url


def fix_flowgram_widget_fg(html, url):  
    widget_start = html.find('<div class="wrapper_widget">') + len('<div class="wrapper_widget">') 
        
    widget_id_start = html[widget_start:].find('<div id="alt_') + len('<div id="alt_')
    widget_id_end = html[widget_start:].find('"></div>')
    widget_id = html[widget_start:][widget_id_start:widget_id_end]
        
    widget_end = widget_start + len('<div id="alt_') + len(widget_id) + len('"></div>') + 2

    widget_source = '<object id="fwidget_' + widget_id + '" type="application/x-shockwave-flash" data="http://www.flowgram.com/widget/flexwidget.swf" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" \
                    width="320" height="282"><param name="movie" value="http://www.flowgram.com/widget/flexwidget.swf" /><param name="flashVars" value="id=' + widget_id + '&hasLinks=true" /> \
                    <param name="allowScriptAccess" value="always" /><param name="allowNetworking" value="all" /> \
                    <param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" /></object>'
    altered_html = html[:widget_start] + widget_source + html[widget_end:]
    return altered_html, url
    

def fix_youtube(html, url):
    FIREFOX, IE = 0, 1
    if html.find('<OBJECT') == -1:
        #print "Firefox mode"
        mode = FIREFOX
    else:
        #print "Entering IE mode!"
        mode = IE

    # Get player code

    if mode == FIREFOX:
        player_id = html.find('id="movie_player"')
        player_start = html.rfind('<', 0, player_id)
        player_end = html.find('>', player_id) + 1
    else:
        player_id = html.find('id=movie_player')
        player_start = html.rfind('<', 0, player_id)
        player_end = html.find('</OBJECT>', player_id) + 9
        
    if player_id == -1 or player_start == -1 or player_end == -1:
        return fix_youtube_webkinz(html, url)

    #print "Player:", html[player_start:player_end]
    #print ''

    # Get embed code
    if mode == FIREFOX:
        embedcode_id = html.find('id="embed_code"')
        embedcode_start = html.find('value=', embedcode_id) + 7
        embedcode_end = html.find('"', embedcode_start)
    else:
        embedcode_id = html.find('id=embed_code')
        embedcode_start = html.find('value=', embedcode_id) + 7
        embedcode_end = html.find("'", embedcode_start)
    embed = html[embedcode_start: embedcode_end]

    #print "Embed:", embed
    #print ''

    real_embed = unescape(embed, entities={'&quot;':'"'})
    real_embed.replace('355', '395')
    real_embed.replace('425', '480')

    #print "Real embed:", real_embed
    #print ''

    altered_html = html[:player_start] + real_embed + html[player_end:]

    return (altered_html, url)

def fix_youtube_webkinz(html, url):
    noplayer_id = html.find('id="watch-noplayer-div"')
    noplayer_start = html.rfind('<', 0, noplayer_id)
    noplayer_end = html.find('/div>', noplayer_id) + len('/div>')+1
    embedcode_id = html.find('id="embed_code"')
    embedcode_start = html.find('value=', embedcode_id) + 7
    embedcode_end = html.find('"', embedcode_start)
    embed = html[embedcode_start: embedcode_end]
    real_embed = unescape(embed, entities={'&quot;':'"'})
    real_embed.replace('355', '395')
    real_embed.replace('425', '480')
    altered_html = html[:noplayer_start] + real_embed + html[noplayer_end:]
    return (altered_html, url)

def fix_google_maps(html, url):
    log.debug('Called fix_google_maps on %s' % (url))
    try:
        link_elem = html.index('id="link"')
        log.debug('Found link_elem: %s' % (link_elem))
    except ValueError:
        try:
            link_elem = html.index('id=link')
        except ValueError:
            return (html, url) #can't find maps, so don't do anything
    
    try:
        link_elem = html.rindex('<', 0, link_elem)
        link_begin = html.index('href=\"', link_elem) + 6
        link_end = html.index('\"', link_begin)
    except ValueError:
        return (html, url) #malformed html, so don't do anything
    
    url = unescape(html[link_begin:link_end])
    log.debug('Got URL: %s' % (url))
    return (html, url)

def fix_mac_gallery(html, url):
    # TODO(Andrew): clean up this and add_page_css
    try:
        head_end = html.index('</head>')
    except ValueError:
        try:
            head_end = html.index('</HEAD>')
        except ValueError:
            return (html, url) #No </head> so don't do anything.

    return (html[:head_end] + "<link rel=\"stylesheet\" href=\"" + MEDIA_URL + "css/site_fixes/fix_mac_gallery.css\" type=\"text/css\" />" + html[head_end:], url)    

def fix_techcrunch_flowgram_article(html, url):
    html.replace("http://cetrk.com/pages/scripts/0009/0873.js", "")
    html.replace("http://analytics.engagd.com/archin-std.js", "")
    html.replace("http://static.fmpub.net/zone/23", "")
    html.replace("http://static.fmpub.net/zone/32", "")
    html.replace("http://static.fmpub.net/zone/70", "")
    return (html, url)

def add_base(html, url):
    #print "add base called"
    base_href = url_base(url)
    base_tag = "<base href=\"%s\"></base>" % base_href
    return (insert_in_head(html, base_tag), url)

def add_base_target(html, url, target="_top"):
    base_tag = "<base target=\"%s\"></base>" % target
    return (insert_in_head(html, base_tag), url)

def add_page_css(html, url, safe=True):
    try:
        head_end = html.index('</head>')
    except ValueError:
        try:
            head_end = html.index('</HEAD>')
        except ValueError:
            return (html, url) #No </head> so don't do anything.

    return (html, url)
