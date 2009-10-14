import gtk

import View_Gtk

import config


class Preferences(View_Gtk.View):
	def __init__(self):
		View_Gtk.View.__init__(self)

		self.config = config.Load()

		# [To-Do] Check diferences between stored and loaded config

		# config window
		self.window = self.builder.get_object("config")
		self.window.connect('response',self.__on_config_response)

		#
		# DataBase

		# Use default database
		chkDefaultDB = self.builder.get_object("chkDefaultDB")
		chkDefaultDB.connect('toggled', self.__on_chkDefaultDB_toggled)
		chkDefaultDB.set_active(self.config['useDefaultDB'])

		# Default database
		self.fcDefaultDB = self.builder.get_object("fcDefaultDB")
		self.fcDefaultDB.connect('file-set', self.__on_fcDefaultDB_fileset)
		self.fcDefaultDB.set_filename(self.config['database'])

		chkDefaultDB.toggled()

		#
		# Graphic

		# Show sharp
		chkShowSharp = self.builder.get_object("chkShowSharp")
		chkShowSharp.connect('toggled', self.__on_chkShowSharp_toggled)
		chkShowSharp.set_active(self.config['showSharp'])

		# Show arrow heads
		chkShowArrowHeads = self.builder.get_object("chkShowArrowHeads")
		chkShowArrowHeads.connect('toggled', self.__on_chkShowArrowHeads_toggled)
		chkShowArrowHeads.set_active(self.config['showArrowHeads'])

		#
		# Button colors

		cbInabordable = self.builder.get_object("cbInabordable")
		cbInabordable.connect('color-set', self.__on_colorbutton_colorset)
		cbInabordable.set_color(gtk.gdk.color_parse(self.config['color_unabordable']))

		cbInProcess = self.builder.get_object("cbInProcess")
		cbInProcess.connect('color-set', self.__on_colorbutton_colorset)
		cbInProcess.set_color(gtk.gdk.color_parse(self.config['color_inprocess']))

		cbAvailable = self.builder.get_object("cbAvailable")
		cbAvailable.connect('color-set', self.__on_colorbutton_colorset)
		cbAvailable.set_color(gtk.gdk.color_parse(self.config['color_available']))

		cbSatisfacted = self.builder.get_object("cbSatisfacted")
		cbSatisfacted.connect('color-set', self.__on_colorbutton_colorset)
		cbSatisfacted.set_color(gtk.gdk.color_parse(self.config['color_satisfacted']))

		#
		# Objectives

		# Show exceeded dependencies
		cbShowExceededDependencies = self.builder.get_object("cbShowExceededDependencies")
		cbShowExceededDependencies.connect('changed', self.__on_cbShowExceededDependencies_changed)
		cbShowExceededDependencies.set_active(self.config['showExceededDependencies'])

		# Expiration warning
		sbExpirationWarning = self.builder.get_object("sbExpirationWarning")
		sbExpirationWarning.connect('value-changed', self.__on_sbExpirationWarning_valuechanged)
		sbExpirationWarning.set_value(self.config['expirationWarning'])

		# Remove orphan requeriments
		chkRemoveOrphanRequeriments = self.builder.get_object("chkRemoveOrphanRequeriments")
		chkRemoveOrphanRequeriments.connect('toggled', self.__on_chkRemoveOrphanRequeriments_toggled)
		chkRemoveOrphanRequeriments.set_active(self.config['removeOrphanRequeriments'])

		# Delete on cascade
		chkDeleteCascade = self.builder.get_object("chkDeleteCascade")
		chkDeleteCascade.connect('toggled', self.__on_chkDeleteCascade_toggled)
		chkDeleteCascade.set_active(self.config['deleteCascade'])

		# Confirm delete on cascade
		self.chkConfirmDeleteCascade = self.builder.get_object("chkConfirmDeleteCascade")
		self.chkConfirmDeleteCascade.connect('toggled', self.__on_chkConfirmDeleteCascade_toggled)
		self.chkConfirmDeleteCascade.set_active(self.config['confirmDeleteCascade'])


	def __on_chkDefaultDB_toggled(self, widget):
		self.fcDefaultDB.set_sensitive(widget.get_active())


	def __on_fcDefaultDB_fileset(self, widget):
		filename = widget.get_filename()
		if filename:
			self.config["database"] = filename


	def __on_colorbutton_colorset(self, widget):
		self.config[widget.get_title()] = widget.get_color()


	def __on_config_response(self, widget, response):
		if response == 1:
			config.Store(self.config)


	def __on_chkShowSharp_toggled(self, widget):
		self.config["showSharp"] = widget.get_active()


	def __on_chkShowArrowHeads_toggled(self, widget):
		self.config["showArrowHeads"] = widget.get_active()


	def __on_chkRemoveOrphanRequeriments_toggled(self, widget):
		self.config["removeOrphanRequeriments"] = widget.get_active()


	def __on_chkDeleteCascade_toggled(self, widget):
		self.config["deleteCascade"] = widget.get_active()
		self.chkConfirmDeleteCascade.set_sensitive(widget.get_active())


	def __on_chkConfirmDeleteCascade_toggled(self, widget):
		self.config["confirmDeleteCascade"] = widget.get_active()


	def __on_cbShowExceededDependencies_changed(self, widget):
		self.config["showExceededDependencies"] = widget.get_active()


	def __on_sbExpirationWarning_valuechanged(self, widget):
		self.config["expirationWarning"] = widget.get_value_as_int()

