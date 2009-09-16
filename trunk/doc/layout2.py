#!/usr/bin/env python

# example layout.py

import gtk
import random

class LayoutExample:
    def WindowDeleteEvent(self, widget, event):
        # return false so that window will be destroyed
        return False

    def WindowDestroy(self, widget, *data):
        # exit main loop
        gtk.main_quit()

    def ButtonClicked(self, button):
        # move the button
        self.layout.move(button, random.randint(0,500),
                         random.randint(0,500))

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("layout2.glade")
        window = builder.get_object("window")
        self.layout = builder.get_object("layout")

        # create the top level window
#        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#        window.set_title("Layout Example")
#        window.set_default_size(300, 300)
        window.connect("delete-event", self.WindowDeleteEvent)
        window.connect("destroy", self.WindowDestroy)


        # create the layout widget and pack into the table
#        self.layout = gtk.Layout(None, None)
#        self.layout.set_size(600, 600)

#        window.add(self.layout)

        # create 3 buttons and put them into the layout widget
        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 0, 0)
        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 100, 0)
        button = gtk.Button("Press Me")
        button.connect("clicked", self.ButtonClicked)
        self.layout.put(button, 200, 0)

        # show all the widgets
        window.show_all()

def main():
    # enter the main loop
    gtk.main()
    return 0

if __name__ == "__main__":
    LayoutExample()
    main()
