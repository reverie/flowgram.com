import datetime

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from flowgram import localsettings, settings
from flowgram.core import controller, helpers, models
from flowgram.core.newsfeed import email, rss, site


# Cache expires after 10 minutes.
CACHE_EXPIRATION = 600


#TODO(westphal): Write a separate service to clean up expired cache items.
def get_rendered_news_feed(request_user, user, type, show_items_after_timestamp=None, rss_key=None):
    
    if type == 'R' or not request_user.is_authenticated():
        request_user = None
    
    try:
        #raise models.RenderedNewsFeedCache.DoesNotExist
        rendered_news_feed = models.RenderedNewsFeedCache.objects.filter(
            user=user,
            request_user=request_user,
            type=type,
            timestamp__gte=datetime.datetime.now() - datetime.timedelta(seconds=CACHE_EXPIRATION))
        models.RenderedNewsFeedCache.objects.filter(
            user=user,
            request_user=request_user,
            type=type,
            timestamp__lte=datetime.datetime.now() - datetime.timedelta(seconds=CACHE_EXPIRATION)).delete()
        if not len(rendered_news_feed):
            raise models.RenderedNewsFeedCache.DoesNotExist()
        return rendered_news_feed[0].data
    except models.RenderedNewsFeedCache.DoesNotExist:
        if type == 'S' or type == 'L':
            data = site.render_news_feed(request_user, user, type, show_items_after_timestamp)
        elif type == 'R':
            data = rss.render_news_feed(request_user, user, type, show_items_after_timestamp, rss_key)
        elif type == 'E':
            data = email.render_news_feed(request_user, user, type, show_items_after_timestamp)
        models.RenderedNewsFeedCache.objects.create(user=user,
                                                    request_user=request_user,
                                                    type=type,
                                                    data=data)
        return data


def get_news_feed_items(request_user, user, show_items_after_timestamp=None):
    # handle FG view landmarks here.  Took this out of toolbar.record_views() to increase
    # efficiency. -- chris
    # if a landmark was reached (100, 500, 10000 views) if so trigger UserHistory event storage
    # pass flowgram.id to get user context
    total_fgs = models.Flowgram.objects.filter(owner=user)
    total_fg_views = 0
    for fg in total_fgs:
        total_fg_views += fg.views
    user_profile = user.get_profile()
    for level in settings.BADGE_VIEW_LEVELS:
        if user_profile.last_total_fg_badge_given < level and total_fg_views > level:
            controller.check_fgviews_landmark(user, level)

            user_profile.last_total_fg_badge_given = level
            user_profile.save()
            break
    
    include_non_creation_items = request_user == user or \
                                 user.get_profile().has_public_news_feed
    items = models.UserHistory.objects.exclude(eventActive=False)
    if show_items_after_timestamp:
        items = items.exclude(eventTime__lt=show_items_after_timestamp)
        
    # handle multiple adjacent tag announcements
    items_adjacent_tags = items.filter(eventCode='FG_TAGGED')
    items_adjacent_tags_include_array = []
    previous_fgid = ''
    current_fgid = ''
    previous_tag_user = ''
    current_tag_user = ''
    for tag_item in items_adjacent_tags:
        previous_tag_user = current_tag_user
        current_tag_user = tag_item.currentUser
        previous_fgid = current_fgid
        current_fgid = tag_item.flowgramId
        if current_tag_user != previous_tag_user or current_fgid != previous_fgid:
            items_adjacent_tags_include_array.append(int(str(tag_item.id)))
    items = items.exclude(eventCode='FG_TAGGED')
    items_adjacent_tags = items_adjacent_tags.filter(id__in=items_adjacent_tags_include_array)
    items = items | items_adjacent_tags

    # we need to announce comments even if the user is not subscribed to the commenter
    items_non_subscribed = items

    if request_user != user:
        items = items.filter(currentUser=user)

    if include_non_creation_items:
        users = [user]
        users.extend([subscription.user for subscription \
                                        in models.Subscription.objects.filter(subscriber=user)])
        items = items.filter(currentUser__in=users)
        # get data set for comments on user fgs where user is unubscribed to commenter
        items_non_subscribed = items_non_subscribed.filter(targetUser=user)
        items = items | items_non_subscribed
        
    else:
        items = items.filter(currentUser=user, eventCode='FG_MADE')

    return items.order_by('-id')


def render(request_user, user, short):
    return render_to_string(
        'includes/modules/newsfeed/newsfeed_display.html',
        {
            'news_list': get_rendered_news_feed(request_user, user, 'S' if short else 'L'),
            'user': user,
            'fullFeed': not short,
            'owner': request_user == user,
            'URL_BASE': localsettings.my_URL_BASE
        })
