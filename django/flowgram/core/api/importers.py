import Image, os, tempfile

from django.shortcuts import get_object_or_404

from flowgram import localsettings, settings
from flowgram.core import controller, encode, log, models, permissions
from flowgram.core.importers import rss
from flowgram.core.require import require
from flowgram.core.response import data_response, error_response


DOC_TYPE_EXTENSIONS = ['ppt', 'pptx', 'pps', 'xls', 'xlsx', 'xlc', 'doc', 'docx', 'rtf', 'txt', 
                           'wri', 'log', 'pdf']

EXTENSION_TO_CONTENT_TYPE = {'aif': 'audio/x-aiff',
                             'aiff': 'audio/x-aiff',
                             'mp3': 'audio/mpeg',
                             'wav': 'audio/x-wav',
                             'wma': 'audio/x-ms-wma'}

IMAGE_FORMAT_TO_MIME_AND_EXTENSION = {'GIF': ['image/gif', '.gif'],
                                      'JPEG': ['image/jpeg', '.jpg'],
                                      'PNG': ['image/png', '.png']}


@require('POST', [], ['login'])
def file_upload(request):
    # Uses GET parameters instead of POST for passing data, handled by Flex.
    file = request.FILES['file']
    content = file['content']
    content_type = file['content-type']
    filename = file['filename']
    filetype = request.GET.get('filetype', '')
    enc = request.GET.get('enc', 'json')
    
    flowgram_id = request.GET.get('flowgram_id')
    flowgram = get_object_or_404(models.Flowgram, id=flowgram_id) \
                   if flowgram_id \
                   else controller.get_working_flowgram(request.user)
    if not permissions.can_edit(request.user, flowgram):
        return error_response.create(enc, 'Does not have edit_flowgram permission.' \
                                              if localsettings.DEBUG \
                                              else 'Permission violation')

    if filetype == 'image' or content_type.startswith('image'):
        return handle_file_upload_image(enc, content, content_type, filetype, filename, flowgram)
    elif filetype in DOC_TYPE_EXTENSIONS:
        return handle_file_upload_doc(enc, content, content_type, filetype, filename, flowgram)
    elif filetype == 'media':
        page = None
        try:
            page_id = request.GET.get('page_id')
            page = models.Page.objects.get(id=page_id)
        except:
            pass

        if page and not permissions.can_edit(request.user, page):
            return error_response.create(enc, 'Does not have edit_page permission.' \
                                                  if localsettings.DEBUG \
                                                  else 'Permission violation')

        return handle_file_upload_media(enc, content, content_type, filetype, filename, \
                                            page or flowgram)
    else:
        return error_response.create(enc, 'Unsupported file type')


@require('POST', ['enc=json', 'flowgram_id', 'url', 'type', 'maxresults:int=0'], ['edit_flowgram'])
def import_rss(request, enc, flowgram, url, type, max_results):
    return rss.import_rss(flowgram, url, type, {'enc': enc,
                                                'max_results': max_results})


# Helpers-------------------------------------------------------------------------------------------


def handle_file_upload_doc(enc, content, content_type, filetype, filename, flowgram):
    ppt_import_request = models.PptImportRequest.objects.create(flowgram=flowgram, filetype=filetype)
    ppt_import_request.save_ppt_to_s3(content)
    
    return data_response.create(enc, 'ok', ppt_import_request.id)


def handle_file_upload_image(enc, content, content_type, filetype, filename, flowgram):
    temp_image = tempfile.mkstemp(".image")
    os.close(temp_image[0])
    temp_image_path = temp_image[1]

    try:
        file = open(temp_image_path, "wb")
        file.write(content)
        file.close()
        
        try:
            # Opens the file to make sure it works as an image.
            image = Image.open(temp_image_path)
            image.load()
        except:
            return error_response.create(
                enc,
                'Invalid image: Currently supported image types include: JPEG, PNG, and GIF')

        (mime, extension) = IMAGE_FORMAT_TO_MIME_AND_EXTENSION[image.format]

        # Resizing the image if too large.
        if image.size[0] > settings.DEFAULT_PHOTO_WIDTH or \
               image.size[1] > settings.DEFAULT_PHOTO_HEIGHT:
            image.thumbnail((settings.DEFAULT_PHOTO_WIDTH, settings.DEFAULT_PHOTO_HEIGHT),
                            Image.BICUBIC)

        page = models.Page.objects.create(title=filename)

        uploaded_file = models.UploadedFile.objects.create(page=page, mimetype=mime, media_type=0)
        page.source_url = uploaded_file.get_absolute_url()

        html = ''.join(['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html><head><title></title>',
                        '<link rel="stylesheet" type="text/css" href="',
                        localsettings.MEDIA_URL,
                        'css/photo_importers.css">',
                        '<link rel="stylesheet" type="text/css" href="',
                        localsettings.MEDIA_URL,
                        'css/page.css"></head><body><div><img src="',
                        uploaded_file.get_absolute_url(),
                        '" /></div></body></html>'])

        # Saving the thumbnailed image and reading the data.
        try:
            temp_image_final = tempfile.mkstemp(extension)
            os.close(temp_image_final[0])
            temp_image_final_path = temp_image_final[1]
            image.save(temp_image_final_path)

            file = open(temp_image_final_path, "rb")
            data = file.read()
            file.close()
        finally:
            os.remove(temp_image_final_path)
        
        uploaded_file.set_file(data)

        page = controller.create_page_to_flowgram(flowgram, page, html)
        return data_response.create(enc, 'ok', encode.page.to_dict(page))
    finally:
        os.remove(temp_image_path)


def handle_file_upload_media(enc, content, content_type, filetype, filename, flowgram_or_page):
    temp_media_path = tempfile.mkstemp('.media')
    os.close(temp_media_path[0])
    file = open(temp_media_path[1], "wb")
    file.write(content)
    file.close()
    os.chmod(temp_media_path[1], 0640)
    
    extension = filename[filename.rfind('.') + 1:].lower()
    content_type = EXTENSION_TO_CONTENT_TYPE[extension]
    
    kwargs = {'path': temp_media_path[1],
              'content_type': content_type}
    kwargs['page' if isinstance(flowgram_or_page, models.Page) else 'flowgram'] = flowgram_or_page

    import_media_request = models.ImportMediaRequest.objects.create(**kwargs)

    return data_response.create(enc, 'ok', import_media_request.id)
