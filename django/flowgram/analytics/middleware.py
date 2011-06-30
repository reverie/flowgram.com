from flowgram.analytics.models import PageView  
class AnalyticsMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            # Exclude staff from logs:
            if request.user.is_staff:
                return
            else:
                user = request.user
        else:
            user = None
            
        # Exclude keynote from logs
        if request.META.get('HTTP_USER_AGENT', '').find('KTXN') != -1:
            return
         
        view = view_func.__name__
        ip = request.META.get('REMOTE_ADDR', '')
        referer = request.META.get('HTTP_REFERER', '')
        url = request.path
        qs = request.META.get('QUERY_STRING', '')
        if qs:
            url += '?' + qs
        url = url[:300]
        PageView.objects.create(url=url, referer=referer, user=user, ip=ip, view=view)