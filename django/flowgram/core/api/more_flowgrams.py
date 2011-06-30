from django.shortcuts import get_object_or_404

# TODO(westphal): Move relevant controller code to controllers submodule.
from flowgram.core import cached_sets, controller, encode, log, models
from flowgram.core.require import require
from flowgram.core.response import data_response


@require('GET', ['page_size:int', 'page_number:int'], ['login'])
def get_favorite_fgs_paginated(request, page_size, page_number):
    favorites_dict = controller.get_favorite_fgs_paginated(request.user, page_size, page_number)
    favorites_dict['flowgrams'] = [encode.flowgram_encoder.to_dict(flowgram, False, request.user) \
                                       for flowgram in favorites_dict['flowgrams']]
    return data_response.create(request.GET.get('enc', 'json'), 'ok', favorites_dict)


@require('GET', ['page_size:int', 'page_number:int'], ['login'])
def get_fgs_paginated(request, page_size, page_number):
    flowgrams = models.Flowgram.objects.filter(owner=request.user)
    num_flowgrams = flowgrams.count()
    
    flowgrams = flowgrams.order_by('-created_at')
    flowgrams = flowgrams[(page_number - 1) * page_size:page_number * page_size]
    flowgrams = [encode.flowgram_encoder.to_dict(flowgram, False, request.user) \
                     for flowgram in flowgrams]
    return data_response.create(request.GET.get('enc', 'json'),
                                'ok',
                                {'num_flowgrams': num_flowgrams,
                                 'flowgrams': flowgrams})


@require('GET', ['page_size:int', 'page_number:int', 'type'])
def get_more_fgs_paginated(request, page_size, page_number, type):
    if type == 'related':
        flowgram_id = request.GET.get('flowgram_id')
        flowgram = models.Flowgram.objects.get(id=flowgram_id)
        flowgrams = get_related_flowgrams(flowgram, request)
    elif type == 'featured':
        flowgrams = get_featured_flowgrams()
    elif type == 'mostpopular':
        flowgrams = get_most_popular_flowgrams()
    elif type == 'mostdiscussed':
        flowgrams = get_most_discussed_flowgrams()
    elif type == 'toprated':
        flowgrams = get_top_rated_flowgrams()
    else:
        raise Http404

    num_flowgrams = len(flowgrams)
    flowgrams = flowgrams[(page_number - 1) * page_size:page_number * page_size]
    flowgrams = [encode.flowgram_encoder.to_dict(flowgram, False, request.user) \
                     for flowgram in flowgrams]
    return data_response.create(request.GET.get('enc', 'json'),
                                'ok',
                                {'num_flowgrams': num_flowgrams,
                                 'flowgrams': flowgrams})


# HELPERS-------------------------------------------------------------------------------------------


def get_featured_flowgrams():
    return cached_sets.get_featured(models.feat.FEATURED_PAGE)


def get_related_flowgrams(flowgram, request):
    return cached_sets.get_related(flowgram, request)


def get_most_popular_flowgrams():
    return cached_sets.most_viewed()


def get_most_discussed_flowgrams():
    return cached_sets.most_discussed()


def get_top_rated_flowgrams():
    return cached_sets.top_rated()
