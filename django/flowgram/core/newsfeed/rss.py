import datetime, time
from flowgram.core.helpers import remove_html_tags

def render_news_feed(request_user, user, type, show_items_after_timestamp=None, rss_key=None):
    from flowgram.core.newsfeed import get_news_feed_items
    from flowgram import localsettings, settings
    from flowgram.core.securerandom import secure_random_id

    items = get_news_feed_items(request_user, user, show_items_after_timestamp)
    
    if rss_key != None:
        items100 = items.filter(eventCode='BADGE_FGVIEWS_100')
        items500 = items.filter(eventCode='BADGE_FGVIEWS_500')
        items1k = items.filter(eventCode='BADGE_FGVIEWS_1k')
        items5k = items.filter(eventCode='BADGE_FGVIEWS_5k')
        items10k = items.filter(eventCode='BADGE_FGVIEWS_10k')
        items = items.exclude(currentUser=user)
        items = items | items100 | items500 | items1k | items5k | items10k
        rss_title = 'Your Flowgram Newsfeed'
    else:
        rss_title = '%s activity on Flowgram' % user.username

    items = items.exclude(eventCode='UNSUB')

    output = []

    output.extend(['<?xml version="1.0"?>',
                   '<rss version="2.0"><channel>',
                   '<title>%s</title>' % rss_title,
                   '<link>%srss/%s/</link>' % (localsettings.my_URL_BASE, user.username),
                   '<description>A Flowgrammer\'s Newsfeed</description>',
                  ])

    feed_id = secure_random_id(settings.ID_ACTUAL_LENGTH)

    for item in items:
        timestamp = time.mktime(item.eventTime.timetuple())
        pubDate = datetime.datetime.utcfromtimestamp(timestamp).strftime("%a, %d %b %Y %H:%M:%S GMT")
        message = ''.join(['<item>',
                           '<title>%s</title>' % \
                               remove_html_tags(item.thirdPersonPast),
                           '<description>%s</description>' % \
                               item.thirdPersonPast.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                           '<pubDate>%s</pubDate>' % pubDate,
                           '</item>',
                          ])
        output.append(message)

    output.append('</channel></rss>');

    return ''.join(output)