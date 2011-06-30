import webkit, gtk, gobject, Queue, mutex, MySQLdb, datetime
from time import sleep

bookmarklet = """var s= document.createElement('script');
s.type = "text/javascript";
s.src = "http://dev.flowgram.com/bj/AddURL.js";
document.getElementsByTagName('body')[0].appendChild(s);
"""

class Enum(object): pass
StatusCode = Enum()
StatusCode.UNPROCESSED = 0
StatusCode.PROCESSING = 1
StatusCode.DONE = 2
StatusCode.ERROR = 100

MAX_WORKERS = 10
JOBS_PER = 2
MAIN_DELAY = 1000
CHILD_DELAY = 1000*MAX_WORKERS
MAX_JOBS = MAX_WORKERS*JOBS_PER # There can be up to 2x this in the Queue
MAX_ATTEMPTS = 3
TIMEOUT = datetime.timedelta(seconds=60)

conn = MySQLdb.connect(host="69.20.78.32", db="fg_dev", user="andrew", passwd="34tl3ss")
main_cursor = conn.cursor()
child_cursors = [conn.cursor() for i in range(MAX_WORKERS)]
webviews = [webkit.WebView() for i in range(MAX_WORKERS)]
main_lock = mutex.mutex()
child_locks = [mutex.mutex() for i in range(MAX_WORKERS)]
q = Queue.Queue(0)


c = main_cursor.execute("UPDATE core_addpagerequest SET status_code=100 WHERE status_code=1 AND attempts>=%d" % MAX_ATTEMPTS)
if c:
    print "Set", c, "rows to error state"
c = main_cursor.execute("UPDATE core_addpagerequest SET status_code=%d WHERE status_code=%d" % (StatusCode.UNPROCESSED, StatusCode.PROCESSING))
if c:
    print "Changed", c, "rows from processing to unprocessed"

def load_finished(view, frame):
    if view.fg_posted:
        child_locks[view.fg_owner].unlock()
        print "APR done on %s (%s)" % (frame.get_uri(), view.fg_orig_url)
        return
    view.execute_script("var fg_host='dev.flowgram.com';")
    view.execute_script("var fg_aprid='%s';" % view.fg_apr_id)
    view.fg_posted = True
    view.execute_script(bookmarklet)
    print "Bookmarklet inserted on %s" % frame.get_uri()

for i in range(MAX_WORKERS):
    webviews[i].connect('load-finished', load_finished)

def start_worker(index):
    print "Worker started"
    if not child_locks[index].testandset():
        print "Worker %d could not acquire lock" % index
        v = webviews[index]
        if v.fg_starttime <= datetime.datetime.now() - TIMEOUT:
            print "Worker %d has timed out - canceling %s" % (index, v.fg_orig_url)
            v.stop_loading()
            main_cursor.execute("UPDATE core_addpagerequest SET status_code=100 WHERE id='%s' AND attempts>=%d" % (v.fg_apr_id, MAX_ATTEMPTS))
            child_locks[index].unlock()
        return True
    try:
        apr_id, url = q.get(False)
    except Queue.Empty:
        print "Worker %d had nothing to do" % index
        child_locks[index].unlock()
        return True
    print "Worker %d got (%s, %s)" % (index, apr_id, url)
    child_cursors[index].execute("UPDATE core_addpagerequest SET attempts=attempts+1 WHERE id='%s'" % apr_id)
    # TODO: set started at
    v = webviews[index]
    v.fg_posted = False
    v.fg_orig_url = url
    v.fg_owner = index
    v.fg_apr_id = apr_id
    v.fg_starttime = datetime.datetime.now()
    v.open(url)
    return True

def main_loop():
    print "Main loop called"
    if q.qsize() > MAX_JOBS:
        return True
    if not main_lock.testandset():
        print "Main loop could not acquire lock"
        return True
    main_cursor.execute("SELECT id, url FROM core_addpagerequest WHERE status_code=0 AND attempts<%d LIMIT %d" % (MAX_ATTEMPTS, MAX_JOBS))
    for job in main_cursor.fetchall():
        main_cursor.execute("UPDATE core_addpagerequest SET status_code=1 WHERE id='%s'" % job[0])
        q.put(job)
    main_lock.unlock()
    return True

gobject.timeout_add(MAIN_DELAY, main_loop)
for i in range(MAX_WORKERS):
    gobject.timeout_add(CHILD_DELAY, start_worker, i)
    sleep(MAIN_DELAY/1000)
gtk.main()
