import datetime, sys

from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import patch_vary_headers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from flowgram.core import log


# DualSessionMiddleware copied and modified from the web -andrew
class DualSessionMiddleware(object):
    """Session middleware that allows you to turn individual browser-length 
    sessions into persistent sessions and vice versa.
    
    This middleware can be used to implement the common "Remember Me" feature
    that allows individual users to decide when their session data is discarded.
    If a user ticks the "Remember Me" check-box on your login form create
    a persistent session, if they don't then create a browser-length session.
    
    This middleware replaces SessionMiddleware, to enable this middleware:
    - Add this middleware to the MIDDLEWARE_CLASSES setting in settings.py, 
      replacing the SessionMiddleware entry.
    - In settings.py add this setting: 
      PERSISTENT_SESSION_KEY = 'sessionpersistent'
    - Tweak any other regular SessionMiddleware settings (see the sessions doc),
      the only session setting that's ignored by this middleware is 
      SESSION_EXPIRE_AT_BROWSER_CLOSE. 
      
    Once this middleware is enabled all sessions will be browser-length by
    default.
    
    To make an individual session persistent simply do this:
    
    session[settings.PERSISTENT_SESSION_KEY] = True
    
    To make a persistent session browser-length again simply do this:
    
    session[settings.PERSISTENT_SESSION_KEY] = False
    """
    def __init__(self):
        self.session_wrapper = SessionMiddleware()
    
    def process_request(self, request):
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)

        if session_key == None:
            session_key = request.POST.get(settings.SESSION_COOKIE_NAME, None)
            
            if session_key == None:
                session_key = request.GET.get(settings.SESSION_COOKIE_NAME, None)
                
            if session_key != None:
                request.COOKIES[settings.SESSION_COOKIE_NAME] = session_key
            
        return self.session_wrapper.process_request(request)

    def process_response(self, request, response):
        # If request.session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        patch_vary_headers(response, ('Cookie',))
        try:
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                session_key = request.session.session_key or Session.objects.get_new_session_key()
                
                if not request.session.get(settings.PERSISTENT_SESSION_KEY, False):
                    # session will expire when the user closes the browser
                    max_age = None
                    expires = None
                else:
                    max_age = settings.SESSION_COOKIE_AGE
                    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
                
                new_session = Session.objects.save(session_key, 
                                                   request.session._session,
                                                   datetime.datetime.now() + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE))
                response.set_cookie(settings.SESSION_COOKIE_NAME, session_key,
                                    max_age = max_age, expires = expires, 
                                    domain = settings.SESSION_COOKIE_DOMAIN,
                                    secure = settings.SESSION_COOKIE_SECURE or None)
        return response


from django.contrib.csrf.middleware import CsrfMiddleware

def excluded(request):
    # Exclude if not POST
    if request.method != 'POST':
        return True

    # Exclude if user is unauthenticated:
    # This won't work because the user object hasn't been created yet. We can't
    # move csrf to after Session/Auth middleware in the middleware list either,
    # because then the form-processing won't work. TODO(andrew): split our custom
    # csrf middleware into separate request+response parts to handle this
    #if not request.user.is_authenticated():
    #    return True

    # Exclude based on path
    path = request.path
    if path.startswith('/api/addpage/') or \
       path.startswith('/api/addupage/') or \
       path.startswith('/api/getappinitdata/') or \
       path.startswith('/register/') or \
       path.startswith('/api/ajaxlogin/') or \
       path.startswith('/api/caneditfg/') or \
       path.startswith('/login/') or \
       path.startswith('/request_regcode/') or \
       path.startswith('/api/logerror/') or \
       path.startswith('/request_regcode') or \
       path.startswith('/api/q-addpageprocessed/') or\
       path.startswith('/i/') or\
       path.startswith('/powerpoint/add_ppt_slide/'):
        return True

    return False

class CustomCsrfMiddleware(CsrfMiddleware):
    def process_request(self, request):
        if excluded(request):
            return None
        
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)

        session_key = request.POST.get(settings.SESSION_COOKIE_NAME, session_key)
        session_key = request.GET.get(settings.SESSION_COOKIE_NAME, session_key)
                
        if session_key != None:
            request.COOKIES[settings.SESSION_COOKIE_NAME] = session_key
        
        request_csrf_token = request.POST.get('csrfmiddlewaretoken', None)
        if request_csrf_token == None:
            request_csrf_token = request.GET.get('csrfmiddlewaretoken', None)
            
            if request_csrf_token != None:
                request.POST['csrfmiddlewaretoken'] = request_csrf_token
        
        response = super(CustomCsrfMiddleware, self).process_request(request)
        if response:
            log.error("403 error on " + request.path)
            r = render_to_response('500.html')
            r.status_code = 500
            return r

from flowgram.core.helpers import is_down_for_maintenance
from django.shortcuts import render_to_response

class DownForMaintenanceMiddleware(object):
    def process_request(self, request):
        if is_down_for_maintenance(request):
            return render_to_response('system/down_for_maintenance.html', {})

        
        
# ProfileMiddleware taken and modified from the web -andrew
# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team
# Andrew added SQL logging output

import sys, os, re, hotshot, hotshot.stats, tempfile, StringIO, pprint

from django.conf import settings


words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]

class ProfileMiddleware(object):
    """
    From http://www.djangosnippets.org/snippets/605/
    
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def process_request(self, request):
        from django.db import connection
        if (settings.DEBUG or request.user.is_superuser) and request.has_key('prof'):
            connection.queries = []
            self.tmpfile = tempfile.mktemp()
            self.prof = hotshot.Profile(self.tmpfile)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG or request.user.is_superuser) and request.has_key('prof'):
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall( file )
            if name:
                return name[0]

    def get_summary(self, results_dict, sum):
        list = [ (item[1], item[0]) for item in results_dict.items() ]
        list.sort( reverse = True )
        list = list[:40]

        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        sum = 0

        for s in stats_str:
            fields = words_re.split(s);
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]

                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time

                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[ group ] = 0
                mygroups[ group ] += time

        return "<pre>" + \
               " ---- By file ----\n\n" + self.get_summary(mystats,sum) + "\n" + \
               " ---- By group ---\n\n" + self.get_summary(mygroups,sum) + \
               "</pre>"

    def process_response(self, request, response):
        from django.db import connection
        if (settings.DEBUG or request.user.is_superuser) and request.has_key('prof'):
            self.prof.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

            response.content = "\n".join(response.content.split("\n")[:40])

            response.content += self.summary_for_files(stats_str)
            
            response.content += '\n%d SQL Queries:\n' % len(connection.queries)
            response.content += pprint.pformat(connection.queries)
            response['content-type'] = 'text/html; charset=utf-8'

            os.unlink(self.tmpfile)

        return response 