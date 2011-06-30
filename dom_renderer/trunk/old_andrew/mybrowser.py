#!/usr/bin/env python

import time, gtk, webkit, gobject
from gettext import gettext as _

def f(*args, **kwargs):
    pass


class WebBrowser(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self._loading = False
        self._browser= webkit.WebView()
        self._browser.connect('load-finished', f)
        #self._browser.connect('load-started', f)
        #self._browser.connect("populate-popup", self._populate_popup)

        #self._browser.connect("console-message", f)
        #self._browser.connect("script-alert",
        #                      self._javascript_script_alert_cb)
        #self._browser.connect("script-confirm",
        #                      self._javascript_script_confirm_cb)
        #self._browser.connect("script-prompt",
        #                      self._javascript_script_prompt_cb)

        self._scrolled_window = gtk.ScrolledWindow()
        self._scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self._scrolled_window.add(self._browser)
        self._scrolled_window.show_all()

        #self._toolbar = WebToolbar(self._browser)


        vbox = gtk.VBox(spacing=4)
        vbox.pack_start(self._scrolled_window)

        self.add(vbox)
        self.set_default_size(600, 480)

        self.connect('destroy', gtk.main_quit)

        about = """
<html><head><title>About</title></head><body>
<h1>Welcome to <code>webbrowser.py</code></h1>
<p><a href="http://live.gnome.org/PyWebKitGtk">Homepage</a></p>
</body></html>
"""
        self._browser.load_string(about, "text/html", "iso-8859-15", "about:")

        self.show_all()



webbrowser = WebBrowser()
gtk.main()

#def _set_scroll_adjustments_cb(self, page, hadjustment, vadjustment):
#    self._scrolled_window.props.hadjustment = hadjustment
#    self._scrolled_window.props.vadjustment = vadjustment

#def _populate_popup(self, view, menu):
#    iampywebkitgtk = gtk.MenuItem(label="PyWebKitGtk!")
#    menu.append(iampywebkitgtk)
#    menu.show_all()

#def _javascript_console_message_cb(self, page, message, line, sourceid):
#    return

#def _javascript_script_alert_cb(self, page, frame, message):
#    pass

#def _javascript_script_confirm_cb(self, page, frame, message, isConfirmed):
#    pass

#def _javascript_script_prompt_cb(self, page, frame, message, default, text):
#    pass


#self._entry.connect('activate', self._entry_activate_cb)
#self._browser.stop_loading()
#self._browser.reload()
#self._browser.connect("title-changed", f)
#self._entry.grab_focus()
