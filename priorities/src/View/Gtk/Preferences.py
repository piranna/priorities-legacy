import gtk

from View.Gtk import _,Gtk


class Preferences(Gtk):
	def __init__(self):
		Gtk.__init__(self, "Preferences")

		# [To-Do] Check diferences between stored and loaded config

		#
		# DataBase

		self.fcDefaultDB = self.builder.get_object("fcDefaultDB")
		self.fcDefaultDB.set_filename(self.config.Get('database'))
		self.fcDefaultDB.set_sensitive(self.config.Get('useDefaultDB'))

		self.builder.get_object("chkDefaultDB").set_active(self.config.Get('useDefaultDB'))

		#
		# Graphic

		self.redraw = None

		self.builder.get_object("chkShowSharp").set_active(self.config.Get('showSharp'))
		self.builder.get_object("chkShowArrowHeads").set_active(self.config.Get('showArrowHeads'))
		self.builder.get_object("chkShowLayoutBorders").set_active(self.config.Get('showLayoutBorders'))

		#
		# Button colors

		self.builder.get_object("cbInabordable").set_color(gtk.gdk.color_parse(self.config.Get('color_unabordable')))
		self.builder.get_object("cbInProcess").set_color(gtk.gdk.color_parse(self.config.Get('color_inprocess')))
		self.builder.get_object("cbAvailable").set_color(gtk.gdk.color_parse(self.config.Get('color_available')))
		self.builder.get_object("cbSatisfacted").set_color(gtk.gdk.color_parse(self.config.Get('color_satisfacted')))

		#
		# Objectives

		self.builder.get_object("cbShowExceededDependencies").set_active(self.config.Get('showExceededDependencies'))
		self.builder.get_object("sbExpirationWarning").set_value(self.config.Get('expirationWarning'))
		self.builder.get_object("chkRemoveOrphanRequeriments").set_active(self.config.Get('removeOrphanRequeriments'))

		self.chkConfirmDeleteCascade = self.builder.get_object("chkConfirmDeleteCascade")
		self.chkConfirmDeleteCascade.set_active(self.config.Get('confirmDeleteCascade'))
		self.chkConfirmDeleteCascade.set_sensitive(self.config.Get('deleteCascade'))

		self.builder.get_object("chkDeleteCascade").set_active(self.config.Get('deleteCascade'))


	# Database

	def on_chkDefaultDB_toggled(self, widget):
		"Set if user should be asked for the database at startup"
		self.config.Set("useDefaultDB", widget.get_active())
		self.fcDefaultDB.set_sensitive(widget.get_active())


	def on_fcDefaultDB_expose_event(self, widget,event):
		"Get the database name from the config if the gtk.filechooserbutton get empty"
		if not widget.get_filename():
			widget.set_filename(self.config.Get('database'))

	def on_fcDefaultDB_file_set(self, widget):
		"Set the database set by the gtk.filechooserbutton"
		self.config.Set("database", widget.get_filename())


	# Objectives colors

	def on_colorbutton_color_set(self, widget):
		"""
		Set the selected color
		and redraw the full objectives tree
		"""
		self.config.Set(widget.get_title(), widget.get_color())
		self.redraw = "tree"


	# Dialog

	def on_Preferences_response(self, widget, response):
		"Store the config when closing the dialog"
		if response == 1:
			self.config.Store()


	# Graph

	def on_chkShowSharp_toggled(self, widget):
		"Set to draw the tree sharp"
		self.config.Set("showSharp", widget.get_active())
		if self.redraw != "tree":
			self.redraw = "arrows"


	def on_chkShowArrowHeads_toggled(self, widget):
		"Set to draw the arrow heads"
		self.config.Set("showArrowHeads", widget.get_active())
		if self.redraw != "tree":
			self.redraw = "arrows"


	def on_chkShowLayoutBorders_toggled(self, widget):
		"Set to draw the layout borders"
		self.config.Set("showLayoutBorders", widget.get_active())
		if self.redraw != "tree":
			self.redraw = "arrows"


	# Objectives

	def on_chkRemoveOrphanRequeriments_toggled(self, widget):
		"Set to remove orphans"
		self.config.Set("removeOrphanRequeriments", widget.get_active())


	def on_chkDeleteCascade_toggled(self, widget):
		"Set if objectives should be deleted in cascade"
		self.config.Set("deleteCascade", widget.get_active())
		self.chkConfirmDeleteCascade.set_sensitive(widget.get_active())


	def on_chkConfirmDeleteCascade_toggled(self, widget):
		"Set if user must be asked to confirm when deleting in cascade"
		self.config.Set("confirmDeleteCascade", widget.get_active())


	def on_cbShowExceededRequeriments_changed(self, widget):
		"""
		Set if exceeded requeriments should be showed
		and redraw the full objectives tree
		"""
		self.config.Set("showExceededRequeriments", widget.get_active())
		self.redraw = "tree"


	def on_sbExpirationWarning_value_changed(self, widget):
		"""
		Set the expiration warning days interval
		and redraw the full objectives tree
		"""
		self.config.Set("expirationWarning", widget.get_value_as_int())
		self.redraw = "tree"

