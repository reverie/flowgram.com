import os, sys, Queue, mutex, MySQLdb, datetime, Image, itertools, urllib2, threading
from time import sleep

display_name = 'localhost:%d.0' % 11
os.environ['DISPLAY'] = display_name

WEB_HOST = "beta.flowgram.com"

bookmarklet = """var s= document.createElement('script');
s.type = "text/javascript";
s.src = "http://%s/bj/AddURL.js";
document.documentElement.appendChild(s);
""" % WEB_HOST

g_AddURLLink = "http://%s/bj/AddURL.js" % WEB_HOST;
g_AddURLJS = urllib2.urlopen(g_AddURLLink).read()
g_QAddPageProcessedLink = "http://%s/api/q-addpageprocessed/" % WEB_HOST;

print "Connecting to", os.environ['DISPLAY']
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

window = WebBrowser()
view = window._webview

window.resize(640, 480)
window.move(0, 0)

def load_finished(view, frame):
    print("load_finished")
    
    print("A")
    view.execute_script("var fg_apr_id='%s';" % "t883wkidkz3w3t")
    print("C")
    
    view.execute_script(g_AddURLJS)
    view.execute_script("SetPostDataToTitle();")
    
    data = frame.get_title()
    
    urllib2.urlopen(g_QAddPageProcessedLink, data)
    
    gobject.timeout_add(1000, main)

view.connect('load-finished', load_finished)

urls = ["http://google.com", "http://yahoo.com"]
num = {}
num["n"] = -1

def main():
    print num
    num["n"] += 1
    num["n"] %= len(urls)
    u = urls[num["n"]]
    
    print(u)
    view.open(u)
    
    return False

gobject.timeout_add(1000, main)

gtk.main()
