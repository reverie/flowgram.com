import localsettings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from flowgram.localsettings import FEATURE

subs_active = FEATURE['subscriptions_fw']
bypasslogin_to_template = direct_to_template
direct_to_template = login_required(direct_to_template)

urlpatterns = patterns('flowgram.core.views',
    #website-> content
    (r'^$', 'index'),
    (r'^home/$', 'index_logged_in'),
    (r'^nojs/$', 'nojs'),
    (r'^rss/(?P<username>\w+)/$', 'rss_newsfeed'),
    (r'^rss/pri/(?P<rss_key>\w+)/$', 'rss_newsfeed_private'),
    (r'^people/(?P<user_id>\w+)/$', 'show_user_by_id'),
    (r'^fg/(?P<flowgram_id>\w+)/$', 'show_flowgram'),
    (r'^fg/(?P<flowgram_id>\w+)/edittitle/$', 'edit_flowgram_title'),
    (r'^fg/(?P<flowgram_id>\w+)/editdescription/$', 'edit_flowgram_description'),
    (r'^fg/(?P<flowgram_id>\w+)/delete/$', 'delete_flowgram'),
    (r'^fgr/(?P<flowgram_id>\w+)/$', 'details_redirect'),
    
    # These were using edit_flowgram previously.
    (r'^r/(?P<flowgram_id>\w+)/?$', 'play_flowgram'),
    (r'^r/(?P<flowgram_id>\w+)/(?P<hash>[^\/ ]+)/$', 'play_flowgram'),
    
    (r'^p/(?P<flowgram_id>\w+)/?$', 'play_flowgram'),
    (r'^p/(?P<flowgram_id>\w+)/(?P<hash>[^\/ ]+)/$', 'play_flowgram'),
    
    (r'^wp/(?P<flowgram_id>\w+)/$', 'widget_play_flowgram'),
    (r'^fg/(?P<flowgram_id>\w+)/play/$', 'play_flowgram'), # @deprecated
    (r'^fg/(?P<flowgram_id>\w+)/flag/$', 'flag_flowgram'),
    (r'^fg/(?P<flowgram_id>\w+)/deletetag/(?P<tag_name>.+)/$', 'delete_tag'),
    (r'^css/(?P<css_id>\w+)/$', 'get_css'),
    (r'^addcomment/$', 'add_comment'),
    (r'^delcomment/(?P<comment_id>\w+)/$', 'delete_comment'),
    (r'^tags/(?P<tag_name>.+)/$', 'show_tag'),
    (r'^addtag/$', 'add_tag'),
    (r'^search/$', 'search'),
    (r'^fgshare/(?P<sharelink_name>\w+)/$', 'show_shared_flowgram'),
    (r'^go/(?P<name>\w+)/$', 'goto_quick_link'),
    (r'^share/(?P<flowgram_id>\w+)/$', 'share_flowgram'),

    (r'^exporttovideo/check/(?P<export_to_video_request_id>\w+)/$', 'export_to_video_check'),
    (r'^export/youtube/(?P<export_to_video_request_id>\w+)/$', 'export_youtube_step1'),
    (r'^export/youtube/(?P<export_to_video_request_id>\w+)/2/$', 'export_youtube_step2'),
    (r'^export/youtube/(?P<export_to_video_request_id>\w+)/3/$', 'export_youtube_step3'),
    
    # search
    (r'^flowgramCSE/$', bypasslogin_to_template, {'template': 'search/flowgramContext.xml'}),
    (r'^flowgramCSEAnnotations/$', 'cse_xml'),
    (r'^flowgramCSEAnnotationsTest/$', bypasslogin_to_template, {'template': 'search/flowgramAnnotations.xml'}),
    (r'^search_results/$', bypasslogin_to_template, {'template': 'search/searchResults.html'}),
    # (r'^search_xml/$', bypasslogin_to_template, {'template': 'search/search_results.xml'}),
    
    
    #search result
    (r'^feedGoogle/$', 'feed_google'),
    (r'^feedGoogle.xml$', 'feed_google'),
    
    
    # browse section
    (r'^browse/featured/$', 'view_featured'),
    (r'^browse/mostviewed/$', 'view_most_viewed'),
    (r'^browse/discussed/$', 'view_most_discussed'), # let's remove this one asap
    (r'^browse/mostdiscussed/$', 'view_most_discussed'),
    (r'^browse/newest/$', 'view_newest'),
    (r'^browse/toprated/$', 'view_toprated'),
    (r'^browse/ajax/(?P<browse_type>\w+)/((?P<user>\w+)/)?$', 'view_ajax_browse'),
    
    # poll module
    (r'^ajax_poll_vote/$', 'handle_poll_submit'),
    
    # dialogs
    (r'^dialogs/video_promo/$', 'dialog_video_promo'),
    
    # promos
    (r'^promos/video_promo/$', 'video_promo'),
    
    # you section
    (r'^you/$', 'you'),
    
    # service dashboard
    (r'^dashboard/$', 'dashboard_index'),
    
    # create section
    (r'^create/$', 'create_easy'),
    (r'^create/bookmarklets/$', 'create_toolbar_landing'),
    (r'^create/create_continue/$', 'create_toolbar_continue'),
    (r'^create/terms_and_conditions/$', bypasslogin_to_template, {'template': 'create/terms_and_conditions.html'}),

    # about us section
    (r'^about_us/$', bypasslogin_to_template, {'template': 'about_us/about_flowgram.html'}),
    (r'^about_us/about_flowgram/$', bypasslogin_to_template, {'template': 'about_us/about_flowgram.html'}),
    (r'^about_us/press/$', 'view_press'),
    (r'^about_us/press/(?P<prid>\w+)/$', 'view_press'),
    #(r'^about_us/jobs/$', bypasslogin_to_template, {'template': 'about_us/jobs.html'}),
    (r'^about_us/jobs/$', 'jobs'),
    (r'^about_us/jobs/(?P<available_position>\w+)/$', 'jobs'),
    (r'^about_us/contact_us/$', bypasslogin_to_template, {'template': 'about_us/contact_us.html'}),
    (r'^about_us/contact_us/email/$', 'contact_us_email'),
    (r'^about_us/contact_us_confirm/$', bypasslogin_to_template, {'template': 'about_us/contact_us_confirm.html'}),
    (r'^about_us/news/$', bypasslogin_to_template, {'template': 'about_us/news.html'}),
    (r'^about_us/blog/$', bypasslogin_to_template, {'template': 'about_us/blog.html'}),
    #(r'^about_us/terms_of_service/$', bypasslogin_to_template, {'template': 'about_us/terms_of_service.html'}),
    #(r'^about_us/privacy_policy/$', bypasslogin_to_template, {'template': 'about_us/privacy_policy.html'}),
    (r'^about_us/terms_of_service/$', bypasslogin_to_template, {'template': 'about_us/terms_of_service.html'}),
    (r'^about_us/privacy_policy/$', bypasslogin_to_template, {'template': 'about_us/privacy_policy.html'}),
    (r'^about_us/copyright/$', bypasslogin_to_template, {'template': 'about_us/copyright.html'}),
    (r'^about_us/copyright_faq/$', bypasslogin_to_template, {'template': 'about_us/copyright_faq.html'}),
    
    # news section
    (r'^news/subscribe/$', bypasslogin_to_template, {'template': 'news/subscribe.html'}),
    (r'^news/already_on/$', bypasslogin_to_template, {'template': 'news/already_on.html'}),
    (r'^news/not_on/$', bypasslogin_to_template, {'template': 'news/not_on.html'}),
    (r'^news/subscribed/$', bypasslogin_to_template, {'template': 'news/subscribed.html'}),
    (r'^news/unsubscribed/$', bypasslogin_to_template, {'template': 'news/unsubscribed.html'}),
    (r'^news/email_confirm/$', bypasslogin_to_template, {'template': 'news/email_confirm.html'}),
    (r'^news/invalid_email/$', bypasslogin_to_template, {'template': 'news/invalid_email.html'}), 

    #website -> account management
    (r'^logout/$', 'my_logout'),
    (r'^login/$', 'login'),
    (r'^register/$', 'register'),
    (r'^register_steps/$', 'register_steps'),
    (r'^reg_success/(?P<next>\w+)/$', 'reg_success'),
    (r'^request_regcode/$', 'request_regcode'),
    (r'^password/$', 'change_password'),
    (r'^reset/$', bypasslogin_to_template, {'template': 'user/reset_password.html'}),
    (r'^reset_password_post/$', 'reset_password_post'),
    (r'^newpassword/$', 'reset_password_makenew'),
    (r'^editprofile/$', 'edit_profile'),
    (r'^edit_avatar/$', 'edit_avatar'),
    
    
    
    # System pages
    (r'^down_for_maintenance/$', bypasslogin_to_template, {'template': 'system/down_for_maintenance.html'}),
    
    # website dialogs
    (r'^dialogs/delete_fg/$', 'delete_flowgram'),
    
    # Admin pages
    (r'^a/inviter/$', 'inviter'),

    #subscriptions
    # view subscriptions --> Same view handles NotifyForm logic as well
    (r'^subscriptions/$', 'view_subscriptions'),
    (r'^(?P<username>\w+)/subscriptions/', 'view_subscriptions_redirect'),
    
    # update notification options
	(r'^updatenotifyoptions/$', 'view_subscriptions'),
        
    # show full newsfeed
    (r'^(?P<username>\w+)/newsfeed/', 'show_full_newsfeed'),
    
    # standalone page
    (r'^standalone/(?P<directory_name>\w+)/$', 'standalone_page'),
    (r'^standalone/(?P<directory_name>\w+)/(?P<page_name>\w+)/$', 'standalone_page'),
    
)

# flickr

urlpatterns += patterns('flowgram.core.flickr',
    (r'^flickr/callback/$', 'callback'),
    (r'^flickr/photosets_import/$', 'photosets_import'),
    (r'^flickr/create_fg_from_photoset/$', 'create_fg_from_photoset'),
)

# facebook

urlpatterns += patterns('flowgram.core.facebook',
    (r'^facebook/callback/$', 'callback'),
    (r'^facebook/albums_import/$', 'albums_import'),
    (r'^facebook/create_fg_from_aid/$', 'create_fg_from_aid'),
)

# picasaweb

urlpatterns += patterns('flowgram.core.picasaweb',
    (r'^picasaweb/callback/$', 'callback'),
  #  (r'^picasaweb/albums_import/$', 'albums_import'),
)

# photo service

urlpatterns += patterns('flowgram.core.photoservice',
    (r'^photoservice/getalbuminfo/$', 'get_album_info'),
    (r'^photoservice/getphotosforalbum/$', 'get_photos_for_album'),
    (r'^photoservice/importphotoswithidsinalbum/$', 'import_photos_with_ids_in_album'),
    (r'^photoservice/importphotoswithidsinsearchresult/$', 'import_photos_with_ids_in_searchresult'),
    (r'^photoservice/login/$', 'login'),
    (r'^photoservice/search/$', 'get_photos_for_search'),
)

# powerpoint

urlpatterns += patterns('flowgram.core.powerpoint',
    (r'^powerpoint/upload/$', 'upload'),
    (r'^powerpoint/check/$', 'check'),
    (r'^powerpoint/add_ppt_slide/$', 'add_ppt_slide')
)

# CMS pages (magic!)
from cms.models import CmsPage
for page in CmsPage.objects.all():
    urlpatterns += patterns('flowgram.cms.views', ("^cmspages/%s$" % page.urlpath, 'show_cms_page', {'id': page.id}))

# Help section pages
urlpatterns += patterns('flowgram.faq.views',
    (r'^help/$', 'help'),
    (r'^help/(?P<question_id>\w+)/$', 'help_article'),
)

# Tutorial section pages
urlpatterns += patterns('flowgram.tutorials.views',
    (r'^tutorials/$', 'tutorials_index'),
    (r'^tutorials/(?P<tutorial_id>\w+)/$', 'tutorial'),
)

#API: upload, download, toolbar
urlpatterns += patterns('flowgram.core.toolbar',
    (r'^tb/login/$', 'login'),
    (r'^tb/registerview/$', 'register_view'),
)

urlpatterns += patterns('flowgram.core.api.views',
    (r'^api/caneditfg/(?P<flowgram_id>\w+)/$', 'can_edit_fg'),
    
    # Page objects and HTML content
    (r'^api/addfeedback/$', 'add_feedback'),	
    (r'^api/addpage/$', 'add_page'),	
    (r'^api/getpage/(?P<page_id>\w+)/$', 'get_page'),
    (r'^api/getpage/(?P<page_id>\w+)/hl/$', 'get_highlighted_page'),	
    (r'^api/setpage/$', 'set_page'),		
    (r'^api/updatehighlight/$', 'update_highlight'),
    (r'^api/deletehighlight/$', 'delete_highlight'),
    (r'^api/getappinitdata/$', 'get_app_init_data'),
    (r'^api/savepage/$', 'save_page'),
    (r'^api/saveflowgram/$', 'save_flowgram'),
    (r'^api/movepages/$', 'move_pages'),
    (r'^api/removepages/$', 'remove_pages'),
    (r'^api/ajaxlogin/$', 'ajax_login'),
    (r'^api/exporttovideo/$', 'export_to_video'),
    (r'^api/removebackgroundaudio/$', 'remove_background_audio'),
    (r'^api/downloadforoffline/$', 'download_for_offline'),
    
    # Page thumbs and audio
    (r'^api/addaudiofms/$', 'add_audio_fms'),
    (r'^api/updateaudio/$', 'update_audio'),
    (r'^api/deleteaudio/$', 'delete_audio'),
    (r'^api/clearaudio/$', 'clear_audio'),		
    (r'^api/clearhighlights/$', 'clear_highlights'),
    (r'^api/getthumb/(?P<page_id>\w+)/$', 'get_thumb'),
    (r'^api/getthumbbydims/fg/(?P<flowgram_id>\w+)/(?P<width>\d+)/(?P<height>\d+)/$', 'get_fg_thumb_by_dims'),
    (r'^api/getthumbbydims/(?P<page_id>\w+)/(?P<width>\d+)/(?P<height>\d+)/$', 'get_thumb_by_dims'),
    
    (r'^api/recordstat/$', 'record_stat'),
    (r'^api/recordbulkstats/$', 'record_bulk_stats'),
    
    # Flowgram objects
    (r'^api/createfg/$', 'create_flowgram'),	
    (r'^api/deletefg/$', 'delete_flowgram'),	
    (r'^api/setfgtitle/(?P<flowgram_id>\w+)/$', 'set_fg_title'),
    (r'^api/setfgdesc/(?P<flowgram_id>\w+)/$', 'set_fg_desc'),
    (r'^api/setworkingfg/$', 'set_working_flowgram'),
    (r'^api/getfg/(?P<flowgram_id>\w+)/$', 'get_fg'),
    (r'^api/getfgspaginated/$', 'get_fgs_paginated'),
    (r'^api/getfavoritefgspaginated/$', 'get_favorite_fgs_paginated'),
    (r'^api/getmorefgspaginated/$', 'get_more_fgs_paginated'),
    (r'^api/changeprivacy/$', 'change_privacy'),
    (r'^api/saveas/$', 'save_as'),
    (r'^api/addfavorite/$', 'add_favorite'),
    (r'^api/removefavorite/$', 'remove_favorite'),
    (r'^api/savecustompage/$', 'save_custom_page'),
    
    (r'^api/senddoneemail/$', 'send_editbar_done_email'),
    (r'^api/q-addurl/$', 'queue_add_url'),
    (r'^api/q-addpageprocessed/$', 'post_queue_add_page'),

    # Website Admin Tools
    (r'^api/admindisplayinnewest/$', 'admin_display_in_newest'),

    # User Info
    (r'^api/getfgavatar-(?P<size>\d+)/(?P<flowgram_id>\w+)/$', 'get_fg_avatar'),
    (r'^api/getworkingfg/$', 'get_working_fg'),
    (r'^api/saverating/$', 'save_rating'),
    
    
    # Importers
    (r'^api/import/rss/$', 'import_rss'),

    # File Uploader
    (r'^api/upload/$', 'file_upload'),
    
    (r'^api/checkall/$', 'check_all'),
    
    # Misc
    (r'^api/share/$', 'share'),
    (r'^api/getcommentspaginated/$', 'get_comments_paginated'),
    (r'^api/invite/$', 'invite'),

    (r'^api/logerror/$', 'log_error'),
    
    # subscriptions
    # add subscription
    (r'^subscribe/(?P<subscribe_to_username>\w+)/', 'create_subscription'), 
    
    # delete subscription
    (r'^unsubscribe/(?P<subscribed_to_username>\w+)/', 'remove_subscription'),
)

from localsettings import my_DEV_STATIC_MEDIA, MEDIA_ROOT, my_DEV_STATIC_ADMIN_MEDIA

# Bookmark Javascript files
urlpatterns += patterns('',
    (r'^bj/Bookmarklet.js$', 'flowgram.core.views.bm_js_maker'),
    (r'^bj/BookmarkletAdd.js$', 'flowgram.core.views.bm_js_quickadd'),
    (r'^bj/AddURL.js$', 'flowgram.core.views.addurl_js'),

)

# IE Bookmarklets
urlpatterns += patterns('',
    (r'^bookmarklets/Flowgram Maker.url$', bypasslogin_to_template, {'template': 'bookmarklets/Flowgram Maker.url', 'extra_context': {'domain_name': localsettings.MASTER_DOMAIN_NAME}}),
    (r'^bookmarklets/Quick Add Page.url$', bypasslogin_to_template, {'template': 'bookmarklets/Quick Add Page.url', 'extra_context': {'domain_name': localsettings.MASTER_DOMAIN_NAME}}),
)

# Bookmarklet source
urlpatterns += patterns('',
    (r'^bookmarklets/maker.js$', bypasslogin_to_template, {'template': 'bookmarklets/maker.js', 'extra_context': {'domain_name': localsettings.MASTER_DOMAIN_NAME}}),
    (r'^bookmarklets/qa.js$', bypasslogin_to_template, {'template': 'bookmarklets/qa.js', 'extra_context': {'domain_name': localsettings.MASTER_DOMAIN_NAME}}),
)

# Admin page and user homepages
urlpatterns += patterns('',
    #robots.txt
    (r'^robots.txt$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA, 'path': 'robots.txt'}),
    
    #favicon
    (r'^favicon.ico$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA + 'images/', 'path': 'favicon.ico'}),

    #crossdomain.xml
    (r'^crossdomain.xml$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA + 'swf/', 'path': 'crossdomain.xml'}),
    
    #admin
    (r'^adminfeatured/$', 'flowgram.core.views.admin_featured'),
    (r'^adminnewest/$', 'flowgram.core.views.admin_newest'),
    (r'^adminpolls/$', 'flowgram.core.views.admin_polls'),
    (r'^adminfiles/$', 'flowgram.core.views.admin_files'),
    (r'^adminfiles/delete/(?P<file_to_delete>\w+)/$', 'flowgram.core.views.admin_files'),
    (r'^adminpolls/(?P<current_poll_id>\w+)$', 'flowgram.core.views.admin_polls'),
    (r'^adminpress/$', 'flowgram.core.views.admin_press'),
    (r'^adminpress/(?P<current_press_id>\w+)$', 'flowgram.core.views.admin_press'),
    (r'^adminpress/(?P<current_press_id>\w+)/delete/$', 'flowgram.core.views.delete_press'),
    (r'^admintutorials/$', 'flowgram.tutorials.views.admin_tutorials'),
    (r'^admintutorials/edit/(?P<tutorial_id>\w+)/$', 'flowgram.tutorials.views.admin_tutorials'),
    (r'^admintutorials/delete/(?P<tutorial_id>\w+)/$', 'flowgram.tutorials.views.delete_tutorial'),
    (r'^admin/', include('django.contrib.admin.urls')),
    
    #catchall for pretty homepages -- make sure this and the next one are last!
    (r'^(?P<username>\w+)/$', 'flowgram.core.views.show_user_by_name'),
    (r'^(?P<username>\w+)/new_fg_user/$', 'flowgram.core.views.show_user_by_name'),
	
    #view your flowgrams thumb
    (r'^(?P<username>\w+)/viewyourflowgramsthumb/(?P<sort_criterion>\w+)/(?P<prpusort>\w+)', 'flowgram.core.views.view_your_flowgrams_thumb'),
    (r'^(?P<username>\w+)/viewyourflowgramsthumb/((?P<sort_criterion>\w+)/)?$', 'flowgram.core.views.view_your_flowgrams_thumb_redirect'),
    
    #view a user's favorites
    (r'^(?P<username>\w+)/favorites/(?P<sort_criterion>\w+)/(?P<prpusort>\w+)', 'flowgram.core.views.view_favorites'),
    (r'^(?P<username>\w+)/favorites/((?P<sort_criterion>\w+)/)?$', 'flowgram.core.views.view_favorites_redirect'),
)


# This can be used for creating temporary files for doing things such as verifying site ownership.
urlpatterns += patterns('',
    (r'^google0cb09ece475e7bb6.html$', bypasslogin_to_template, {'template': 'blank.html'}),
    (r'^google68f47c71bbbc562a.html$', bypasslogin_to_template, {'template': 'blank.html'}),
    (r'^google4360811b3f4a80da.html$', bypasslogin_to_template, {'template': 'blank.html'}),
)



#static files (for development only)
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^flex/(?P<path>.*)$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA + 'flex/'}),
        (r'^f/(?P<path>.*)$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA + 'flex/'}),
        (r'^widget/(?P<path>.*)$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA + 'widget/'}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_MEDIA}),
        (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': my_DEV_STATIC_ADMIN_MEDIA}),
        (r'^avatars/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'avatars/'}),
        (r'^thumbs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'thumbs/'}),
        (r'^powerpoint/(?P<path>.*)$', 'django.views.static.serve', {'document_root': localsettings.POWERPOINT_DIR}),
        (r'^intmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': localsettings.INTERNAL_MEDIA_ROOT}),
    )

