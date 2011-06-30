from django.contrib.auth import models as auth_models
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from flowgram import localsettings
from flowgram.core import cached_sets, helpers, models, newsfeed, webhelpers
from flowgram.core.require import require


@require('GET', ['enc=html', 'user'], ['authorized'])
def show_user(request, enc, user):
    user_properties = webhelpers.get_user_properties(user, True)
    
    profile = user_properties['profile']
    profile.views += 1
    profile.save()
    profile_views = profile.views

    newsfeed_display = newsfeed.render(request.user, user, True)

    context = {
        'u': user,
        'subs_active': localsettings.FEATURE['subscriptions_fw'],
        'send_to_details': localsettings.FEATURE['send_to_details'],
        'activesecondary': 'profile',
        'mostviewed': cached_sets.most_viewed()[:6],
        'profile_views': profile_views,
        'newsfeed_display': newsfeed_display,
        'posts': webhelpers.get_latest_fg_blog_posts(),
    }
    context.update(webhelpers.translate_user_properties(user_properties))

    if user == request.user:
        return helpers.req_render_to_response(request, 'user/show_profile_owner.html', context)
    else:
        favs = models.Favorite.objects.filter(owner=user)
        fav_fgs = [favorite.flowgram for favorite in favs if favorite.flowgram.public][:4]
                
        fgs = models.Flowgram.from_published.filter(owner=user,
                                                    public=True).order_by('-published_at')[:6]
        
        # Checking if user is sub'd to this user.
        is_subscribed = models.Subscription.objects.filter(user=user, subscriber=request.user)
        
        context.update({
            'is_subscribed': is_subscribed,
            'fgs': fgs,
            'active': 'browse',
            'pageowner' : False,
            'display_filters_suppress': True,
            'fg_timestamp': False,
            'fav_fgs': fav_fgs,
            'news_list': newsfeed.get_rendered_news_feed(request.user, user, 'S')
        })
        
        return helpers.req_render_to_response(request, 'user/show_profile.html', context)
        
        
@require('GET', ['enc=html', 'user_id'], ['authorized']) 
def show_user_by_id(request, enc, user):
    return show_user(request, user=user)


@require('GET', ['enc=html', 'username'], ['authorized'])
def show_user_by_name(request, enc, username):
    return show_user(request, user=get_object_or_404(auth_models.User, username=username))
