import os
from datetime import datetime

from flowgram import localsettings
from flowgram.core import helpers, log, models, s3
from flowgram.core.require import require
from flowgram.core.response import data_response, error_response


@require('POST', ['page_id', 'time:int', 'duration:int'], ['edit_page'])
def add_audio_fms(request, page, time, duration):
    file_path = '%s/%s/%s/%d.flv' % (localsettings.FMS_STREAM_DIR, page.flowgram.id, page.id, time)
    
    if os.path.isfile(file_path):
        audio = models.Audio.objects.create(page=page, time=time, duration=duration)
        audio.path = file_path
        
        helpers.set_modified(page.flowgram)
        
        s3.save_filename_to_bucket(localsettings.S3_BUCKET_AUDIO, '%s.flv' % audio.id, file_path)
        
        return data_response.create(request.POST.get('enc', 'json'), 'ok', audio.id)
    else:
        log.debug('add_audio_fms called with page.id=%s, time=%d, and duration=%d but file_path=%s DNE' % \
                      (page.id, time, duration, file_path))
        
        return error_response.create(request.POST.get('enc', 'json'), 'flv does not exist.')


@require('POST', ['page_id'], ['edit_page'])
def clear_audio(request, page):
    models.Audio.objects.filter(page=page).delete()
    log.debug('Action log: clear_audio on page %s for %s' % (page.id, request.user.username))


@require('POST', ['page_id', 'audio_id'], ['edit_page'])
def delete_audio(request, page, audio):
    audio.delete()


@require('POST', ['flowgram_id'])
def remove_background_audio(request, flowgram):
    flowgram.background_audio = None
    flowgram.save()


@require('POST', ['page_id', 'audio_id', 'time:int', 'duration:int'], ['edit_page'])
def update_audio(request, page, audio, time, duration):
    audio.time = time
    audio.duration = duration
    audio.save()
