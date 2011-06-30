from django.contrib import auth
from django.views.generic.list_detail import object_list

from flowgram import localsettings
from flowgram.core import cached_sets, controller, helpers, webhelpers, models
from flowgram.core.require import require


@require('GET', ['enc=html', 'username', 'sort_criterion', 'prpusort=', 'page:int=1'])
def view_your_flowgrams_thumb(request, enc, user, sort_criterion, prpusort, page):
    controller.record_stat(request, 'view_browse_userFGs_website', '0',
                               'FGs owner user id = ' + str(user.id))

    users_flowgrams = models.Flowgram.objects.filter(owner=user)

    fgs = {}

    page_owner = request.user == user
    if page_owner:
        active = 'you'
        activesecondary = 'viewall'

        if prpusort == 'private':
            fgs = users_flowgrams.filter(public=False)
        elif prpusort == 'public':
            fgs = users_flowgrams.filter(public=True)
        else:
            fgs = users_flowgrams

        fgs = fgs.order_by(helpers.convert_sort_criterion(sort_criterion, '-modified_at'))
    else:
        #TODO(cyap) figure out multiple views on this for owner/non-owners
        active = 'browse'
        activesecondary = 'viewalluser'

        fgs = users_flowgrams.filter(public=True)\
                  .order_by(helpers.convert_sort_criterion(sort_criterion, '-modified_at'))

    helpers.delete_blank_flowgrams(fgs)
        
    args = {'template_name': 'flowgram/view_your_flowgrams_thumb.html',
            'template_object_name': 'flowgram',
            'paginate_by': 14, 
            'allow_empty': True,
            'page': page,
            'extra_context': {
                'user': request.user,
                'u': user,
                'profile': user.get_profile(),
                'active': active,
                'subs_active': localsettings.FEATURE['subscriptions_fw'],
                'activesecondary': activesecondary,
                'pageowner': page_owner,
                'mostviewed': cached_sets.most_viewed()[:6],
                'display_mode': request.COOKIES.get('flowgram_results_filter_type', 'grid'),
                'num_favs': len(models.Favorite.objects.filter(owner=user)),
                'sort_criterion': sort_criterion,
                'pub_priv': prpusort,
                'multiple_owners': False,
                'sortable': True,
                'send_to_details': localsettings.FEATURE['send_to_details'],
                'posts': webhelpers.get_latest_fg_blog_posts(),
                },
            'queryset': fgs}
    return object_list(request, **args)
