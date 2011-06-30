import datetime, re, urllib2, socket, time

from flowgram import localsettings
from flowgram.core import s3, helpers
from flowgram.core.models import GetCssRequest, StatusCode
from flowgram.queueprocessors.queueprocessor import QueueProcessor

DEFAULT_UA = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'
FILE_ENCODING = 'utf-8'
MAX_ATTEMPTS = 2
RETRY_TIME = datetime.timedelta(seconds=60)

TIME_TO_SLEEP = 3

IMPORT_FORM_1 = re.compile(r'@import[ \t]+("[^"\r\n]+"|\'[^\'\r\n]+\')[ \t]*;', re.I)
IMPORT_FORM_2 = re.compile(r'(@import)?([ \t]*)url\([ \t]*("[^"\r\n]+"|\'[^\'\r\n]+\'|[^\)\'"\r\n]+)[ \t]*\)(([^;\r\n]*);)?', re.I)
EXPRESSION = re.compile(r'(behavior)?\s*:\s*expression\s*\([^;]*?;|(behavior)?\s*:\s*url\s*\([^\)]*?\);?', re.I)

class DownloadException(Exception): 
    pass

# TODO(westphal): Have this use helpers.download_url

# TODO(westphal): Handle circular references.
class GetCssRequestProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return
            
        tasksUnprocessed = GetCssRequest.objects.filter(status_code=StatusCode.UNPROCESSED)
        tasksProcessing = GetCssRequest.objects.filter(status_code=StatusCode.PROCESSING)

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
            file = download_css_file(task.url)

            file = process_css_file(task.page, file, task.url)
            path = save_css_file_to_s3(task, file)

            task.status_code = StatusCode.DONE
            task.path = path
            task.save()

            success = True
        except DownloadException:
            pass
        except Exception, e:
            print e
            print("Failed attempt to load CSS file for caching: %s" % task.url)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:
                    task.status_code = StatusCode.ERROR
                    task.save()

def download_css_file(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', DEFAULT_UA)]
    
    urlReader = None
    try:
        try:
            urlReader = opener.open(url)
        except (ValueError, urllib2.URLError):
            print("Failed attempt to cache CSS file: %s" % url)
            raise DownloadException
        
        # Handles redirects
        url = urlReader.geturl()
        
        # Checking the MIME type
        contentType = urlReader.info()['content-type']
        if not contentType.startswith('text'):
            print("Unsupported MIME type for CSS file: %s" % url)
            raise DownloadException
        
        return urlReader.read()
    finally:
        if urlReader:
            urlReader.close()
        opener.close()

def get_absolute_import_url(import_url, doc_url):
    if import_url.startswith('"') or import_url.startswith("'"):
        import_url = import_url[1:len(import_url) - 1]
    
    # URL should always be absolute by the time it gets to this point (i.e. by the time it is
    # entered as a GetCssRequest)
    url_domain = doc_url[0:doc_url.index("/", doc_url.startswith("http://") and 7 or 8)]
    url_dir = doc_url[0:doc_url.rindex("/") + 1]
    
    # Calculating the absolute URL of the CSS file.
    if not import_url.startswith("http://") and not import_url.startswith("https://"):
        if import_url.startswith("/"):
            if import_url.startswith("//"):
                import_url = "http:%s" % import_url
            else:
                import_url = url_domain + import_url
        else:
            import_url = url_dir + import_url
    
    return import_url

def process_css_file(page, file, url):
    file = process_css_file_form_1_imports(page, file, url)
    file = process_css_file_form_2_imports(page, file, url)
    file = process_expression(page, file, url)
    
    return file

def process_css_file_form_1_imports(page, file, url):
    output = []
    
    offset = 0
    
    match_iter = IMPORT_FORM_1.finditer(file)
    for match in match_iter:
        # Calculating the absolute URL of the CSS file.
        import_url = str(helpers.unescape_html(get_absolute_import_url(match.group(1), url)))
        
        # Creating a request to fetch the linked CSS file.
        request = GetCssRequest.objects.create(url=import_url, page=page)
        
        # Replacing the original import statement with a new one, that points to our servers.
        output.append(file[offset:match.start()])
        output.append("@import url('%s');" % request.calculate_local_url())
        
        offset = match.end()
    
    output.append(file[offset:len(file)])
    
    return "".join(output)

def process_css_file_form_2_imports(page, file, url):
    output = []
    
    offset = 0
    
    match_iter = IMPORT_FORM_2.finditer(file)
    for match in match_iter:
        if match.group(1) == '@import':
            # If another css url.
            
            # Calculating the absolute URL of the CSS file.
            import_url = str(helpers.unescape_html(get_absolute_import_url(match.group(3), url)))
            
            # Checking the media type for the import, we're only caching screen CSS.
            media_ok = True
            media = match.group(5)

            if len(media.strip()):
                try:
                    media.index("screen")
                except:
                    media_ok = False
            
            if media_ok:
                # Creating a request to fetch the linked CSS file.
                request = GetCssRequest.objects.create(url=import_url, page=page)
                
                # Replacing the original import statement with a new one, that points to our servers.
                output.append(file[offset:match.start()])
                output.append("@import url('%s');" % request.calculate_local_url())
            else:
                # Treating as if it were a regular file.
                output.append(file[offset:match.start()])
                output.append("%surl('%s')%s" % (match.group(2), import_url, match.group(4) or ''))
            
            offset = match.end()                
        else:
            # If a non-css url.
            
            # Calculating the absolute URL of the file.
            import_url = str(helpers.unescape_html(get_absolute_import_url(match.group(3), url)))
            output.append(file[offset:match.start()])
            output.append("%surl('%s')%s" % (match.group(2), import_url, match.group(4) or ''))
            offset = match.end()
    
    output.append(file[offset:len(file)])
    
    return "".join(output)

def process_expression(page, file, url):
    output = []
    
    offset = 0
    
    match_iter = EXPRESSION.finditer(file)
    for match in match_iter:
        output.append(file[offset:match.start()])
        
        offset = match.end()
    
    output.append(file[offset:len(file)])
    
    return "".join(output)

def save_css_file_to_s3(task, file):
    s3.save_string_to_bucket(localsettings.S3_BUCKET_CSS, task.id + ".css", file, "public-read", "text/css")
    
    return "S3"
