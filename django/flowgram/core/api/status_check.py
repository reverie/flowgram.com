from flowgram.core import encode, models
from flowgram.core.require import require
from flowgram.core.response import data_response


@require('POST',
         [
             'apr_ids:csl=',
             'etvr_ids:csl=',
             'imr_ids:csl=',
             'page_ids:csl=',
             'ppt_ids:csl=',
             'thumb_page_ids:csl=',
         ])
def check_all(request, apr_ids, etvr_ids, imr_ids, page_ids, ppt_ids, thumb_page_ids):
    (aprs_done, aprs_failed) = check_add_page_requests(apr_ids)
    (etvrs_done, etvrs_failed) = check_export_to_video_requests(etvr_ids)
    (imrs_done, imrs_failed) = check_import_media_requests(imr_ids)
    (pages_done, pages_failed) = check_pages(page_ids)
    (ppts_done, ppts_failed) = check_ppt(ppt_ids, request.POST.get('flowgram_id', None))
    (thumbs_done, thumbs_failed) = check_thumbs(thumb_page_ids)

    return data_response.create(
        request.POST.get('enc', 'json'),
        'ok',
        {
            'aprs_done': aprs_done,
            'aprs_failed': aprs_failed,
            'etvrs_done': etvrs_done,
            'etvrs_failed': etvrs_failed,
            'imrs_done': imrs_done,
            'imrs_failed': imrs_failed,
            'pages_done': pages_done,
            'pages_failed': pages_failed,
            'ppts_done': ppts_done,
            'ppts_failed': ppts_failed,
            'thumbs_done' : thumbs_done,
            'thumbs_failed' : thumbs_failed,
        })


# Helpers-------------------------------------------------------------------------------------------


def check_add_page_requests(apr_ids):
    aprs = map(id_to_apr, apr_ids)
    aprs_done = dict((apr.id, encode.page.to_dict(apr.page)) \
                         for apr in aprs if apr.status_code == models.StatusCode.DONE)
    aprs_failed = [apr.id for apr in aprs if apr.status_code == models.StatusCode.ERROR]
    return (aprs_done, aprs_failed)


def check_export_to_video_requests(etvr_ids):
    etvrs = map(id_to_etvr, etvr_ids)
    etvrs_done = dict((etvr.id, encode.page.to_dict(etvr.page)) \
                          for etvr in etvrs if etvr.status_code == models.StatusCode.DONE)
    etvrs_failed = [etvr.id for etvr in etvrs if etvr.status_code == models.StatusCode.ERROR]
    return (etvrs_done, etvrs_failed)


def check_import_media_requests(imr_ids):
    imrs = map(id_to_imr, imr_ids)
    
    imrs_done = {}
    for imr in imrs:
        if imr.status_code == models.StatusCode.DONE:
            output = {'media_type': imr.media_type}
            if imr.media_type == 'audio':
                output['data'] = \
                    encode.audio.to_dict(models.Audio.objects.get(id=imr.media_model_id))
            imrs_done[imr.id] = output

    imrs_failed = [imr.id for imr in imrs if imr.status_code == models.StatusCode.ERROR]

    return (imrs_done, imrs_failed)


def check_pages(page_ids):
    try:
        pages = map(id_to_page_nocache, page_ids)
        pages_done = {}
        pages_failed = []
        for page in pages:
            status = page.get_loading_status()
            if status == models.StatusCode.DONE:
                pages_done[page.id] = page.id
            elif status == models.StatusCode.ERROR:
                pages_failed.append(page.id)
        return (pages_done, pages_failed)
    except models.Page.DoesNotExist:
        return ([], page_ids)


def check_ppt(ppt_ids, flowgram_id):
    try:
        flowgram = models.Flowgram.objects.get(id=flowgram_id) if flowgram_id else None

        ppts = map(id_to_ppt, ppt_ids)
        ppts_done = dict((ppt.id,
                          [encode.page.to_dict(page) for page \
                                   in flowgram.page_set.filter(creation_source='ppt:%s' % ppt.id)]) \
                               for ppt in ppts if ppt.status_code == models.StatusCode.DONE)
        ppts_failed = [ppt.id for ppt in ppts if ppt.status_code == models.StatusCode.ERROR]
        return (ppts_done, ppts_failed)
    except models.Flowgram.DoesNotExist:
        return ([], ppt_ids)


def check_thumbs(page_ids):
    try:
        pages = map(id_to_page_nocache, page_ids)
        thumbs_done = [page.id for page in pages if page.thumb_path]
        thumbs_failed = [page.id for page in pages \
                             if page.get_loading_status() == models.StatusCode.ERROR]
        return (thumbs_done, thumbs_failed)
    except models.Page.DoesNotExist:
        return ([], page_ids)


def id_to_apr(id): 
    return models.AddPageRequest.objects.get(id=id)

def id_to_etvr(id):
    return models.ExportToVideoRequest.objects.get(id=id)

def id_to_imr(id): 
    return models.ImportMediaRequest.objects.get(id=id)

def id_to_page_nocache(pid):
    return models.Page.bypass_cache.get(id=pid)

def id_to_ppt(id): 
    return models.PptImportRequest.objects.get(id=id)
