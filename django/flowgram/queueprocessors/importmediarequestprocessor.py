import commands, datetime, os, re, urllib2, socket, time, sys, traceback, tempfile, shutil

from flowgram.core import s3, helpers
from flowgram.core.models import Audio, ImportMediaRequest, StatusCode
from flowgram.queueprocessors.queueprocessor import QueueProcessor
from flowgram import localsettings

AUDIO_SPS = 22050
MAX_ATTEMPTS = 2
RETRY_TIME = datetime.timedelta(seconds=300)

TIME_TO_SLEEP = 5

DURATION_REGEX = re.compile(r'Duration:\s*(\d+):(\d+):(\d+)\.(\d+)')

class ImportMediaRequestProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return
            
        tasksUnprocessed = ImportMediaRequest.objects.filter(status_code=StatusCode.UNPROCESSED)
        tasksProcessing = ImportMediaRequest.objects.filter(status_code=StatusCode.PROCESSING)

        tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.datetime.now() - RETRY_TIME)

        tasks = tasksUnprocessed | tasksTimedOut
        tasks = tasks[:10]
        
        for task in tasks:
            print("queuing %s" % task.id)
            task.status_code = StatusCode.PROCESSING
            task.started_at = datetime.datetime.now()
            task.save()
            
            self.queue.put(task)
        
        if len(tasks) == 0:
            time.sleep(TIME_TO_SLEEP)
            
    def process(self, task):
        print("processing %s" % task.id)
        
        task.attempts += 1
        task.started_at = datetime.datetime.now()
        task.save()

        success = False
        
        try:
            if task.content_type.startswith('audio/'):
                new_path = '%s.flv' % task.path
                print("task.path = %s new_path = %s" % (task.path, new_path))
                
                execute_command = '%s -i %s -ar %d -ac 1 -y %s' % \
                                      (localsettings.VIDEO['ffmpeg_path'],
                                       task.path,
                                       AUDIO_SPS,
                                       new_path)
                conversion_output = commands.getoutput(execute_command)

                # Using a regular expression to extract the duration of the input audio from ffmpeg.
                match = DURATION_REGEX.search(conversion_output)
                if match:
                    hours = int(match.groups()[0])
                    mins = int(match.groups()[1])
                    secs = int(match.groups()[2])
                    millis = match.groups()[3]

                    while len(millis) < 3:
                        millis += '0'
                    millis = int(millis)
                    duration = millis + secs * 1000 + mins * 60000 + hours * 3600000
                else:
                    raise Exception('Unable to determine audio duration.  Executed: %s\n%s' % \
                                        (execute_command, conversion_output))

                if task.page:
                    audio = Audio.objects.create(page=task.page, time=0, duration=duration, path='')
                    if task.page.duration < duration:
                        task.page.duration = duration
                        task.page.save()
                elif task.flowgram:
                    audio = Audio.objects.create(page=None, time=0, duration=duration, path='')
                    task.flowgram.background_audio = audio
                    task.flowgram.save()

                save_audio_file_to_s3(audio.id, new_path)

                os.remove(new_path)

                task.status_code = StatusCode.DONE
                task.media_type = 'audio'
                task.media_model_id = audio.id
                task.save()

                success = True
            else:
                raise Exception('Unsupported MIME type "%s"' % task.content_type)
        except Exception, e:
            print e
            traceback.print_exc(file=sys.stdout)
            print("Failed attempt to add media for page: %s" % task.page.id)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:

                    task.status_code = StatusCode.ERROR
                    task.save()

def save_audio_file_to_s3(audio_id, file):
    s3.save_file_to_bucket(localsettings.S3_BUCKET_AUDIO,
                           '%s.flv' % audio_id,
                           open(file),
                           'public-read',
                           'video/x-flv')
    return "S3"
