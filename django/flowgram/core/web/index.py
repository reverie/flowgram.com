from django.contrib.auth import models as auth_models
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string

from flowgram import localsettings, settings
from flowgram.core import cached_sets, controller, helpers, models, newsfeed, webhelpers
from flowgram.core.require import require


@require('GET', ['enc=html'], ['authorized'])
def index(request, enc):
    if request.user.is_authenticated():
        controller.record_stat(request, 'view_index_website', '0', 'logged in')
        return HttpResponseRedirect('/home')

    (featured_set, category_bestof_fgs) = get_featured_and_best_flowgrams()

    mostviewed = cached_sets.most_viewed()[:8]

    controller.record_stat(request, 'view_index_website', '0', 'anonymous')
    
    referer = request.META.get('HTTP_REFERER', '')
    
    landing_name = request.GET.get('landing_name', '')
    
    default_hero_image = '/media/images/homeherotext.png'
    default_hero_text = 'Create interactive guided presentations by combining web pages, photos, Powerpoint and more with your voice, notes and highlights. Viewers can control the pages, scroll, click on links, view videos and more.'
    
    hero_image = '/media/images/homehero' + landing_name + '.png'
    if landing_name == 'presos':
        hero_text = 'The ultimate presentation sharing and mashup tool.  Upload PowerPoint, add web pages, photos, PDF & a voice narration, then share as a link or embed the Flowgram widget.  Viewers can control the pages, scroll, clikco n the links, view videos and more.  Easy, free & nothing to install.'
    elif landing_name == 'education':
        hero_text = '"a fantastic interactive communication tool both inside and outside the classroom -- for instructors and students alike," -- Gina Maranto, Dir. of English Composition University of Miami.  Create guided presos by combining the web, photos, PowerPoint and your voice.  Viewers can control the pages, scroll, click on links, & view videos.  Free, easy & nothing to install.'
    elif landing_name == 'photos':
        hero_text = 'Bring your photos to life.  Upload form your computer or import Flickr and Facebook, then add your voice and related media to create rich, engaging and fun albums & slideshows.'
    elif referer.find('.edu') >= 0:
        hero_image = '/media/images/homeheroeducation.png'
        hero_text = '"a fantastic interactive communication tool both inside and outside the classroom -- for instructors and students alike," -- Gina Maranto, Dir. of English Composition University of Miami.  Create guided presos by combining the web, photos, PowerPoint and your voice.  Viewers can control the pages, scroll, click on links, & view videos.  Free, easy & nothing to install.'
    else:
        hero_image = default_hero_image
        hero_text = default_hero_text

    return helpers.req_render_to_response(
        request,
        'index/index.html',
        {
            'active': 'home',
            'category_bestof_fgs': category_bestof_fgs,
            'community': cached_sets.get_community_content(),
            'display_filters_suppress': True,
            'featured': featured_set,
            'fg_timestamp': False,        
            'mostviewed': mostviewed,
            's3_bucket_static': localsettings.S3_BUCKETS[localsettings.S3_BUCKET_STATIC],
            'tip': cached_sets.get_a_tip(),
            'whats_new': cached_sets.get_a_whats_new(),
            'send_to_details': localsettings.FEATURE['send_to_details'],
            'hero_image': hero_image,
            'hero_text': hero_text,
        })


@require('GET', ['enc=html'], ['authorized'])
def index_logged_in(request, enc):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    
    user = request.user
    user_properties = webhelpers.get_user_properties(user, True)

    (featured_set, category_bestof_fgs) = get_featured_and_best_flowgrams()

    favorites = models.Favorite.objects.filter(owner=user)

    current_poll = current_poll_fg1 = current_poll_fg2 = current_poll_fg3 = current_poll_fgs = \
        poll_module_cookie_name = poll_module_status = None

    polls = models.FlowgramPoll.objects.filter(poll_active=1).order_by('-date_created')[:1]
    poll_exists = bool(polls)
    if poll_exists:
        current_poll = polls[len(polls) - 1]
        current_poll_fgs = models.Flowgram.objects.filter(id__in=[current_poll.candidate_id_1,
                                                                  current_poll.candidate_id_2,
                                                                  current_poll.candidate_id_3])
        # TODO(westphal): Take a look at these. Why do we need to separate?
        (current_poll_fg1, current_poll_fg2, current_poll_fg3) = current_poll_fgs
        poll_module_cookie_name = 'flowgram_poll_' + str(current_poll.id)
        poll_module_status = request.COOKIES.get(poll_module_cookie_name, 'not_voted_yet')

    context = {
        'user': user,
        'featured': featured_set,
        'category_bestof_fgs': category_bestof_fgs,
        'favorites': favorites,
        'active': 'home',
        'activesecondary': '',
        'profile_views': user_properties['profile'].views,
        'current_poll': current_poll,
        'current_poll_fg1': current_poll_fg1,
        'current_poll_fg2': current_poll_fg2,
        'current_poll_fg3': current_poll_fg3,
        'current_poll_fgs': current_poll_fgs,
        'poll_module_status': poll_module_status,
        'poll_exists': poll_exists,
        'fg_timestamp': False,
        'whats_new': cached_sets.get_a_whats_new(),
        'tip': cached_sets.get_a_tip(),
        'community': cached_sets.get_community_content(),
        'subs_active': localsettings.FEATURE['subscriptions_fw'],
        'newsfeed_display': newsfeed.render(request.user, user, True),
        'send_to_details': localsettings.FEATURE['send_to_details'],
        'posts': webhelpers.get_latest_fg_blog_posts(),
    }
    context.update(webhelpers.translate_user_properties(user_properties))

    # TODO(westphal): get user_property names inline with these context variables.
    return helpers.req_render_to_response(
        request, 
        'index/index_logged_in.html',
        context)


# HELPERS-------------------------------------------------------------------------------------------


def get_featured_and_best_flowgrams():
    featured_set = [cached_sets.get_hero(models.feat.FEATURED_PAGE)] + \
                       cached_sets.get_featured(models.feat.FEATURED_PAGE)[:11]

    category_bestof_fgs = [(cached_sets.get_featured(category), models.feat_fullname[category]) \
                               for category in models.FEATURED_CATEGORIES]

    return (featured_set, category_bestof_fgs)
