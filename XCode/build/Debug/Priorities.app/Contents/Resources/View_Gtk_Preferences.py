import gtk

import preferences


class Preferences:
	def __init__(self, controller):
		self.__controller = controller

		self.preferences = preferences.Load()

		# [To-Do] Check diferences between stored and loaded preferences

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("Preferences")
		self.window.connect('response',self.__on_Preferences_response)

		chkDefaultDB = builder.get_object("chkDefaultDB")
		chkDefaultDB.connect('toggled', self.__on_chkDefaultDB_toggled)
		chkDefaultDB.set_active(self.preferences['useDefaultDB'])

		self.fcDefaultDB = builder.get_object("fcDefaultDB")
		self.fcDefaultDB.set_filename(self.preferences['database'])

		chkDefaultDB.toggled()

		cbInabordable = builder.get_object("cbInabordable")
		cbInabordable.connect('color-set', self.__on_colorbutton_colorset)
		cbInabordable.set_color(gtk.gdk.color_parse(self.preferences['color_unabordable']))
		cbInabordable.set_title('color_unabordable')

		cbInProcess = builder.get_object("cbInProcess")
		cbInProcess.connect('color-set', self.__on_colorbutton_colorset)
		cbInProcess.set_color(gtk.gdk.color_parse(self.preferences['color_inprocess']))
		cbInProcess.set_title('color_inprocess')

		cbAvailable = builder.get_object("cbAvailable")
		cbAvailable.connect('color-set', self.__on_colorbutton_colorset)
		cbAvailable.set_color(gtk.gdk.color_parse(self.preferences['color_available']))
		cbAvailable.set_title('color_available')

		cbSatisfacted = builder.get_object("cbSatisfacted")
		cbSatisfacted.connect('color-set', self.__on_colorbutton_colorset)
		cbSatisfacted.set_color(gtk.gdk.color_parse(self.preferences['color_satisfacted']))
		cbSatisfacted.set_title('color_satisfacted')


	def __on_chkDefaultDB_toggled(self, widget):
		print "__on_chkDefaultDB_toggled"
		self.fcDefaultDB.set_sensitive(widget.get_active)


	def __on_colorbutton_colorset(self, widget):
		self.preferences[widget.get_title()] = widget.get_color()


	def __on_Preferences_response(self, widget, response):
		if response == 1:
			preferences.Store(self.preferences)
