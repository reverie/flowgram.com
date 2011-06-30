from flowgram.core import controller
from flowgram.core.require import require


@require('GET', ['type', 'num:int=0', 'string='])
def record_stat(request, type, num, string):
    controller.record_stat(request, type, num, string)


@require('POST')
def record_bulk_stats(request):
    for stat_index in range(5):
        type_key = 'type%s' % stat_index
        # Exiting when the first missing entry is encountered.
        if not type_key in request.POST:
            break
        
        type_value = request.POST.get(type_key, None)
        num_value = int(request.POST.get('num%s' % stat_index, 0))
        string_value = request.POST.get('string%s' % stat_index, '')

        controller.record_stat(request, type_value, num_value, string_value)
