import random, itertools, re, datetime

from django.conf import settings
from django.core.cache import cache

from flowgram.core import log
from flowgram.core.models import Flowgram, Featured
from django.contrib.auth.models import User
from flowgram.core.models import UserProfile, WhatsNew, Tip, Community_Content, Tag, Flowgram, FlowgramRelated
from flowgram.core.search import searcher
from flowgram.localsettings import FEATURE
from django.shortcuts import get_object_or_404
from string import punctuation

from django.http import HttpResponseRedirect, HttpResponse, Http404

MAX_RESULTS = 180
EXPIRATION = 30
CACHE_PREFIX = settings.CACHE_MIDDLEWARE_KEY_PREFIX
MAX_FEATURED = 100
RELATED_FLOWGRAM_EXPIRATION_DELTA = datetime.timedelta(days=1)

def set_from_cache(cache_key, queryset, limit=True):
    cache_key = CACHE_PREFIX + ':' + cache_key
    fgs = cache.get(cache_key)
    if fgs is None:
        if limit:
            queryset = queryset[:MAX_RESULTS]
        fgs = list(queryset)
        cache.set(cache_key, fgs, EXPIRATION)
    #    log.cache_hit(cache_key)
    #else:
    #    log.cache_miss(cache_key)
    return fgs 
    
def most_viewed():
    cache_key = "cached_sets:mostviewed"
    queryset = Flowgram.from_published.filter(public=True).order_by('-views')
    return set_from_cache(cache_key, queryset)
    
def most_discussed():
    cache_key = "cached_sets:mostdicussed"
    queryset = Flowgram.from_published.filter(public=True).order_by('-num_comments')
    return set_from_cache(cache_key, queryset)

def newest():
    cache_key = "cached_sets:newest"
    queryset = Flowgram.from_published.filter(public=True,display_in_newest=True).order_by('-modified_at')
    return set_from_cache(cache_key, queryset)
    
def admin_newest():
    cache_key = "cached_sets:admin_newest"
    queryset = Flowgram.from_published.filter(public=True).order_by('-modified_at')
    return set_from_cache(cache_key, queryset)

def top_rated():
    cache_key = "cached_sets:toprated"
    queryset = Flowgram.from_published.filter(public=True).order_by('-avg_rating')
    return set_from_cache(cache_key, queryset)
    
def get_a_whats_new():
    queryset = WhatsNew.objects.all();
    if queryset.count() == 0:
        return None

    counter = 0
    contentList = []
    for query in queryset:
        tempArray = range(query.weight)
        for i in tempArray:
            contentList.append(query)
            counter += 1
            
    random_number = random.randrange(0, counter)
    return contentList[random_number]
    
#    random_number = random.randrange(0, queryset.count())
#    query = queryset[random_number]
#    return query

def get_community_content():
    queryset = Community_Content.objects.all();
    if queryset.count() == 0:
        return None
    
    counter = 0
    contentList = []
    for query in queryset:
        tempArray = range(query.weight)
        for i in tempArray:
            contentList.append(query)
            counter += 1
            
    random_number = random.randrange(0, counter)
    return contentList[random_number]
#    random_number = random.randrange(0, queryset.count())
#    query = queryset[random_number]
#    return query


def get_a_tip():
    queryset = Tip.objects.all();
    if queryset.count() == 0:
        return None

    counter = 0
    contentList = []
    for query in queryset:
        tempArray = range(query.weight)
        for i in tempArray:
            contentList.append(query)
            counter += 1
            
    random_number = random.randrange(0, counter)
    return contentList[random_number]
#    random_number = random.randrange(0, queryset.count())
#    query = queryset[random_number]
#    return query

non_search_words = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                    'an','as' ,'at','by','he','his','me','or','us','who','and','for','her','him','if','it','its','nor','of',
                    'our','she','the','to','via','we','you','all','any','but','few','in','off','on','own','so','up','yet','them','they']


def get_related_fg_changed(flowgram, request):
    if FEATURE['use_HEsearch']:
        non_alpha_charaters = re.compile(r'[a-zA-Z]+')
        tags = Tag.objects.filter(flowgram=flowgram)
        searchphrase_list = [tag.name for tag in tags] + non_alpha_charaters.findall(flowgram.title)
        searchphrase_list = [word for word in searchphrase_list if word not in non_search_words and word not in punctuation]
        
        searchphrase = ' OR '.join(searchphrase_list)
        
        related_flowgrams = []
        log.debug('use hyperestraier, the searchphrase is: ' + searchphrase)
        he_documents = searcher.search(str(searchphrase))
        for he_doc in he_documents:
            if searcher.get_attr(he_doc, '@flowgram_type') == 'flowgram':
                fg_id = searcher.get_attr(he_doc, '@flowgram_id')
                one_flowgram = get_object_or_404(Flowgram, pk=fg_id)
                if one_flowgram.public or \
                        request.user.is_authenticated() and request.user == one_flowgram.owner:
                    if one_flowgram != flowgram:
                        related_flowgrams.append(one_flowgram)

        related_flowgrams = related_flowgrams[:10]
        related_flowgrams_string = ";".join([fg.id for fg in related_flowgrams])

        # flowgram changed, update the related flowgrams in db
        flowgram_need_update = FlowgramRelated.objects.filter(flowgram=flowgram)
        flowgram_need_update = flowgram_need_update[0] if len(flowgram_need_update) else None
        if flowgram_need_update:
            flowgram_need_update.related = related_flowgrams_string
            flowgram_need_update.timestamp = datetime.datetime.now()
            flowgram_need_update.save()
        else:
            FlowgramRelated.objects.create(flowgram=flowgram, related=related_flowgrams_string)
            
        return related_flowgrams
    else:
        return get_featured(feat.FEATURED_PAGE)
    

def get_related(flowgram, request):
    if FEATURE['use_HEsearch']:
        expiration_time = datetime.datetime.now() - RELATED_FLOWGRAM_EXPIRATION_DELTA
        flowgram_related_record = FlowgramRelated.objects.filter(flowgram=flowgram, timestamp__gte=expiration_time)
        flowgram_related_record = flowgram_related_record[0] if len(flowgram_related_record) else None
        if not flowgram_related_record:
            log.debug("need to re-calculate the related flowgrams record of %s" % flowgram.id)
            return get_related_fg_changed(flowgram, request)
        
        related_ids = flowgram_related_record.related
        related_flowgrams = []
        if related_ids:
            for fg_id in related_ids.split(';'):
                one_flowgram = get_object_or_404(Flowgram, pk=fg_id)
                related_flowgrams.append(one_flowgram)
        return related_flowgrams
    else:
        return get_featured(feat.FEATURED_PAGE)
        

def user_most_viewed(username):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    cache_key = "cached_sets:usermostviewed"
    queryset = Flowgram.from_published.filter(owner=u,public=True).order_by('-views')
    return set_from_cache(cache_key, queryset)

def user_most_discussed(username):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    cache_key = "cached_sets:usermostdicussed"
    queryset = Flowgram.from_published.filter(owner=u,public=True).order_by('-num_comments')
    return set_from_cache(cache_key, queryset)

def user_newest(username):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    cache_key = "cached_sets:usernewest"
    queryset = Flowgram.from_published.filter(owner=u,public=True).order_by('-modified_at')
    return set_from_cache(cache_key, queryset)

def user_top_rated(username):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    cache_key = "cached_sets:usertoprated"
    queryset = Flowgram.from_published.filter(owner=u,public=True).order_by('-avg_rating')
    return set_from_cache(cache_key, queryset)
    
def user_title(username):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    cache_key = "cached_sets:usertitle"
    queryset = Flowgram.from_published.filter(owner=u,public=True).order_by('title')
    return set_from_cache(cache_key, queryset)


def get_hero(area=0):
    cache_key = CACHE_PREFIX+":cached_sets:get_hero:"+str(area)
    hero = cache.get(cache_key)
    if hero is None:
        log.cache_miss(cache_key)
        try:
            hero = Featured.objects.filter(area=area)[0].flowgram
        except IndexError:
            hero = None
        cache.add(cache_key, hero, EXPIRATION)
    else:
        log.cache_hit(cache_key)
    return hero

def get_featured(area):
    cache_key = CACHE_PREFIX+":cached_sets:get_featured:" + str(area)
    flowgrams = cache.get(cache_key)
    if flowgrams is None:
        log.cache_miss(cache_key)
        featured = Featured.objects.filter(area=area)[1:100]
        flowgrams = []
        for rank, features in itertools.groupby(featured, lambda x: x.rank):
            l = [feat.flowgram for feat in features]
            random.shuffle(l)
            flowgrams.extend(l)
        cache.set(cache_key, flowgrams, EXPIRATION)
    else:
        log.cache_hit(cache_key)
    return flowgrams

