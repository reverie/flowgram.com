from flowgram.core import helpers, webhelpers
from flowgram.core.web.admin import admin_featured, admin_newest, admin_polls, admin_press, \
                                        delete_press, inviter, admin_files
from flowgram.core.web.auth import login, my_logout
from flowgram.core.web.comments import add_comment, delete_comment
from flowgram.core.web.create import create_easy, create_toolbar_continue, create_toolbar_landing
from flowgram.core.web.index import index, index_logged_in
from flowgram.core.web.export_to_video import export_to_video_check, export_youtube_step1, \
                                                  export_youtube_step2, export_youtube_step3
from flowgram.core.web.flowgrams import delete_flowgram, edit_flowgram_description, \
                                            edit_flowgram_title, share_flowgram, show_flowgram
from flowgram.core.web.more_flowgrams import view_ajax_browse, view_favorites, view_featured, \
                                                 view_most_discussed, view_most_viewed, \
                                                 view_newest, view_toprated
from flowgram.core.web.newsfeed import rss_newsfeed, rss_newsfeed_private, show_full_newsfeed
from flowgram.core.web.password import change_password, reset_password_makenew, reset_password_post
from flowgram.core.web.redirects import details_redirect, flag_flowgram, get_css, goto_quick_link, \
                                            show_shared_flowgram, view_favorites_redirect, \
                                            view_your_flowgrams_thumb_redirect, \
                                            widget_play_flowgram, you
from flowgram.core.web.registration import register, register_steps, reg_success, request_regcode
from flowgram.core.web.search import feed_google, search
from flowgram.core.web.standalone import standalone_page
from flowgram.core.web.tags import add_tag, delete_tag
from flowgram.core.web.user_profile import show_user, show_user_by_id, show_user_by_name
from flowgram.core.web.you import view_your_flowgrams_thumb



import itertools, random, re, datetime, StringIO, Image, string

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.template.loader import render_to_string

from flowgram import settings, localsettings
from flowgram.core import avatar, log, controller, cached_sets, permissions, s3
from flowgram.core.decorators import authorized, analytics_check_anon_create

from flowgram.core.forms import ProfileForm, RegistrationForm, ChangePasswordForm, NotifyForm
from flowgram.core.models import UserProfile, Flowgram, Comment, Tag, Page, Favorite, Audio, Regcode, feat, feat_fullname, QuickLink, GetCssRequest, StatusCode, UploadedFile, FlowgramPoll, FlowgramPress, Subscription, UploadToYouTubeRequest, ExportToVideoRequest, EmailSubscriptionRequest
from flowgram.core.helpers import add_good_message, add_bad_message, go_back, req_render_to_response, redirect
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue
from flowgram.core.exporters.video import uploadtoyoutube

from flowgram.core.require import require
from flowgram.core.response import data_response, error_response
from django.views.generic.list_detail import object_list


subs_active = localsettings.FEATURE['subscriptions_fw'] # feature flag for subs...
send_to_details = localsettings.FEATURE['send_to_details'] # using details page as main access point to FGs


@authorized 
def show_tag(request, tag_name):
    tags = Tag.objects.filter(name=tag_name).order_by('-flowgram', '-created_at')
    fgs = []
    previous_fgid = ''
    current_fgid = ''
    for tag in tags:
        fg = tag.flowgram
        current_fgid = tag.flowgram.id
        if current_fgid != previous_fgid:
            fgs.append(tag.flowgram)
        previous_fgid = current_fgid
        
    return req_render_to_response(request, 'flowgram/show_tag.html', {
        'name': tag_name,
        'fgs': fgs,
        'send_to_details': localsettings.FEATURE['send_to_details'],
    })

@vary_on_headers('User-Agent')
def play_flowgram(request, flowgram_id, hash=None):
    log.debug("user agent found : play_flowgram" + request.META.get("HTTP_USER_AGENT", ""))
    user_agent=request.META.get("HTTP_USER_AGENT", "")
    if user_agent.lower().find(settings.GOOGLEBOT_UA) >= 0:
        # it is robot, need to find out yahoo robot too
        return HttpResponse(controller.reponse_non_user_agent(flowgram_id, hash)) 
    else:
        # it is real user
        #fg = get_object_or_404(Flowgram, pk=flowgram_id)
        #return HttpResponseRedirect(fg.play_url(hash))
        return HttpResponse(controller.html_for_static_flex_file('p.html'))


@login_required
def edit_profile(request):
    u = request.user
    p = u.get_profile()
    if request.method == 'GET':
        initial = {
            'gender': p.gender,
            'newsletter_optin': p.newsletter_optin,
            'birthdate': p.birthdate,
            'homepage': p.homepage,
            'email': u.email,
            'description': p.description,
            #'subscribe_fg_on_comment': p.subscribe_fg_on_comment,
            #'subscribed_to_own_fgs': p.subscribed_to_own_fgs,
        }
        f = ProfileForm(initial=initial)
        return req_render_to_response(request, 'user/edit_profile.html', {
            'profile': p,
            'form': f,
            'subs_active': subs_active,
        })
    elif request.method == 'POST':
        f = ProfileForm(request.POST)
        if f.is_valid():
            cleaned = f.cleaned_data
            p.gender = cleaned['gender']
            p.newsletter_optin = cleaned['newsletter_optin']
            p.birthdate = cleaned['birthdate']
            p.homepage = cleaned['homepage']
            p.description = cleaned['description']
            #p.subscribe_fg_on_comment = cleaned['subscribe_fg_on_comment']
            #p.subscribed_to_own_fgs = cleaned['subscribed_to_own_fgs']
            p.save()
            u.email = cleaned['email']
            u.save()
            add_good_message(request, "Your profile was updated.")
            controller.record_stat(request, 'edit_profile_website', '0', '')
            EmailSubscriptionRequest.objects.create(should_subscribe=p.newsletter_optin, email_address=u.email)
        return HttpResponseRedirect(p.url())


from flowgram.core.avatar import BUILTIN_AVATARS
from flowgram.core.forms import AvatarForm
@login_required
def edit_avatar(request):
    random.shuffle(BUILTIN_AVATARS)
    form = AvatarForm()
    if request.method == 'POST':
        if "upload_form" in request.POST.keys():
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                avatar.save_uploaded_avatar(request.user.get_profile(), form)
        else: # if "builtin_form" in request.POST.keys():
            builtin_name = request.POST['name']
            if builtin_name != 'XXX':  
                p = request.user.get_profile()
                avatar.save_builtin_avatar(p, builtin_name)

    return req_render_to_response(request, "user/edit_avatar.html", {
        'form': form,
        'builtin_avatars' : BUILTIN_AVATARS,
    })



@vary_on_headers('User-Agent')
def nojs(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    (browser, version) = webhelpers.get_brower_and_version(request)
    return req_render_to_response(request,
                                  "system/nojs.html",
                                  {'domain_name': localsettings.MASTER_DOMAIN_NAME, 
                                   'browser': browser,
                                   'browser_version': version})


    
def send_javascript_with_csrf(request, template_name):
    from flowgram.core import contexts
    context = contexts.csrf_token(request)
    return render_to_response(template_name, context, mimetype="text/javascript")

def bm_js_maker(request):
    return send_javascript_with_csrf(request, 'js/Bookmarklet.js')
bm_js_quickadd = bm_js_maker


def addurl_js(request):
    return send_javascript_with_csrf(request, 'js/AddURL.js')

def view_press(request, prid=''):
    press_list = FlowgramPress.objects.filter().order_by('-link_date')
    fgpr_press_list = press_list.filter(press_category='R')
    featured_press_list = press_list.filter(press_category='F')
    more_press_list = press_list.filter(press_category='M')
    press_display = 'index'
    
    if not prid == '':
        press_display = 'pr'
        pr = FlowgramPress.objects.get(id=prid)
        return req_render_to_response(request, 'about_us/press.html', {
            'pr': pr,
            'press_display': press_display,
        })
    
    return req_render_to_response(request, 'about_us/press.html', {
        'fgpr_press_list': fgpr_press_list,
        'featured_press_list': featured_press_list,
        'more_press_list': more_press_list,
        'press_display': press_display,
    })

    

@login_required
def handle_poll_submit(request):
    if not request.method == 'POST':
        log.sec_req(request, "Tried to hit poll submit URL by GET.")
        raise Http404
    
    poll_id = request.POST['poll_id']
    vote_id = request.POST['vote_id']
    current_poll = FlowgramPoll.objects.get(id=poll_id)
    
    # increment votes and save
    if vote_id == current_poll.candidate_id_1:
        current_poll.votes_1 += 1
    elif vote_id == current_poll.candidate_id_2:
        current_poll.votes_2 += 1
    elif vote_id == current_poll.candidate_id_3:
        current_poll.votes_3 += 1
    current_poll.save()
    
    current_poll_fg1 = Flowgram.objects.get(id=current_poll.candidate_id_1)
    current_poll_fg2 = Flowgram.objects.get(id=current_poll.candidate_id_2)
    current_poll_fg3 = Flowgram.objects.get(id=current_poll.candidate_id_3)
    
    return req_render_to_response(request, 'includes/modules/other_content/poll_module_results.incl', {
        'current_poll': current_poll,
        'current_poll_fg1': current_poll_fg1,
        'current_poll_fg2': current_poll_fg2,
        'current_poll_fg3': current_poll_fg3,
    })
     
def jobs(request, available_position=''):
    if available_position == '':
        position = ''
    elif available_position == '/':
        position = ''
    elif available_position == 'appdev':
        position = 'appdev'
    elif available_position == 'producer':
        position = 'producer'
    else:
        position = ''
    return req_render_to_response(request, "about_us/jobs.html", {
        'position': position,
    })

def contact_us_email(request):
    if request.method != 'POST':
        return req_render_to_response(request, 'about_us/contact_us_email.html')
    name = request.POST.get('name', '')
    if name == '':
        name='Anonymous'
    email = request.POST.get('email', '')
    subject = request.POST.get('subject', '')
    if subject == '':
        subject='I am not big on typing or words.'
    comments = request.POST.get('comments', '') 
    controller.record_stat(request, 'add_feedback_website', '0', '')      
    add_to_mail_queue(
        'mailman@flowgram.com',
        'feedback@flowgram.com',
        'Contact via FG Contact Us/Feedback form',
        'FROM: %s <%s> | SUBJECT: %s | COMMENTS: %s' % (name, email, subject, comments))
    return HttpResponseRedirect('/about_us/contact_us_confirm/')

def cse_xml(request):
    xml = render_to_string('search/fgAnnotations.xml', {
        'fgs': Flowgram.from_published.all(),
        'host' : localsettings.MASTER_DOMAIN_NAME
      })
    return HttpResponse(xml, mimetype="text/xml")

##give flowgram source for google search


#===== Dialogs ===
def dialog_video_promo(request):
    return req_render_to_response(request, 'dialogs/video_promo.html', {
        's3_bucket_static': localsettings.S3_BUCKETS[localsettings.S3_BUCKET_STATIC],
    })


#===== Promos ===
def video_promo(request):
    return req_render_to_response(request, 'promos/video_promo.html', {
        'posts': webhelpers.get_latest_fg_blog_posts(),
        'tip': cached_sets.get_a_tip(),
        's3_bucket_static': localsettings.S3_BUCKETS[localsettings.S3_BUCKET_STATIC],
    })
    
    

#===== Subscriptions & Notifications ===

# TODO(cyap): this is temporary to handle the url changes I made to view_subscriptions -- chris
@login_required
def view_subscriptions_redirect(request, username=''):
    return HttpResponseRedirect('/subscriptions/')

@login_required   
def view_subscriptions(request):
    u = request.user
    p = u.get_profile() 
                   
    if request.method == 'POST':
        f = NotifyForm(request.POST)
        if f.is_valid():
            cleaned = f.cleaned_data
            p.notification_freq = cleaned['notification_freq']
            p.notify_by_email = cleaned['notify_by_email']
            p.has_public_news_feed = cleaned['has_public_news_feed']
            p.save()
            url = "/subscriptions/"
            add_good_message(request, "Your settings have been successfully updated.")
        return HttpResponseRedirect(url)

    
    initial = {
        'notification_freq': p.notification_freq,
        'notify_by_email': p.notify_by_email,
        'has_public_news_feed': p.has_public_news_feed,
    }
    f = NotifyForm(initial=initial)
    
    # Get User profiles items from list of subscriptions
    user_subscriptions = controller.get_user_subscriptions(u)
    subscription_profiles = []
    for sub in user_subscriptions:
        subscription_user = UserProfile.objects.get(user=sub["user"])
        avatar_url= UserProfile.avatar_100(subscription_user)
        subscription_profiles.append({'username':subscription_user.user,'avatar_url':avatar_url})

    # Get User profiles items from list of subscribers
    subscribers = controller.get_user_subscribers(u)    
    subscriber_profiles = []
    for sub in subscribers:
        subscriber_user = UserProfile.objects.get(user=sub["subscriber"])
        avatar_url= UserProfile.avatar_100(subscriber_user)
        subscriber_profiles.append({'username':subscriber_user.user,'avatar_url':avatar_url})


    # For secondary nav include
    activesecondary = 'subscriptions'

    show_unsubscribe = True
    
    return req_render_to_response(request, 'user/view_subscriptions.html', {
        'subscription_profiles':subscription_profiles,
        'activesecondary': activesecondary,
        'subs_active':subs_active,
        'profile':p,
        'form': f,
        'u':u,
        'show_unsubscribe': show_unsubscribe,
        'subscriber_profiles':subscriber_profiles,
        'mostviewed': cached_sets.most_viewed()[:6],
    })
    
    
from flowgram.core.models import DashboardServiceRecord
#===== Dashboard ===

@require('GET', [], ['staff'])
def dashboard_index(request):
    error_records = []
    pass_records = []
    records = DashboardServiceRecord.objects.all()
    if not records:
       log.debug('dashboard service recorder not running, check servicechecker.py in /flowgram/flowgram/core/dashboard')
       
    for record in records:
        if record.service_status == False:
            error_records.append(record)
        else:
            pass_records.append(record)
            
    return req_render_to_response(request, "dashboard/index.html", {
        'error_records': error_records,
        'pass_records':pass_records
    })
     