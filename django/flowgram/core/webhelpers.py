from datetime import date, timedelta
import MySQLdb

from django.views.generic.list_detail import object_list

from flowgram.core import helpers, models
from flowgram.core.require import require
from flowgram import localsettings

FLOWGRAMS_PER_PAGE = 12

MAX_PAGES = 20

MAX_RESULTS = FLOWGRAMS_PER_PAGE * MAX_PAGES

USER_AGENTS_BROWSERS_AND_VERSION = {'MSIE 7': ('MSIE', 7),
                                    'MSIE 6': ('MSIE', 6),
                                    'Gecko': ('Gecko', 0)}

last_blog_entry = None
last_blog_entry_timestamp = None


@require('GET', ['enc=html', 'queryset', 'template_name', 'extra_context=', 'display_mode=',
                     'page:int=1'])
def flowgram_lister(request, enc, queryset, template_name, extra_context, display_mode, page):
    queryset = queryset[:MAX_RESULTS]
    extra_context = extra_context or {}
    
    extra_context.update({
        'user': request.user,
        'display_mode': display_mode or request.COOKIES.get('flowgram_results_filter_type', 'grid')
    })
    
    return object_list(
        request,
        template_name=template_name,
        paginate_by=FLOWGRAMS_PER_PAGE,
        allow_empty=True,
        page=page,
        extra_context=extra_context,
        queryset=helpers.qs_list(queryset) if isinstance(queryset, list) else queryset)


def get_brower_and_version(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    browser_version = [USER_AGENTS_BROWSERS_AND_VERSION[id] \
                           for id in USER_AGENTS_BROWSERS_AND_VERSION \
                           if user_agent.find(id) >= 0]
    return browser_version[0] if len(browser_version) else ('', 0)


def get_latest_fg_blog_posts(posts_to_show=3):
    return []
    
    global last_blog_entry, last_blog_entry_timestamp

    expiration_time = date.today() - timedelta(seconds=600)
    if last_blog_entry and last_blog_entry_timestamp and \
            last_blog_entry_timestamp > expiration_time:
        return last_blog_entry[:posts_to_show]

    DB_HOST = localsettings.DATABASE_HOST_BLOG
    DB_NAME = 'fg_wordpress'
    DB_USER = 'fg_dev'
    DB_PASS = 'qwe[poi'
    
    conn = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    main_cursor = conn.cursor()
    posts = []

    query = "select post_title, id from wp_posts where post_status='publish' order by post_date desc limit 10"
    main_cursor.execute(query)
    wordpress_data = main_cursor.fetchall()
    
    for row in wordpress_data:
       row_content = {}
       row_content['title'] = row[0]
       row_content['url'] = 'http://blog.flowgram.com/?p=' + str(row[1])
       posts.append(row_content)
    
    last_blog_entry = posts
    last_blog_entry_timestamp = date.today()
    return last_blog_entry[:posts_to_show]


def get_user_properties(user, should_delete_blank_flowgrams=False):
    profile = user.get_profile()
    profile_complete = sum([bool(profile.gender),
                            bool(profile.homepage),
                            bool(profile.description)]) == 3
    
    badges = {'teamFg': 'TeamFG' if user.is_staff else ''}
    
    flowgrams = models.Flowgram.objects.filter(owner=user)
    if should_delete_blank_flowgrams:
        helpers.delete_blank_flowgrams(flowgrams)
    
    total_num_views = sum([flowgram.views for flowgram in flowgrams])
    badges['views'] = helpers.get_badge_view_level(total_num_views)

    num_public_flowgrams = flowgrams.filter(public=True).count()
    num_unlisted_flowgrams = flowgrams.count() - num_public_flowgrams
    num_times_flowgrams_favorited = models.Favorite.objects.filter(flowgram__in=flowgrams).count()

    return {
        'profile': profile,
        'profile_complete': profile_complete,
        'badges': badges,
        'flowgrams': flowgrams,
        'total_num_views': total_num_views,
        'num_public_flowgrams': num_public_flowgrams,
        'num_unlisted_flowgrams': num_unlisted_flowgrams,
        'num_times_flowgrams_favorited': num_times_flowgrams_favorited
    }


# TODO(westphal): Change the naming system used in templates so this method is unnecessary.
def translate_user_properties(user_properties):
    """Translates user properties into the naming system that is currently used by templates."""
    return {
        'profile': user_properties['profile'],
        'profile_complete': user_properties['profile_complete'],
        'badges': user_properties['badges'],
        'badgeTeamFG': user_properties['badges']['teamFg'],
        'badgeViews': user_properties['badges']['views'],
        'public_fgs_count': user_properties['num_public_flowgrams'],
        'private_fgs_count': user_properties['num_unlisted_flowgrams'],
        'total_views': user_properties['total_num_views'],
        'total_favs': user_properties['num_times_flowgrams_favorited'],
    }
    
def get_flowgram_stats(flowgram):
    faved = models.Favorite.objects.filter(flowgram=flowgram).count()
    return {
        'views': flowgram.views,
        'widget_views': flowgram.widget_views,
        'faved': faved,
        'share_emails': flowgram.share_emails,
    }
