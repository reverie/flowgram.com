import re

from django.shortcuts import get_object_or_404

from flowgram import localsettings
from flowgram.core import helpers, models
from flowgram.core.exporters.video import uploadtoyoutube
from flowgram.core.require import require


WHITE_SPACE_OR_COMMAS_REGEX = re.compile(r'[,\s]+')


@require('GET', ['enc=html', 'export_to_video_request_id'])
def export_to_video_check(request, enc, export_to_video_request_id):
    export_to_video_request = models.ExportToVideoRequest.objects.get(id=export_to_video_request_id)

    if export_to_video_request.status_code == models.StatusCode.ERROR:
        return helpers.req_render_to_response(
            request,
            'flowgram/export_to_video_error.html',
            {'title': export_to_video_request.flowgram.title})
    if export_to_video_request.status_code == models.StatusCode.DONE:
        return helpers.req_render_to_response(
            request,
            'flowgram/export_to_video_done.html',
            {'title': export_to_video_request.flowgram.title})

    unfinished_status_codes = [models.StatusCode.UNPROCESSED, models.StatusCode.PROCESSING]

    num_prior_unprocessed_tasks = 0
    if export_to_video_request.status_code != models.StatusCode.PROCESSING:
        unfinished_tasks = models.ExportToVideoRequest.objects.filter(
            status_code__in=unfinished_status_codes)

        similar_tasks = unfinished_tasks.filter(
            flowgram=export_to_video_request.flowgram,
            use_highlight_popups=export_to_video_request.use_highlight_popups).order_by('timestamp')
        if similar_tasks.count():
            num_prior_unprocessed_tasks = unfinished_tasks.filter(
                timestamp__lt=similar_tasks[0].timestamp).count()        

    return helpers.req_render_to_response(
        request,
        'flowgram/export_to_video_check.html',
        {'title': export_to_video_request.flowgram.title,
         'status': 'currently processing' \
             if export_to_video_request.status_code == models.StatusCode.PROCESSING \
             else 'in our queue, waiting to be processed',
         'approx_wait': 10 \
             if export_to_video_request.status_code == models.StatusCode.PROCESSING \
             else num_prior_unprocessed_tasks * 3 + 10})


@require('GET', ['enc=html', 'export_to_video_request_id'])
def export_youtube_step1(request, enc, export_to_video_request_id):
    export_to_video_request = get_object_or_404(models.ExportToVideoRequest,
                                                id=export_to_video_request_id)
    return helpers.req_render_to_response(
        request,
        'flowgram/export_youtube_step1.html',
        {
            'flowgram': export_to_video_request.flowgram,
            'auth_sub_url': uploadtoyoutube.get_auth_sub_url(export_to_video_request_id),
            'preview_url': 'http://%s/%s.wmv' % \
                (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_UPLOAD],
                 export_to_video_request_id)
        })


@require('GET', ['enc=html', 'export_to_video_request_id', 'token'])
def export_youtube_step2(request, enc, export_to_video_request_id, token):
    export_to_video_request = get_object_or_404(models.ExportToVideoRequest,
                                                id=export_to_video_request_id)
    flowgram = export_to_video_request.flowgram

    tags = models.Tag.objects.filter(flowgram=flowgram)
    keywords = ', '.join([tag.name for tag in tags])

    return helpers.req_render_to_response(
        request,
        'flowgram/export_youtube_step2.html',
        {
            'export_to_video_request_id': export_to_video_request_id,
            'flowgram_id': flowgram.id,
            'title': flowgram.title,
            'description': '%s\n\nClick here to view and interact with this Flowgram:\n%s' % \
                (flowgram.description, flowgram.flex_url()),
            'keywords': keywords,
            'token': token,
        })


@require('POST',
         ['enc=html', 'export_to_video_request_id', 'token', 'title', 'description', 'category', \
              'private:boolean=false'])
def export_youtube_step3(request, enc, export_to_video_request_id, token, title, description, \
                             category, private):
    export_to_video_request = get_object_or_404(models.ExportToVideoRequest,
                                                id=export_to_video_request_id)
    flowgram = export_to_video_request.flowgram

    keywords = WHITE_SPACE_OR_COMMAS_REGEX.sub(', ', request.POST.get('keywords'))

    models.UploadToYouTubeRequest.objects.create(
        token=token,
        request_user=request.user if request.user.is_authenticated() else None,
        export_to_video_request=export_to_video_request,
        flowgram=flowgram,
        title=title,
        description=description,
        keywords=keywords,
        category=category,
        private=private)

    return helpers.req_render_to_response(request, 'flowgram/export_youtube_step3.html', {})
