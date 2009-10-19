# Copyright (C) 2009 Canonical
#
# Authors:
#  Michael Vogt
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gtk

class NavigationBar(gtk.HBox):
    """A navigation bar using button (like nautilus)"""

    def __init__(self, group=None):
        super(NavigationBar, self).__init__()
        self.id_to_widget = {}
        self.id_to_callback = {}
        if not group:
            self.group = gtk.RadioButton()
        else:
            self.group = group

    def add_with_id(self, label, callback, id):
        """
        Add a new button with the given label/callback

        If there is the same id already, replace the existing one
        with the new one
        """
        # check if we have the button of that id or need a new one
        if id in self.id_to_widget:
            button = self.id_to_widget[id]
            button.disconnect(self.id_to_callback[id])
        else:
            button = gtk.RadioButton(self.group)
            button.set_mode(False)
            self.pack_start(button, expand=False)
            self.id_to_widget[id] = button
            button.show()
        # common code
        handler_id = button.connect("clicked", callback)
        button.set_label(label)
        button.set_active(True)
        self.id_to_callback[id] = handler_id

    def remove_id(self, id):
        """
        Remove the navigation button with the given id
        """
        if not id in self.id_to_widget:
            return
        self.remove(self.id_to_widget[id])
        del self.id_to_widget[id]
        try:
            del self.id_to_callback[id]
        except KeyError:
            pass

    def remove_all(self):
        """remove all elements"""
        for w in self:
            self.remove(w)
        self.id_to_widget = {}
        self.id_to_callback = {}

    def get_button_from_id(self, id):
        """
        return the button for the given id (or None)
        """
        if not id in self.id_to_widget:
            return None
        return self.id_to_widget[id]

    def get_label(self, id):
        """
        Return the label of the navigation button with the given id
        """
        if not id in self.id_to_widget:
            return
        return self.id_to_widget[id].get_label()


    # Added by Piranna <piranna@gmail.com>
    def get_active_position(self):
        """
        Return the position of the active button
        """
        position = 0
        for children in self.get_children():
            if children.get_active():
                return position
            position += 1
        return None

    def remove_remanents(self):
        """
        Remove all the navigation buttons whose position
        is greater than the current active one.
        WARNING: if there are two or more IDs with the same children
        it will remove the last one
        """
        active_position = self.get_active_position()
        position = 0
        for children in self.get_children():
            if position > active_position:
                self.remove_id(dict([[v,k] for k,v in self.id_to_widget.items()])[children])
            position += 1

