# NOTE WHEN SETTING UP A NEW PPT SERVER:
# source: http://forums.sun.com/thread.jspa?threadID=532305
# You can disable the popup error message by setting the value of HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Windows\ErrorMode: 0x00000002 (2)

# ErrMode takes one of the following DWORD(hex) values:
# 0 All errors appear in popups (Default)
# 1 System errors disabled, application errors still using popups
# 2 Neither system or application errors use popups


import codecs, datetime, Image, re, urllib, urllib2, socket, os, tempfile, time, sys, shutil

from flowgram import localsettings
from flowgram.core import s3, controller, helpers
from flowgram.core.models import StatusCode, PptImportRequest, Page
from flowgram.queueprocessors.queueprocessor import QueueProcessor

NUM_WORKERS = int(sys.argv[sys.argv.index('-num_workers') + 1])

# Subtracting 1 from the worker number (which is 1-based on the command-line) to make it 0-based
# for performing mod operations.
WORKER_NUMBER = int(sys.argv[sys.argv.index('-worker') + 1]) - 1

print("NUM_WORKERS = %s WORKER_NUMBER = %s" % (NUM_WORKERS, WORKER_NUMBER))

if WORKER_NUMBER > NUM_WORKERS:
    print("error WORKER_NUMBER > NUM_WORKERS")
    exit(-1)

# To Do:
# 1. Fetch a job from the queue
# 2. Extract the ppt file
# 3. Send the ppt file to the C# program
# 4. Read .info file from C# 
# 5. Retrieve .svg slides
# 6. Place slides on s3
# ??? create new pages in fg?
# 7. Call back webserver to announce finished

FILE_ENCODING = 'utf-8'
MAX_ATTEMPTS = 2

OUTPUT_FORMAT_PNG = "png"
OUTPUT_FORMAT_SWF = "swf"

THUMB_WIDTH = 750
THUMB_HEIGHT = 563

TIME_TO_SLEEP = 5

RENDER_WIDTH = THUMB_WIDTH * 2
RENDER_HEIGHT = THUMB_HEIGHT * 2

RENDER_WIDTH_STR = str(RENDER_WIDTH)
RENDER_HEIGHT_STR = str(RENDER_HEIGHT)

RETRY_TIME = datetime.timedelta(seconds=900)
ADD_PPT_SLIDE_URL = "http://%s/powerpoint/add_ppt_slide/" % localsettings.MASTER_DOMAIN_NAME;

SWFOBJECT_URL = "http://%s/media/js/third_party/swfobject.js" % localsettings.MASTER_DOMAIN_NAME;

class PptProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    # 1. Fetch a job from the queue - done
    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return
    
        tasksUnprocessed = PptImportRequest.objects.filter(status_code=StatusCode.UNPROCESSED, uploaded_to_s3=True)
        tasksProcessing = PptImportRequest.objects.filter(status_code=StatusCode.PROCESSING, uploaded_to_s3=True)

        tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.datetime.now() - RETRY_TIME)
        
        tasks = tasksUnprocessed | tasksTimedOut
        tasks = tasks[:40]
        
        num_queued = 0

        for task in tasks:
            if ord(task.id[0]) % NUM_WORKERS != WORKER_NUMBER:
                print("skipping %s" % task.id)
                continue
            else:
                print("queuing %s" % task.id)

            task.status_code = StatusCode.PROCESSING
            task.started_at = datetime.datetime.now()
            task.save()
            
            self.queue.put(task)
            
            num_queued += 1
        
        if num_queued == 0:
            time.sleep(TIME_TO_SLEEP)
            
    def process(self, task):
        print("processing %s" % task.id)
        
        task.attempts += 1
        task.started_at = datetime.datetime.now()
        task.save()

        success = False
        try:
            # 2. Extract the ppt file
            temp_dir = tempfile.mkdtemp()
            temp_path = temp_dir + "\\" + task.id + "." + task.filetype
            print("temp_dir = %s" % temp_dir)
            print("temp_path = %s" % temp_path)
            
            download_file(task.get_s3_url(), temp_path)

            output_dir = localsettings.POWERPOINT_DIR + "/" + helpers.get_id_subdir_path(task.id) + "/" + task.id
            helpers._mkdir(output_dir + "/")

            # 3. Send the ppt file to the C# program
            slide_files = process_ppt_file(temp_path, output_dir)

            #s3_slide_urls = save_slides_to_s3(task, slide_files)
            slide_urls = get_slide_urls(task, slide_files)

            for url in slide_urls:
                extension = url[-3:]
                
                if extension.lower() == "swf":
                    html = '<html>' \
                                '<head>' \
                                    '<title>Slide</title>' \
                                    '<script src=\"%s\"></script>' \
                                '</head>' \
                                '<body>' \
                                    '<div id="swfwrapper">' \
                                        '<div id="swfholder">' \
                                            'You either have JavaScript turned off or an old version of Adobe\'s Flash Player.' \
                                            '<a href="http://www.macromedia.com/go/getflashplayer/">Click here to get the latest Flash player</a>.' \
                                        '</div>' \
                                    '</div>' \
                                    '<script>' \
                                        'swfobject.embedSWF("%s",' \
                                        '"swfholder",' \
                                        '"100%%",' \
                                        '"100%%",' \
                                        '"9.0.60",' \
                                        '"/media/swf/expressInstall.swf",' \
                                        '{},' \
                                        '{' \
                                            'wmode: \'opaque\',' \
                                            'bgcolor: \'#FFFFFF\',' \
                                            'allowScriptAccess: \'always\'' \
                                        '},' \
                                        '{' \
                                            'id: \'FlexClient2\'' \
                                        '});' \
                                    '</script>' \
                                '</body>' \
                            '</html>' % (SWFOBJECT_URL, url)
                else:
                    html = '<html>' \
                                '<head>' \
                                    '<title>Slide</title>' \
                                    '<style>@import url("/media/css/photo_importers.css");</style>' \
                                '</head>' \
                                '<body>' \
                                    '<center>' \
                                        '<img src="%s" />' \
                                    '</center>' \
                                '</body>' \
                            '</html>' % (url)
                    

                data = {
                        'flowgram_id': task.flowgram.id,
                        'ppt_req_id': task.id,
                        'title': "Slide",
                        'url': url,
                        'html': html
                }

                u = urllib2.urlopen(ADD_PPT_SLIDE_URL, urllib.urlencode(data))
                u.close()

            task.status_code = StatusCode.DONE
            task.save()
            
            print("task saved and status_code set to DONE")

            success = True
        except DownloadException:
            pass
        except Exception, e:
            print e 
            print("Failed attempt to process %s" % task.id)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:
                    task.status_code = StatusCode.ERROR
                    task.save()
                    
            shutil.rmtree(temp_dir)
            print("deleted %s" % temp_dir)

class DownloadException(Exception): 
    print ("Download Exception\n")
    pass

def download_file(url, path):
    try:
        print("downloading %s" % url)
        
        u = urllib2.urlopen(url)
        f = open(path, "wb")
        f.write(u.read())
        f.close()
        u.close()
    except Exception, e:
        print e
        print("download failed")
        raise DownloadException

def process_ppt_file(ppt_path, output_dir):
    #converter_command = "ispringsdk.exe make-slides " + os.getcwd() + "\\" + path + " " + path[0:-4]
    converter_command = "ppt_converter.exe %s %s %s %s %s" % (ppt_path, output_dir, OUTPUT_FORMAT_SWF, RENDER_WIDTH_STR, RENDER_HEIGHT_STR) 
    
    print("executing %s" % converter_command)
    ret = os.system(converter_command)
    
    resize_thumbs = False
    
    if str(ret) != "0":
        print("converting to SWF failed defaulting to PNG")
        converter_command = "ppt_converter.exe %s %s %s %s %s" % (ppt_path, output_dir, OUTPUT_FORMAT_PNG, RENDER_WIDTH_STR, RENDER_HEIGHT_STR)
        ret = os.system(converter_command)
        
        if str(ret) == "0":
            raise Exception("conversion failed")
        
        resize_thumbs = True
    
    info_path = output_dir + "\\info.txt"
    f = open(info_path, 'r')
    lines = f.readlines()
    f.close()
    
    slide_files = [line.rstrip() for line in lines]
    
    if resize_thumbs:
        for f in slide_files:
            print f
            img = Image.open(f)
            img.thumbnail((THUMB_WIDTH, THUMB_HEIGHT), Image.ANTIALIAS)
            img.save(f)

    return slide_files

def save_slides_to_s3(task, slide_files):
    counter = 1
    
    num_slides = str(len(slide_files))
    
    s3_slide_urls = []
    
    for slide_file in slide_files:
        try:
            key = task.id + "/" + str(counter) + "_" + num_slides + ".png"
            print("saving to s3 key=%s path=%s" % (key, slide_file))
            
            s3.save_filename_to_bucket(localsettings.S3_BUCKET_PPT, key, slide_file)
            
            s3_slide_urls.append(s3.get_url_from_bucket(localsettings.S3_BUCKET_PPT, key))
        except Exception, e:
            print e
            print("save to s3 failed")
            raise e

        counter = counter + 1
    
    return s3_slide_urls

def get_slide_urls(task, slide_files):
    subdir_path = helpers.get_id_subdir_path(task.id)
    
    return ["http://" + localsettings.POWERPOINT_SERVER + "/" + subdir_path + "/" + task.id + "/" + os.path.basename(file) for file in slide_files]
        
