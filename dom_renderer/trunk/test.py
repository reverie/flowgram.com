#!/usr/bin/python

import os
from settings import WEB_HOST, DB_HOST, DB_NAME, DB_USER, DB_PASS, DISPLAY, TMP_DIR

if DISPLAY is not None:
    os.environ['DISPLAY'] = DISPLAY

print "Connecting to", os.environ['DISPLAY']

import gtk, webkit, gobject, Queue, mutex, MySQLdb, datetime, Image, sys, itertools

from time import sleep

class WebBrowser(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self._browser= webkit.WebView()
        self._browser.fg_window = self

        # Original version
        #self._scrolled_window = gtk.ScrolledWindow()
        #self._scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        #self._scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        #self._scrolled_window.add(self._browser)
        #self._scrolled_window.show_all()
        #vbox = gtk.VBox(spacing=4)
        #vbox.pack_start(self._scrolled_window)
        #self.add(vbox)


        # My version:
        self.add(self._browser)

        self.set_decorated(False)
        self.connect('destroy', gtk.main_quit)
        #self.set_default_size(SIZE_X, SIZE_Y)
        self.show_all()

        #print self.frame, type(self.frame)
        #print self.window, type(self.window)

# Place windows

window = WebBrowser()
webview = window._browser

desktop_x, desktop_y = window.get_root_window().get_size()
win_x, win_y = desktop_x/2, desktop_y/2
window.resize(win_x - 10, win_y - 50)
window.move(0, 0)

def make_screenshot(view, frame):
    browser = view.fg_window
    gdk_win = browser.window
    filename = "test_output.jpg"
    width, height = gdk_win.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
    pb.get_from_drawable(gdk_win, gdk_win.get_colormap(), 0, 0, 0, 0, width, height)
    pb = pb.scale_simple(400, 300, gtk.gdk.INTERP_BILINEAR)
    pb.save(filename, 'jpeg', {'quality' : '50'})
    print "Done writing to", filename
    sys.exit()

def load_finished(view, frame):
    print "Start processing page at", datetime.datetime.now()
    print "Frame uri is", frame.get_uri()
    browser = view.fg_window
    browser.present()
    #sleep(.1)
    make_screenshot(view, frame)
    view.fg_posted = True
    view.execute_script("var fg_host='%s';" % WEB_HOST)
    view.execute_script(bookmarklet)
    print "Bookmarklet inserted on %s" % frame.get_uri()

def do_load_finished(view, frame):
    gobject.timeout_add(100, load_finished, view, frame)


webview.connect('load-finished', do_load_finished)

v = webview
url = 'http://www.google.com/'
v.fg_posted = False
v.fg_orig_url = url
v.fg_owner = 0
v.fg_starttime = datetime.datetime.now()
v.open(url)

gtk.main()
