from django.contrib.auth import models as auth_models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from flowgram import localsettings
from flowgram.core import cached_sets, controller, helpers, models, newsfeed, webhelpers
from flowgram.core.require import require


@require('GET', ['enc=html', 'username'])
def rss_newsfeed(request, enc, username):
    return HttpResponse(
        newsfeed.get_rendered_news_feed(request.user,
                                        get_object_or_404(auth_models.User, username=username),
                                        'R'),
        mimetype='application/rss+xml')
        
@require('GET', ['enc=html', 'rss_key'])
def rss_newsfeed_private(request, enc, rss_key):
    userprofile = models.UserProfile.objects.get(rss_key=rss_key)
    user = userprofile.user
    return HttpResponse(
        newsfeed.get_rendered_news_feed(request.user,
                                        user,
                                        'R', None, rss_key),
        mimetype='application/rss+xml')

@require('GET', ['enc=html', 'username'])
def show_full_newsfeed(request, enc, username):
    user = get_object_or_404(auth_models.User, username=username)
    user_properties = webhelpers.get_user_properties(user, True)
    
    context = webhelpers.translate_user_properties(user_properties)

    favs = models.Favorite.objects.filter(owner=user)
    fav_fgs = [favorite.flowgram for favorite in favs if favorite.flowgram.public][:4]
                
    # Get User profiles items from list of subscriptions
    subscription_profiles = []
    for sub in controller.get_user_subscriptions(user):
        subscription_user = models.UserProfile.objects.get(user=sub["user"])
        avatar_url= models.UserProfile.avatar_100(subscription_user)
        subscription_profiles.append({'username': subscription_user.user,
                                      'avatar_url': avatar_url})

    # Get User profiles items from list of subscribers
    subscriber_profiles = []
    for sub in controller.get_user_subscribers(user):
        subscriber_user = models.UserProfile.objects.get(user=sub["subscriber"])
        avatar_url= models.UserProfile.avatar_100(subscriber_user)
        subscriber_profiles.append({'username':subscriber_user.user,
                                    'avatar_url':avatar_url})
    
    context.update({'u': user,
                    'subs_active': localsettings.FEATURE['subscriptions_fw'],
                    'mostviewed': cached_sets.most_viewed()[:6],
                    'fav_fgs': fav_fgs,
                    'profile_views': user_properties['profile'].views,
                    'subscription_profiles': subscription_profiles,
                    'subscriber_profiles': subscriber_profiles,
                    'newsfeed_display': newsfeed.render(request.user, user, False)})
    
    return helpers.req_render_to_response(request, 'user/show_profile_newsfeed_full.html', context)
