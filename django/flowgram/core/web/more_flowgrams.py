from django.contrib.auth import models as auth_models

from flowgram import localsettings
from flowgram.core import cached_sets, controller, helpers, models, webhelpers
from flowgram.core.require import require


@require('GET', ['enc=html', 'browse_type', 'user='])
def view_ajax_browse(request, enc, browse_type, user):
    stat_string = 'FGs owner user id = ' + (user.username if user else 'None')

    if browse_type == 'featured':
        fg_data_set = [cached_sets.get_hero(models.feat.FEATURED_PAGE)] + \
                          cached_sets.get_featured(models.feat.FEATURED_PAGE)[:11]
        controller.record_stat(request, 'view_browse_feat_ajax_website', '0', '')
    elif browse_type == 'newest':
        fg_data_set = cached_sets.newest()[:12]
        controller.record_stat(request, 'view_browse_feat_new_website', '0', '')
    elif browse_type == 'most_viewed':
        fg_data_set = cached_sets.most_viewed()[:12]
        controller.record_stat(request, 'view_browse_most_ajax_website', '0', '')
    elif browse_type == 'most_discussed':
        fg_data_set = cached_sets.most_discussed()[:12]
        controller.record_stat(request, 'view_browse_disc_ajax_website', '0', '')
    elif browse_type == 'top_rated':
        fg_data_set = cached_sets.top_rated()[:12]
        controller.record_stat(request, 'view_browse_rate_ajax_website', '0', '')
    elif browse_type == 'user_newest':
        fg_data_set = cached_sets.user_newest(user.username)[:6]
        controller.record_stat(request, 'view_browse_new_ajax_website', '0', stat_string)
    elif browse_type == 'user_most_viewed':
        fg_data_set = cached_sets.user_most_viewed(user.username)[:6]
        controller.record_stat(request, 'view_browse_most_ajax_website', '0', stat_string)
    elif browse_type == 'user_most_discussed':
        fg_data_set = cached_sets.user_most_discussed(user.username)[:6]
        controller.record_stat(request, 'view_browse_disc_ajax_website', '0', stat_string)
    elif browse_type == 'user_top_rated':
        fg_data_set = cached_sets.user_top_rated(user.username)[:6]
        controller.record_stat(request, 'view_browse_rate_ajax_website', '0', stat_string)
    elif browse_type == 'user_title':
        fg_data_set = cached_sets.user_title(user.username)[:6]
        controller.record_stat(request, 'view_browse_title_ajax_website', '0', stat_string)
    
    return helpers.req_render_to_response(request,
                                          'includes/modules/flowgram/fg_modules_ajax.incl',
                                          {'fg_data_set': fg_data_set,
                                           'fg_timestamp': request.user == user,
                                           'send_to_details': localsettings.FEATURE['send_to_details'],})


# TODO(westphal): Figure out what prpu stands for and document.
@require('GET', ['enc=html', 'username', 'sort_criterion', 'prpusort='])
def view_favorites(request, enc, user, sort_criterion, prpusort):
    favs = models.Favorite.objects.filter(owner=user)
    
    controller.record_stat(request,
                           'view_favorites_website',
                           '0',
                           'fave owner user id = ' + str(user.id))
    
    fav_fgs = []
    for favorite in favs:
        flowgram = favorite.flowgram
        is_public_str = 'public' if flowgram.public else 'private'

        if request.user == user:
            if prpusort == 'all' or prpusort == is_public_str:
                fav_fgs.append(flowgram)
        elif flowgram.public:
            fav_fgs.append(flowgram)
    
    (page_owner, active) = (True, 'you') if request.user == user else (False, 'browse')
    
    fav_fgs = helpers.sort_flowgrams(fav_fgs,
                                     helpers.convert_sort_criterion(sort_criterion, '-modified_at'))
    
    extra_context = {
        'u': user,
        'profile': user.get_profile(),
        'fgs': fav_fgs,
        'active': active,
        'subs_active': localsettings.FEATURE['subscriptions_fw'],
        'activesecondary': 'favorites',
        'mostviewed': cached_sets.most_viewed()[:6],
        'pageowner': page_owner,
        'num_favs': len(fav_fgs),
        'sort_criterion': sort_criterion,
        'pub_priv': prpusort,
        'multiple_owners': True,
        'sortable': True,
        'send_to_details': localsettings.FEATURE['send_to_details'],
        'posts': webhelpers.get_latest_fg_blog_posts(),
    }
    
    return webhelpers.flowgram_lister(request,
                                      enc='html',
                                      queryset=fav_fgs,
                                      template_name='flowgram/view_favorites.html',
                                      extra_context=extra_context)


@require('GET', ['enc=html']) 
def view_featured(request, enc):
    context = {'hero': cached_sets.get_hero(models.feat.FEATURED_PAGE),
               'mostviewed': cached_sets.most_viewed()[:6],
               'category_bestof_fgs': helpers.get_category_bestof_fgs(),
               'next': '/browse/featured',
               'send_to_details': localsettings.FEATURE['send_to_details'],
               'posts': webhelpers.get_latest_fg_blog_posts(),
               }
    controller.record_stat(request, 'view_browse_feat_website', '0', '')
    return webhelpers.flowgram_lister(request,
                                      enc=enc,
                                      queryset=cached_sets.get_featured(models.feat.FEATURED_PAGE),
                                      template_name='flowgram/view_featured.html',
                                      extra_context=context)


@require('GET', ['enc=html']) 
def view_most_discussed(request, enc):
    context = get_default_context()
    context['next'] = '/browse/mostdiscussed'
    controller.record_stat(request, 'view_browse_disc_website', '0', '')
    return webhelpers.flowgram_lister(request,
                                      enc=enc,
                                      queryset=cached_sets.most_discussed(),
                                      template_name='flowgram/view_most_discussed.html',
                                      extra_context=context)


@require('GET', ['enc=html']) 
def view_most_viewed(request, enc):
    context = get_default_context()
    context['next'] = '/browse/mostviewed'
    controller.record_stat(request, 'view_browse_most_website', '0', '')
    return webhelpers.flowgram_lister(request,
                                      enc=enc,
                                      queryset=cached_sets.most_viewed(),
                                      template_name='flowgram/view_most_viewed.html',
                                      extra_context=context)


@require('GET', ['enc=html']) 
def view_newest(request, enc):
    context = get_default_context()
    context['fg_timestamp'] = True
    context['next'] = '/browse/newest'
    controller.record_stat(request, 'view_browse_new_website', '0', '')
    return webhelpers.flowgram_lister(request, 
                                      enc=enc,
                                      queryset=cached_sets.newest(),
                                      template_name='flowgram/view_newest.html',
                                      extra_context=context)


@require('GET', ['enc=html'])
def view_toprated(request, enc):
    context = get_default_context()
    context['next'] = '/browse/toprated'
    controller.record_stat(request, 'view_browse_rate_website', '0', '')
    return webhelpers.flowgram_lister(request, 
                                      enc=enc,
                                      queryset=cached_sets.top_rated(),
                                      template_name='flowgram/view_toprated.html',
                                      extra_context=context)


# HELPERS-------------------------------------------------------------------------------------------


def get_default_context():
    return {'discussed': cached_sets.most_discussed()[:6],
            'category_bestof_fgs': helpers.get_category_bestof_fgs(),
            'mostviewed': cached_sets.most_viewed()[:6],
            'send_to_details': localsettings.FEATURE['send_to_details'],
            'posts': webhelpers.get_latest_fg_blog_posts(),
            }
