from django.template import Context, loader
from django.http import Http404
from flowgram import settings
from flowgram.core import controller, encode, log
from flowgram.core.helpers import remove_script_tags
from flowgram.core.models import Page, AddPageRequest
from flowgram.core.response import data_response
from flowgram.lib import feedparser

def import_rss(flowgram, rss_url, type, options):
    if rss_url.startswith('feed://'):
        rss_url = 'http://' + rss_url[7:]

    parsed = feedparser.parse(rss_url)
    if not parsed.has_key('status'):
        raise Http404
    else:
        if parsed['status'] == '404':
            raise Http404
        
    is_atom = not not parsed['feed']

    if is_atom:
        # If ATOM
        channelTitle = parsed['feed'].get('title', '')
        channelDescription = ''
    else:
        # If RSS
        channelTitle = parsed.channel.title
        channelDescription = parsed.channel.description

    flowgram_changed = False
    if not flowgram.title or flowgram.title.lower() == 'untitled':
        flowgram.title = channelTitle
        flowgram_changed = True
    if not flowgram.description:
        flowgram.description = channelDescription
        flowgram_changed = True

    if flowgram_changed:
        flowgram.save()

    pages = []

    items = parsed['items']
    if options['max_results']:
        max_results = options['max_results']
        items = items[:max_results]

    if type == 'linkedarticles' or type == 'articlesummaries':
        required_keys = ['title', 'link', 'description']
        for item in items: 
            for rkey in required_keys:
                if not item.has_key('title'):
                    title = ''
                elif item.has_key('title'):
                    title = item.title 
                if not item.has_key('link'):
                    link = ''
                elif item.has_key('link'):
                    link = item.link
                if not item.has_key('description'):
                    description = ''
                elif item.has_key('description'):
                    description = item.description
            
            # need to check whether the 'title,link,description' attribute exists
          
            
            if type == 'linkedarticles':
                page = Page.objects.create(flowgram=flowgram,
                                           owner=flowgram.owner,
                                           title=title,
                                           source_url=link,
                                           position=controller.get_next_position(flowgram))
                
                controller.add_default_time(page)
                
                AddPageRequest.objects.create(flowgram=flowgram, url=link, page=page)

                pages.append(encode.page.to_dict(page))
            elif type == 'articlesummaries':
                # Create and save the page:
                page = Page.objects.create(title=title, source_url=link)
                page.save()

                context = Context({
                    'title': title,
                    'url': link,
                    'description': remove_script_tags(description)
                })
                template = loader.get_template('importers/rss.html')

                html = '%s' % template.render(context)
                page = controller.create_page_to_flowgram(flowgram, page, html)

                pages.append(encode.page.to_dict(page))
    elif type == 'singlesummarypage':
        # Create and save the page:
        page = Page.objects.create(title=channelTitle, source_url=rss_url)
        page.save()

        context = Context({
            'title': channelTitle,
            'items': items
        })
        template = loader.get_template('importers/rss_singlesummarypage.html')

        html = '%s' % template.render(context)
        page = controller.create_page_to_flowgram(flowgram, page, html)

        pages.append(encode.page.to_dict(page))
        
    if len(pages) == 0:
        raise Http404
    return data_response.create(options.get('enc', 'json'), 'ok', pages)
