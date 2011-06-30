from flowgram.core.forms import LoginForm
from flowgram.core.helpers import is_down_for_maintenance

def login_form(request):
    context = {}
    if request.user.is_authenticated():# or request.path == '/login/':
        return context
    #print "Checking for processed_login_form in session",
    if 'processed_login_form' in request.session.keys():
        #print "... found processed_login form (removing)"
        #print request.session['processed_login_form']
        context['login_form'] = request.session['processed_login_form']
        del request.session['processed_login_form']
    else:
        #print "processed login form not found (generating new)"
        context['login_form'] = LoginForm().as_p()
    return context
    
#def on_beta(request):
    #beta = False
    #try:
        #str(request.get_host()).index('beta')
        #beta = True
    #except:
        #pass
    #return {'on_beta': beta}

#def newsfeed(request):
    #from flowgram.core.feed import user_messages, global_messages
    #context = {}
    #if request.user.is_authenticated():
        #context['news_items'] = user_messages(request.user)[:6]
        #context['news_type'] = 'user'
    #else:
        #context['news_items'] = global_messages()[:6]
        #context['news_type'] = 'global'
    #return context
    
def active_tab(request):

    # Get the first 'word' of the URL path:
    pageroot = request.path.split('/')[1]
    if len(request.path.split('/')) > 2:
        pagesecondary = request.path.split('/')[2]
    else:
        pagesecondary = ''

    default = ''
    
    # PAGE HEADERS
    # home
    if pageroot == '':
        pageheader='home'
    elif pageroot == 'register':
        pageheader='register'
    
    # browse
    elif pageroot == 'fg':
        pageheader='browse'
    elif pageroot == 'browse':
        pageheader='browse'
    
    # create
    elif pageroot == 'create':
        pageheader='create'
    
    else:
        pageheader = default
    
    # GLOBAL LEVEL
    # home
    if pageroot == '':
        active='home'
    elif pageroot == 'register':
        active='home'
    
    # browse
    elif pageroot == 'fg':
        active='browse'
    elif pageroot == 'browse':
        active='browse'
    
    # manage
    elif pageroot == 'you': # TODO(cyap) get rid of this, or do something else w/ it
        active='you'
    #elif pageroot == 'editprofile':
        #active='you'
    elif pageroot == 'viewyourflowgramsthumb':
        active='you'
    elif pageroot == 'viewyourflowgramslist':
        active='you'
    elif pageroot == 'password':
        active='you'
    elif pageroot == 'edit_avatar':
        active='you'
    
    # create
    elif pageroot == 'create':
        active='create'
    
    # help
    elif pageroot == 'help':
        active='help'
    
    else:
        active = default
    
    # SECONDARY LEVEL
    
    # browse
    if pagesecondary == 'featured':
        activesecondary='featured'
    elif pagesecondary == 'mostviewed':
        activesecondary='mostviewed'
    elif pagesecondary == 'discussed': # let's get rid of this one asap
        activesecondary='discussed'
    elif pagesecondary == 'mostdiscussed':
        activesecondary='mostdiscussed'
    elif pagesecondary == 'newest':
        activesecondary='newest'
    elif pagesecondary == 'mostactive':
        activesecondary='mostactive'
    elif pagesecondary == 'toprated':
        activesecondary='toprated'
    
    # about us
    elif pagesecondary == 'about_flowgram':
        activesecondary='aboutflowgram'
    elif pagesecondary == 'jobs':
        activesecondary='jobs'
    elif pagesecondary == 'contact_us':
        activesecondary='contactus'
    elif pagesecondary == 'blog':
        activesecondary='blog'
    elif pagesecondary == 'press':
        activesecondary='press'
    elif pagesecondary == 'terms_of_service':
        activesecondary='termsofservice'
    elif pagesecondary == 'privacy_policy':
        activesecondary='privacypolicy'
    elif pagesecondary == 'copyright':
        activesecondary='copyright'
    elif pagesecondary == 'copyright_faq':
        activesecondary='copyrightfaq'
    
    # your flowgrams
    elif pageroot == 'editprofile':
        activesecondary='profile'
        
    else:
        activesecondary = default

    return {'active': active, 'activesecondary': activesecondary}

from django.contrib.csrf.middleware import _make_token
from django.conf import settings
def csrf_token(request):
    try:
        session_id = request.COOKIES[settings.SESSION_COOKIE_NAME]
    except KeyError:
        return {}
    csrf_token = _make_token(session_id)
    return {'csrf_token' : csrf_token}
    
