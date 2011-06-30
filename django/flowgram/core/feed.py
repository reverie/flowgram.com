"""This file is deprefecated. Leaving it here for a bit in case we change our minds
about killing the newsfeed. -andrew, 4/30/08"""


#import itertools

#from django.conf import settings
#from django.core.cache import cache

#from flowgram import urlbuilder
#from flowgram.core import log
#from flowgram.core.models import Flowgram, Comment

#CACHE_PREFIX = settings.CACHE_MIDDLEWARE_KEY_PREFIX
#EXPIRATION = 30

#def render_flowgram(flowgram):
    #user_link = urlbuilder.link_to_user(flowgram.owner)
    #fg_link = urlbuilder.link_to_flowgram_details(flowgram)
    #return "%s created a new Flowgram: %s" % (user_link, fg_link)

#def render_comment(comment):
    #if comment.owner.username != 'Anonymous':
        #user_link = urlbuilder.link_to_user(comment.owner)
    #else:
        #user_link = 'Anonymous'
    #fg_link = urlbuilder.link_to_flowgram_details(comment.flowgram)
    #return "%s commented on %s" % (user_link, fg_link)

#def render_and_merge(flowgrams, comments):
    ## This function copied and modified from http://en.literateprograms.org/Merge_sort_(Python)
    ## -andrew
    #flowgrams = flowgrams.select_related('owner')
    #comments = comments.select_related('owner')
    #result = []
    #i ,j = 0, 0
    #while (i < len(flowgrams)) and (j < len(comments)):
        #f = flowgrams[i]
        #c = comments[j]
        #if (flowgrams[i].published_at <= comments[j].created_at):
            #result.append(render_flowgram(flowgrams[i]))
            #i = i + 1
        #else:
            #result.append(render_comment(comments[j]))
            #j = j + 1
    #result += map(render_flowgram, flowgrams[i:])
    #result += map(render_comment, comments[j:])
    #return result

#def user_messages(user):
    #p = user.get_profile()

    #flowgrams = Flowgram.objects.filter(owner__in=p.user_subscriptions.all())
    #if p.subscribed_to_self:
        #flowgrams |= user.flowgram_set.all()
    #flowgrams = flowgrams.filter(published=True).order_by('-published_at')[:10]
        
    #comments = Comment.objects.filter(flowgram__in=p.flowgram_subscriptions.all())  
    #if p.subscribed_to_own_fgs:
        #comments |= Comment.objects.filter(flowgram__in=user.flowgram_set.all())
    #comments = comments.exclude(owner=user).order_by('-created_at')[:10]

    #return render_and_merge(flowgrams, comments)

#def global_messages():
    #cache_key = CACHE_PREFIX+":feed:global_messages"
    #messages = cache.get(cache_key)
    #if messages is None:
        #log.cache_miss(cache_key)
        #flowgrams = Flowgram.from_published.filter(public=True).order_by('-published_at')[:10]
        #comments = Comment.objects.filter(flowgram__public=True).order_by('-created_at')[:10]
        #messages = render_and_merge(flowgrams, comments)
        #cache.set(cache_key, messages, EXPIRATION)
    #else:
        #log.cache_hit(cache_key)
    #return messages