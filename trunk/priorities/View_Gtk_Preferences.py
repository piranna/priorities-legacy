import gtk

import preferences


class Preferences:
	def __init__(self, controller):
		self.__controller = controller

		self.preferences = preferences.Load()

		# [To-Do] Check diferences between stored and loaded preferences

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		# Preferences window
		self.window = builder.get_object("Preferences")
		self.window.connect('response',self.__on_Preferences_response)

		# DataBase
		chkDefaultDB = builder.get_object("chkDefaultDB")
		chkDefaultDB.connect('toggled', self.__on_chkDefaultDB_toggled)
		chkDefaultDB.set_active(self.preferences['useDefaultDB'])

		self.fcDefaultDB = builder.get_object("fcDefaultDB")
		self.fcDefaultDB.set_filename(self.preferences['database'])

		chkDefaultDB.toggled()

		# Show sharp
		chkShowSharp = builder.get_object("chkShowSharp")
		chkShowSharp.connect('toggled', self.__on_chkShowSharp_toggled)
		chkShowSharp.set_active(self.preferences['showSharp'])

		# Show satisfacted dependencies
		model_scrit = gtk.ListStore(str)
		model_scrit.append(("Nunca",))
		model_scrit.append(("Solo no expiradas",))
		model_scrit.append(("Siempre",))
		cell = gtk.CellRendererText()

		cbShowExceededDependencies = builder.get_object("cbShowExceededDependencies")
		cbShowExceededDependencies.set_model(model_scrit)
		cbShowExceededDependencies.pack_start(cell)
		cbShowExceededDependencies.add_attribute(cell,'text',0)
		cbShowExceededDependencies.connect('changed', self.__on_cbShowExceededDependencies_changed)
		cbShowExceededDependencies.set_active(self.preferences['showExceededDependencies'])

		# Expiration warning
		sbExpirationWarning = builder.get_object("sbExpirationWarning")
		sbExpirationWarning.connect('value-changed', self.__on_sbExpirationWarning_valuechanged)
		sbExpirationWarning.set_value(self.preferences['expirationWarning'])

		# Colors
		cbInabordable = builder.get_object("cbInabordable")
		cbInabordable.connect('color-set', self.__on_colorbutton_colorset)
		cbInabordable.set_color(gtk.gdk.color_parse(self.preferences['color_unabordable']))

		cbInProcess = builder.get_object("cbInProcess")
		cbInProcess.connect('color-set', self.__on_colorbutton_colorset)
		cbInProcess.set_color(gtk.gdk.color_parse(self.preferences['color_inprocess']))

		cbAvailable = builder.get_object("cbAvailable")
		cbAvailable.connect('color-set', self.__on_colorbutton_colorset)
		cbAvailable.set_color(gtk.gdk.color_parse(self.preferences['color_available']))

		cbSatisfacted = builder.get_object("cbSatisfacted")
		cbSatisfacted.connect('color-set', self.__on_colorbutton_colorset)
		cbSatisfacted.set_color(gtk.gdk.color_parse(self.preferences['color_satisfacted']))


	def __on_chkDefaultDB_toggled(self, widget):
		self.fcDefaultDB.set_sensitive(widget.get_active())


	def __on_colorbutton_colorset(self, widget):
		self.preferences[widget.get_title()] = widget.get_color()


	def __on_Preferences_response(self, widget, response):
		if response == 1:
			preferences.Store(self.preferences)


	def __on_chkShowSharp_toggled(self, widget):
		self.preferences["showSharp"] = widget.get_active()


	def __on_cbShowExceededDependencies_changed(self, widget):
		print "__on_showExceededDependencies_toggled",widget.get_active()
		self.preferences["showExceededDependencies"] = widget.get_active()


	def __on_sbExpirationWarning_valuechanged(self, widget):
		print "__on_sbExpirationWarning_valuechanged",widget.get_value_as_int()
		self.preferences["expirationWarning"] = widget.get_value_as_int()
