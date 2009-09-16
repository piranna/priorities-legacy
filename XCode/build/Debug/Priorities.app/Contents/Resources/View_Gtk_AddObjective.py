import gtk


class AddObjective:
	def __init__(self, controller, objective=None):
		self.__controller = controller

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("AddObjective")
		self.window.connect('destroy',self.__on_AddObjective_destroy)
		self.window.connect('response',self.__on_AddObjective_response)

		self.txtObjective = builder.get_object("txtObjective")
		self.txtQuantity = builder.get_object("txtQuantity")
#		self.expiration = builder.get_object("expiration")
#		self.txtRequeriments = builder.get_object("txtRequeriments")

		if objective:
			objective = self.__controller.GetObjective_byId(objective)

			if objective:
				self.txtObjective.set_text(objective["name"])

				self.txtQuantity.set_text(str(objective["quantity"]))

#				if objective["expiration"]:
#					self.expiration.set_text(objective["expiration"])

#				self.txtRequeriments.set_text()

		self.oldObjective = self.txtObjective.get_text()
		self.oldQuantity = self.txtQuantity.get_text()
#		self.oldExpiration = self.txtExpiration.get_text()
#		self.oldRequeriments = self.txtRequeriments.get_text()



	def __StoreData(self):
		print "StoreData"

		closeDialog = (self.txtObjective.get_text() and self.txtQuantity.get_text())

		if closeDialog:
			self.__controller.AddObjective(self.txtObjective.get_text(), self.txtQuantity.get_text())
			print "\tDatos guardados"
		else:
			print "\tStoreData no cierra"

		return closeDialog


	def __Cancel(self):
		print "Cancel"

		closeDialog = (self.oldObjective == self.txtObjective.get_text())

		if not closeDialog:
			print "\tCancel no cierra"

		return closeDialog


	def __on_AddObjective_destroy(self, widget):
		print "destroy"

		if not self.__Cancel():
			self.window.emit_stop_by_name('destroy')


	def __on_AddObjective_response(self, widget, response):
		print "response"

		closeDialog = True

		if response == 1:
			closeDialog = self.__StoreData()
		else:
			closeDialog = self.__Cancel()

		if not closeDialog:
			self.window.emit_stop_by_name('response')