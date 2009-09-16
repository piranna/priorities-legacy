#!/usr/bin/env python

# example scrolledwin.py

import pygtk
pygtk.require('2.0')
import gtk
import random

class ScrolledWindowExample:
    def destroy(self, widget):
        gtk.main_quit()

    def ButtonClicked(self, button):
        # move the button
        self.layout.move(button, random.randint(0,500),
                         random.randint(0,500))

    def __init__(self):
        # Create a new dialog window for the scrolled window to be
        # packed into. 
        window = gtk.Dialog()
        window.connect("destroy", self.destroy)
        window.set_title("ScrolledWindow example")
        window.set_border_width(0)
        window.set_size_request(300, 300)

        # create a new scrolled window.
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)

        # the policy is one of POLICY AUTOMATIC, or POLICY_ALWAYS.
        # POLICY_AUTOMATIC will automatically decide whether you need
        # scrollbars, whereas POLICY_ALWAYS will always leave the scrollbars
        # there. The first one is the horizontal scrollbar, the second, the
        # vertical.
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        # The dialog window is created with a vbox packed into it.
        window.vbox.pack_start(scrolled_window, gtk.TRUE, gtk.TRUE, 0)
        scrolled_window.show()
    
         # create the layout widget and pack into the table
        self.layout = gtk.Layout(None, None)
        self.layout.set_size(600, 600)

        # pack the table into the scrolled window
        scrolled_window.add_with_viewport(self.layout)
        self.layout.show()

        # create 3 buttons and put them into the layout widget
        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 0, 0)
        button.show()

        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 100, 0)
        button.show()

        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 200, 0)
        button.show()

        # Add a "close" button to the bottom of the dialog
        button = gtk.Button("close")
        button.connect_object("clicked", self.destroy, window)

        # this makes it so the button is the default.
        button.set_flags(gtk.CAN_DEFAULT)
        window.action_area.pack_start( button, gtk.TRUE, gtk.TRUE, 0)

        # This grabs this button to be the default button. Simply hitting
        # the "Enter" key will cause this button to activate.
        button.grab_default()

        # show all the widgets
        button.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    ScrolledWindowExample()
    main()
