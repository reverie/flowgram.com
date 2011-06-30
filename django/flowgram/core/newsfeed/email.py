def render_news_feed(request_user, user, type, show_items_after_timestamp=None):
    from flowgram.core.newsfeed import get_news_feed_items
    from flowgram import localsettings, settings
     
    items = get_news_feed_items(request_user, user, show_items_after_timestamp)
    print "there are %d" % len(items)
    items = items.exclude(currentUser=user)
    print "there are now %d" % len(items)
    
    items = items.exclude(eventCode='UNSUB')
    if not request_user == user:
        items = items.exclude(eventCode='BADGE_FGVIEWS_100')
        items = items.exclude(eventCode='BADGE_FGVIEWS_10k')
        items = items.exclude(eventCode='BADGE_FGVIEWS_1k')
        items = items.exclude(eventCode='BADGE_FGVIEWS_500')
        items = items.exclude(eventCode='BADGE_FGVIEWS_5k')
        items = items.exclude(eventCode='BADGE_FGVIEWS_GENERIC')

    if not len(items):
        return ''

    output = []
    
    messageIntro = "<p><strong>Hello!  Here are your Flowgram subscription updates:</strong></p><p>"
    
    output.append(messageIntro)

    for item in items:
        if item.currentUser == request_user:
            message = item.secondPersonPresent
        elif item.targetUser == request_user:
            message = item.secondPersonPast
        else:
            message = item.thirdPersonPast
        messageFull = "%s<br/>" % (message)
        output.append(messageFull)
    
    updateUrl = "%ssubscriptions/" % (localsettings.my_URL_BASE)
    
    messageFooter = "</p><p><a href=\"%s\"><strong>Click here to update your Flowgram notification settings</strong></a>.</p><p>Flowgram subscriptions is a new feature that allows you to track things on Flowgram that are important to you. You can subscribe to any user and get notified when they make a new Flowgram, comment on something and so on. We'll also let you know about activity related to your Flowgrams.</p><p>You can control how notifications are delivered and the frequency by visiting your <a href=\"%s\">Flowgram notifications</a> page.</p>" % (updateUrl, updateUrl)
    
    output.append(messageFooter)

    return ''.join(output)
