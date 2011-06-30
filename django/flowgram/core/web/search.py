from django.contrib.auth import models as auth_models
from django.http import HttpResponse

from flowgram import localsettings, settings
from flowgram.core import cached_sets, controller, models, webhelpers
from flowgram.core.require import require
from flowgram.core.search import searcher


@require('GET')
def feed_google(request):
    if request.META.get("HTTP_USER_AGENT", "").lower().find(settings.GOOGLEBOT_UA) >= 0:
        host_fg = localsettings.my_URL_BASE + "p/"
        
        xml = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">']
        
        for fg in models.Flowgram.objects.filter(public=True):
            xml.extend(["<url>",
                        "<loc>%s%s/</loc>" % (host_fg, fg.id),
                        "<lastmod>%s</lastmod>" % str(fg.modified_at).split(" ")[0],
                        "<changefreq>weekly</changefreq>",
                        "<priority>0.5</priority>",
                        "</url>"])
                
        xml.append("</urlset>")
        return HttpResponse("".join(xml), mimetype="text/xml")
    else:
        return HttpResponse("Your Action is not Allowed!")


@require('GET', ['enc=html', 'q='], ['authorized'])
def search(request, enc, q):
    controller.record_stat(request, 'view_search_website', '0', '')
    
    if localsettings.FEATURE['use_HEsearch']:
        return hyperestraier_search(request, enc, q)
    
    fgs = models.Flowgram.objects.filter(public=True)
    if request.user.is_authenticated():
        fgs |= models.Flowgram.objects.filter(owner=request.user)
    
    # Using filter with a non-sense id because .none returns an EmptyQueueSet, which causes |= to
    # fail with "TypeError: Cannot merge querysets of different types 'EmptyQuerySet' and
    # 'QuerySet'.".
    by_title = by_tag = by_page_url = by_description = fgs.filter(id='NONSENSE_ID')
    
    extra_context = {'mostviewed': cached_sets.most_viewed()[:6],
                     'q': q,
                     'get_args': "q=%s" % q,
                     'send_to_details': localsettings.FEATURE['send_to_details']}
    
    terms = q.split()
    query_terms = "%%%s%%" % "%".join(terms)
    
    by_title_description = fgs.extra(where=['(title LIKE %s OR description LIKE %s)'],
                                     params=[query_terms, query_terms])
    
    if not len(by_title_description):
        # By title:
        for term in terms:
            by_this_title = fgs.filter(title__icontains=term)
            by_title |= by_this_title
        
        # By description:
        for term in terms:
            by_this_description = fgs.filter(description__icontains=term)
            by_description |= by_this_description
            
        by_title_description = by_title | by_description
    
        # By tag:
        for term in terms:
            tags = models.Tag.objects.filter(name=term)
            by_this_tag = fgs.filter(id__in=[tag.flowgram.id for tag in tags])
            by_tag |= by_this_tag
        
    search_results = (by_tag | by_page_url | by_title_description).order_by('-created_at')

    # Check if author exists
    if len(terms) == 1:
        try:
            auth_models.User.objects.get(username=terms[0])
            by_username = True
        except auth_models.User.DoesNotExist:
            by_username = False
        extra_context['by_username'] = by_username

    return webhelpers.flowgram_lister(request,
                                      enc='html',
                                      queryset=search_results,
                                      template_name='search/search_results.html',
                                      extra_context=extra_context,
                                      display_mode='list')


# HELPERS-------------------------------------------------------------------------------------------


def hyperestraier_search(request, enc, q):
    searchphrase = ' AND '.join(q.split())
            
    queryset = []
    extra_context = {'mostviewed': cached_sets.most_viewed()[:6],
                     'q': q,
                     'get_args': "q=%s" % q,
                      'send_to_details': localsettings.FEATURE['send_to_details']}
    he_documents = searcher.search(str(searchphrase))
        
    for he_doc in he_documents:
        if searcher.get_attr(he_doc, '@flowgram_type') == 'flowgram':
            flowgram_id = searcher.get_attr(he_doc, '@flowgram_id')
            matching_flowgram = models.Flowgram.objects.filter(id=flowgram_id)
            matching_flowgram = matching_flowgram.filter(public=True) | \
                                matching_flowgram.filter(owner=request.user)
            if len(matching_flowgram):
                queryset.append(matching_flowgram[0])

    return webhelpers.flowgram_lister(request,
                                      enc='html',
                                      queryset=queryset,
                                      template_name='search/search_results.html',
                                      extra_context=extra_context,
                                      display_mode='list')
