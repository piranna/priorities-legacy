import gtk

import View_Gtk


class Preferences(View_Gtk.View_Gtk):
	def __init__(self):
		View_Gtk.View_Gtk.__init__(self)

		# [To-Do] Check diferences between stored and loaded config

		# Preferences window
		self.window = self.builder.get_object("Preferences")
		self.window.connect('response',self.__on_Preferences_response)

		#
		# DataBase

		# Use default database
		chkDefaultDB = self.builder.get_object("chkDefaultDB")
		chkDefaultDB.set_active(self.config.Get('useDefaultDB'))

		# Default database
		self.fcDefaultDB = self.builder.get_object("fcDefaultDB")
		self.fcDefaultDB.connect('file-set', self.__on_fcDefaultDB_fileset)
		self.fcDefaultDB.set_filename(self.config.Get('database'))
		self.fcDefaultDB.set_sensitive(self.config.Get('useDefaultDB'))

		chkDefaultDB.connect('toggled', self.__on_chkDefaultDB_toggled)

		#
		# Graphic

		self.redraw = None

		# Show sharp
		chkShowSharp = self.builder.get_object("chkShowSharp")
		chkShowSharp.connect('toggled', self.__on_chkShowSharp_toggled)
		chkShowSharp.set_active(self.config.Get('showSharp'))

		# Show arrow heads
		chkShowArrowHeads = self.builder.get_object("chkShowArrowHeads")
		chkShowArrowHeads.connect('toggled', self.__on_chkShowArrowHeads_toggled)
		chkShowArrowHeads.set_active(self.config.Get('showArrowHeads'))

		#
		# Button colors

		cbInabordable = self.builder.get_object("cbInabordable")
		cbInabordable.connect('color-set', self.__on_colorbutton_colorset)
		cbInabordable.set_color(gtk.gdk.color_parse(self.config.Get('color_unabordable')))

		cbInProcess = self.builder.get_object("cbInProcess")
		cbInProcess.connect('color-set', self.__on_colorbutton_colorset)
		cbInProcess.set_color(gtk.gdk.color_parse(self.config.Get('color_inprocess')))

		cbAvailable = self.builder.get_object("cbAvailable")
		cbAvailable.connect('color-set', self.__on_colorbutton_colorset)
		cbAvailable.set_color(gtk.gdk.color_parse(self.config.Get('color_available')))

		cbSatisfacted = self.builder.get_object("cbSatisfacted")
		cbSatisfacted.connect('color-set', self.__on_colorbutton_colorset)
		cbSatisfacted.set_color(gtk.gdk.color_parse(self.config.Get('color_satisfacted')))

		#
		# Objectives

		# Show exceeded dependencies
		cbShowExceededDependencies = self.builder.get_object("cbShowExceededDependencies")
		cbShowExceededDependencies.connect('changed', self.__on_cbShowExceededDependencies_changed)
		cbShowExceededDependencies.set_active(self.config.Get('showExceededDependencies'))

		# Expiration warning
		sbExpirationWarning = self.builder.get_object("sbExpirationWarning")
		sbExpirationWarning.connect('value-changed', self.__on_sbExpirationWarning_valuechanged)
		sbExpirationWarning.set_value(self.config.Get('expirationWarning'))

		# Remove orphan requeriments
		chkRemoveOrphanRequeriments = self.builder.get_object("chkRemoveOrphanRequeriments")
		chkRemoveOrphanRequeriments.connect('toggled', self.__on_chkRemoveOrphanRequeriments_toggled)
		chkRemoveOrphanRequeriments.set_active(self.config.Get('removeOrphanRequeriments'))

		# Delete on cascade
		chkDeleteCascade = self.builder.get_object("chkDeleteCascade")
		chkDeleteCascade.set_active(self.config.Get('deleteCascade'))

		# Confirm delete on cascade
		self.chkConfirmDeleteCascade = self.builder.get_object("chkConfirmDeleteCascade")
		self.chkConfirmDeleteCascade.connect('toggled', self.__on_chkConfirmDeleteCascade_toggled)
		self.chkConfirmDeleteCascade.set_active(self.config.Get('confirmDeleteCascade'))
		self.chkConfirmDeleteCascade.set_sensitive(self.config.Get('deleteCascade'))

		chkDeleteCascade.connect('toggled', self.__on_chkDeleteCascade_toggled)


	def __on_chkDefaultDB_toggled(self, widget):
		self.config.Set("useDefaultDB", widget.get_active())
		self.fcDefaultDB.set_sensitive(widget.get_active())


	def __on_fcDefaultDB_fileset(self, widget):
		filename = widget.get_filename()
		if filename:
			self.config.Set("database", filename)


	def __on_colorbutton_colorset(self, widget):
		self.config.Set(widget.get_title(), widget.get_color())
		self.redraw = "tree"


	def __on_Preferences_response(self, widget, response):
		if response == 1:
			self.config.Store()


	def __on_chkShowSharp_toggled(self, widget):
		self.config.Set("showSharp", widget.get_active())
		if self.redraw != "tree":
			self.redraw = "arrows"


	def __on_chkShowArrowHeads_toggled(self, widget):
		self.config.Set("showArrowHeads", widget.get_active())
		if self.redraw != "tree":
			self.redraw = "arrows"


	def __on_chkRemoveOrphanRequeriments_toggled(self, widget):
		self.config.Set("removeOrphanRequeriments", widget.get_active())


	def __on_chkDeleteCascade_toggled(self, widget):
		self.config.Set("deleteCascade", widget.get_active())
		self.chkConfirmDeleteCascade.set_sensitive(widget.get_active())


	def __on_chkConfirmDeleteCascade_toggled(self, widget):
		self.config.Set("confirmDeleteCascade", widget.get_active())


	def __on_cbShowExceededDependencies_changed(self, widget):
		self.config.Set("showExceededDependencies", widget.get_active())
		self.redraw = "tree"


	def __on_sbExpirationWarning_valuechanged(self, widget):
		self.config.Set("expirationWarning", widget.get_value_as_int())
		self.redraw = "tree"

