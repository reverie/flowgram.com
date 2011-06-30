#!/usr/bin/python

import math, os, random, sys, Queue, mutex, MySQLdb, Image, itertools, urllib, urllib2, threading, traceback
from datetime import datetime
from settings import WEB_HOST, DB_HOST, DB_NAME, DB_USER, DB_PASS, TMP_DIR, NUM_PROCS
from time import sleep

from flowgram.core import controller
from flowgram.core.models import AddPageRequest, Enum, StatusCode, ThumbQueue, TQ_TYPES
from flowgram.queueprocessors import get_tasks_to_process

THUMB_QUEUE_TYPES = {'webpage': 0,
                     'image': 1}

THUMB_WIDTH = 800
THUMB_HEIGHT = 600

MAX_ATTEMPTS = 5

WORKER_DELAY = 4000
INSERT_BOOKMARKLET_DELAY = 2500
RENDER_DELAY = 5000
TIMEOUT_SECS = 180
DB_TIMEOUT_SECS = 140

SLEEP_SECONDS = 10

NUM_WORKERS = 4

ADD_URL_JS_URL = urllib2.urlopen("http://%s/bj/AddURL.js" % WEB_HOST).read()
Q_ADD_PAGE_PROCESSED_LINK_URL = "http://%s/api/q-addpageprocessed/" % WEB_HOST;


def excepthook(exctype, value, trace):
    """Make sure that the program quits completely once a single gtk thread dies. This
    way daemontools can restart it."""
    
    print "Exception -- quitting:", exctype, value, trace
    traceback.print_exc(file=sys.stdout)
    
    gtk.main_quit()


def insert_bookmarklet(view, frame):
    view.fg_inserted_bookmarklet = True
    
    print "%d inserting bookmarklet for %s id=%s" % (view.fg_owner, view.fg_type, view.fg_id)
    
    view.execute_script("var fg_apr_id='%s'; document.title = '';" % view.fg_id)
    view.execute_script(ADD_URL_JS_URL)
    
    # see http://code.google.com/p/pywebkitgtk/issues/detail?id=12 -----------------------------
    # upgrade webkit and patch to get real dom access.
    view.execute_script("SetTitleToTitle();")
    title = frame.get_title()
    #doc = context.get_by_name('document')
    #title = doc.title
    
    title = title or controller.DEFAULT_FG_TITLE
    
    view.execute_script("SetURLToTitle();")
    url = frame.get_title()
    view.execute_script("SetAPRIDToTitle();")
    addpagerequest_id = frame.get_title()
    view.execute_script("SetHTMLToTitle();")
    html = frame.get_title()
    # ------------------------------------------------------------------------------------------
    
    data = urllib.urlencode({'title': title,
                             'url': url,
                             'addpagerequest_id': addpagerequest_id,
                             'html': html})

    try:
        urllib2.urlopen(Q_ADD_PAGE_PROCESSED_LINK_URL, data)

        view.fg_task.status_code = StatusCode.DONE
        view.fg_task.save()
    except:
        traceback.print_exc(file=sys.stdout)
    
    view.fg_posted_done = True
    
    print "%d done posting for %s id=%s" % (view.fg_owner, view.fg_type, view.fg_id)

    if view.fg_sshot_done:
        stop_and_clear(view)

    return False


def is_image_all_one_color(pixel_buffer):
    pixel_rows = pixel_buffer.get_pixels_array().tolist()
    
    first_pixel_color = pixel_rows[0][0]
    
    # Checking to see if the image is all white.
    for row in pixel_rows:
        for p in row:
            if p != first_pixel_color:
                return False

    print "all_one_color"
    return True


def load_finished(view, frame):
    if frame != view.get_main_frame():
        print "%d load_finished for %s id=%s NOT main_frame" % \
                  (view.fg_owner, view.fg_type, view.fg_id)
        return
    else:
        print "%d load_finished at %s for %s id=%s" % \
                  (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
        
    # about:blank is loaded before the worker is allowed to work on another item.  When it finishes
    # loading the worker is released.
    if view.fg_loading_blank:
        print "%d unlocking at %s for %s id=%s" % \
                  (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
        worker_locks[view.fg_owner].unlock()
        return
    
    if not view.fg_scheduled_sshot:
        schedule_sshot(view, frame)
    
    if view.fg_is_apr and not view.fg_inserted_bookmarklet:
        gobject.timeout_add(INSERT_BOOKMARKLET_DELAY, insert_bookmarklet, view, frame)


def make_screenshot(view, frame):
    print "%d starting screenshot at %s for %s id=%s" % \
              (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
    
    try:
        gdk_win = view.fg_browser.window
        
        (width, height) = gdk_win.get_size()
        pixel_buffer = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
        pixel_buffer.get_from_drawable(gdk_win, gdk_win.get_colormap(), 0, 0, 0, 0, width, height)
        
        if is_image_all_one_color(pixel_buffer):
            return False
        
        filepath = "%s/%s.jpg" % (TMP_DIR, view.fg_id)

        pixel_buffer.save(filepath, 'jpeg', {'quality': '95'})
        
        print "%d starting save to s3 id=%s (%s)" % (view.fg_owner, view.fg_id, filepath)
        
        page_id = view.fg_task.page.id
        controller.save_thumb_to_s3(view.fg_task.page, filepath)
        if view.fg_is_webpage:
            view.fg_task.delete()
        
        print "%d done saving to s3 id=%s page_id=%s" % (view.fg_owner, view.fg_id, page_id)
        
        os.remove(filepath);

        print "%d finishing screenshot at %s for %s id=%s" % (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
    except:
        traceback.print_exc(file=sys.stdout)
        return False
        
    return True
    

def mark_task(task):
    result = True

    task.status_code = StatusCode.PROCESSING
    task.started_at = datetime.now()
    task.attempts += 1
    if task.attempts > MAX_ATTEMPTS:
        task.status_code = StatusCode.ERROR
        result = False
    task.save()

    return result


def page_id_url(pid):
    return "http://%s/api/getpage/%s/" % (WEB_HOST, pid)


def reserve_apr_task():
    try:
        tasks = get_tasks_to_process(AddPageRequest, DB_TIMEOUT_SECS)[:1]    
        if not len(tasks):
            return None

        task = tasks[0]
        if not mark_task(task):
            return reserve_apr_task()
        return task
    except:
        return None


def reserve_tq_task():
    try:
        tasks = get_tasks_to_process(ThumbQueue, DB_TIMEOUT_SECS)[:1]    
        if not len(tasks):
            transition.commit()
            return None

        task = tasks[0]
        if not mark_task(task):
            return reserve_tq_task()
        return task
    except:
        return None


def make_thumbs_for_image(task):
    url_io = urllib2.urlopen(task.page.source_url)
    content_type = url_io.headers.get('content-type')

    # Downloading the image from the source URL and saving it to a temporary file.
    temp_filepath = "%s/%s_orig.image" % (TMP_DIR, task.id)
    f = open(temp_filepath, 'wb')
    f.write(url_io.read())
    f.close()

    controller.save_thumb_to_s3(task.page, temp_filepath)

    os.remove(temp_filepath)
    
    print "done saving to s3 id=%s page_id=%s" % (task.id, task.page.id)


def schedule_sshot(view, frame):
    # Adding a thumb queue entry in case the screen shotter fails, since the APR might be done.
    if view.fg_is_apr and not ThumbQueue.objects.filter(page=view.fg_task.page).count():
        # Adding with timestamp and status in order to delay the initial processing of this
        # entry, to give the direct screenshotting (from the APR) a chance.
        fg_backup_thumbqueue = ThumbQueue.objects.create(
            page=view.fg_task.page,
            path=view.fg_task.page.source_url,
            type=0,
            status_code=StatusCode.PROCESSING,
            started_at=datetime.now())
        view.fg_backup_thumbqueue_id = fg_backup_thumbqueue.id

    print "%d scheduling sshot at %s for %s id=%s" % \
              (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
    gobject.timeout_add(RENDER_DELAY, take_sshot, view, frame)
    view.fg_scheduled_sshot = True


def start_worker(index):
    print "starting worker %d" % index
    view = webviews[index]
    
    # If the worker is busy, check to see if it has timed out.
    if not worker_locks[index].testandset():
        print "%d could not acquire lock" % index
        
        if (datetime.now() - view.fg_starttime).seconds > TIMEOUT_SECS:
            print "%d has timed out - canceling %s id=%s url=%s" % \
                      (index, view.fg_type, view.fg_id, view.fg_url)
            stop_and_clear(view)
            
        return True
    
    try:
        first_try_apr = int(random.random() * 2)
        if first_try_apr:
            task = reserve_apr_task() or reserve_tq_task()
        else:
            task = reserve_tq_task() or reserve_apr_task()

        if not task:
            worker_locks[index].unlock()
            return True
        
        view.fg_task = task
        view.fg_is_apr = isinstance(task, AddPageRequest)
        view.fg_is_webpage = not view.fg_is_apr and task.type == THUMB_QUEUE_TYPES['webpage']
        view.fg_is_image = not view.fg_is_apr and task.type == THUMB_QUEUE_TYPES['image']
        # fg_type is used for debugging only.
        view.fg_type = 'apr' if view.fg_is_apr else 'webpage' if view.fg_is_webpage else 'image'
        
        url = task.url if view.fg_is_apr else task.page.source_url
        
        print "%d at %s got %s id=%s url=%s" % (index, datetime.now(), view.fg_type, task.id, url)
        
        if view.fg_is_apr or view.fg_is_webpage:
            view.fg_owner = index
            view.fg_id = task.id
            view.fg_starttime = datetime.now()
            view.fg_url = url
            
            view.fg_backup_thumbqueue_id = None
            view.fg_inserted_bookmarklet = False
            view.fg_scheduled_sshot = False
            view.fg_posted_done = False
            view.fg_sshot_done = False
            view.fg_loading_blank = False
            
            view.open(url)
        else: # if view.fg_is_image:
            make_thumbs_for_image(task)
            worker_locks[index].unlock()
    except:
        traceback.print_exc(file=sys.stdout)
        stop_and_clear(view)

    return True


def stop_and_clear(view):
    print "%d stopping load and going to about:blank at %s for %s id=%s" % (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
    view.stop_loading()
    
    view.fg_loading_blank = True
    view.fg_id = None
    
    view.open("about:blank")


def take_sshot(view, frame):
    print "%d take_sshot at %s for %s id=%s" % (view.fg_owner, datetime.now(), view.fg_type, view.fg_id)
    if not make_screenshot(view, frame):
        gobject.timeout_add(RENDER_DELAY, take_sshot, view, frame)
        return
    
    # Removing the backup thumbqueue entry if the screenshot is successfully rendered.
    if view.fg_backup_thumbqueue_id:
        print "setting status of backup thumbqueue entry to done"
        task = ThumbQueue.objects.get(id=view.fg_backup_thumbqueue_id)
        task.status_code = StatusCode.DONE
        task.save()
    
    view.fg_sshot_done = True

    if view.fg_posted_done:
        stop_and_clear(view)


display_number = int(sys.argv[sys.argv.index('-display') + 1])
os.environ['DISPLAY'] = 'localhost:%d.0' % display_number
# These imports must be down here because the display has to be set up beforehand
print "Connecting to", os.environ['DISPLAY']

# Subtracting 1 from the worker number (which is 1-based on the command-line) to make it 0-based
# for performing mod operations.
# TODO(westphal): proc_number is now unused, see if this works out well.
# proc_number = int(sys.argv[sys.argv.index('-worker') + 1]) - 1

if '-nosleep' not in sys.argv:
    print "Sleeping..."
    sleep(SLEEP_SECONDS)
else:
    print "Not sleeping"


# NOTE: This definition and import have to come after the sleep.
import gtk, webkit, gobject
class WebBrowser(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        self._webview = webkit.WebView()
        self._webview.fg_browser = self
        
        self.add(self._webview)
        
        self.set_decorated(False)
        self.connect('destroy', gtk.main_quit)
        self.show_all()
        

sys.excepthook = excepthook

main_lock = mutex.mutex()
worker_locks = [mutex.mutex() for i in range(NUM_WORKERS)]

windows = [WebBrowser() for i in range(NUM_WORKERS)]
webviews = [win._webview for win in windows]

(desktop_width, desktop_height) = windows[0].get_root_window().get_size()

num_windows_per_row_or_column = int(math.ceil(math.sqrt(NUM_WORKERS)))
win_width = desktop_width / num_windows_per_row_or_column
win_height = desktop_height / num_windows_per_row_or_column
    
print "desktop_width = %d desktop_height = %s win_width = %d win_height = %d" % \
          (desktop_width, desktop_height, win_width, win_height)

for position in range(NUM_WORKERS):
    window = windows[position]
    window.resize(win_width, win_height)
    row_num = position / num_windows_per_row_or_column
    col_num = position % num_windows_per_row_or_column
    window.move(col_num * win_width, row_num * win_height)

    webview = webviews[position]
    webview.fg_lock = threading.Lock()
    webview.connect('load-finished', load_finished)

    gobject.timeout_add(WORKER_DELAY, start_worker, position)

gtk.main()
