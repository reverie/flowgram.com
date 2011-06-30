from flowgram.core import controller, log, models
from flowgram.core.decorators import internal
from flowgram.core.require import require
from flowgram.core.response import data_response, error_response


@internal
@require('POST', ['flowgram_id', 'ppt_req_id', 'title', 'url', 'html'])
def add_ppt_slide(request, flowgram, ppt_req_id, title, url, html):
    page = models.Page.objects.create(title=title,
                                      source_url=url,
                                      creation_source="ppt:" + ppt_req_id)
    page = controller.create_page_to_flowgram(flowgram, page, html)


@require('POST', ['enc=json', 'ppt_import_request_id'])
def check(request, enc, ppt_import_request_id):
    ppt_import_request = models.PptImportRequest.objects.get(id=ppt_import_request_id)
    
    if ppt_import_request.status_code == models.StatusCode.DONE:
        return data_response.create(enc, 'ok', {"status_code": "1"})
    elif ppt_import_request.status_code == models.StatusCode.ERROR:
        return data_response.create(enc, 'ok', {"status_code": "-1"})
    else:
        return data_response.create(enc, 'ok', {"status_code": "0"})


# What needs to be done:
#     1. Add to Queue
#     2. Send to S3
#     3. Update queue (with link from S3)
@require('POST', ['enc=json'])
def upload(request, enc):
    if request.FILES.has_key('file'):
        # do later in queue once per slide
        # adds a page to the fg
        # html will be like before but embed a swf that is centered
        # page = Page.objects.create(title=request.FILES['file']['filename'], position=255)
        # page = controller.create_page_to_flowgram(fg, page, html)

        (fg, new) = controller.get_working_flowgram(request.user)
        if new:
            log.debug("Action log: new working flowgram %s created during add_page" % fg.id)

        # create queue item
        ppt_import_request = models.PptImportRequest.objects.create(flowgram=fg)

        #     2. Send to S3
        ppt_import_request.save_ppt_to_s3(request.FILES['file']['content'])
        
        return data_response.create(enc, 'ok', ppt_import_request.id)
    else:
        return error_response.create(enc, 'No file was uploaded.')
