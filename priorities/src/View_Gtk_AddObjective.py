import datetime
import gtk


class AddObjective:
	__destroy = True

	def __init__(self, controller, objective=None):
		self.__controller = controller
		self.__objective = objective

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("AddObjective")
		self.window.connect('delete-event',self.__on_AddObjective_deleteevent)
		self.window.connect('destroy',self.__on_AddObjective_destroy)
		self.window.connect('response',self.__on_AddObjective_response)

		# Objective & quantity
		self.txtObjective = builder.get_object("txtObjective")
		self.txtQuantity = builder.get_object("txtQuantity")

		# Expiration
		self.chkExpiration = builder.get_object("chkExpiration")
		self.chkExpiration.connect('toggled', self.__on_chkExpiration_toggled)

		self.vbCalendarHour = builder.get_object("vbCalendarHour")
		self.calExpiration = builder.get_object("calExpiration")
		self.sbHour = builder.get_object("sbHour")
		self.sbMinute = builder.get_object("sbMinute")
		self.sbSecond = builder.get_object("sbSecond")

		# Requeriments
		self.txtRequeriments = builder.get_object("txtRequirements")
		txtBuffer = self.txtRequeriments.get_buffer()

		# Set data
		if objective:
			objective = self.__controller.GetObjective_byId(objective)

			btnDelete = builder.get_object("btnDelete")
			btnDelete.show()

			if objective:
				self.txtObjective.set_text(objective["name"])

				self.txtQuantity.set_text(str(objective["quantity"]))

				self.expiration=None
				if objective["expiration"]:
					self.chkExpiration.set_active(True)
					self.chkExpiration.toggled()

					self.expiration = datetime.datetime.strptime(objective["expiration"], "%Y-%m-%d %H:%M:%S")

					self.calExpiration.select_month(self.expiration.month-1, self.expiration.year)
					self.calExpiration.select_day(self.expiration.day)
					self.sbHour.set_value(self.expiration.hour)
					self.sbMinute.set_value(self.expiration.minute)
					self.sbSecond.set_value(self.expiration.second)

				dependencies = ""
				last_requeriment = None
				for dependency in self.__controller.DirectDependencies(objective['id']):
					if(last_requeriment and last_requeriment==dependency['requeriment']):
						dependencies += ','
					else:
						if(last_requeriment):
							dependencies += '\n'
						last_requeriment = dependency['requeriment']
					if(dependency['alternative']):
						dependencies += self.__controller.GetName(dependency['alternative'])
				txtBuffer.set_text(dependencies)

		# Old data
		self.oldObjective = self.txtObjective.get_text()
		self.oldQuantity = self.txtQuantity.get_text()

		start,end = txtBuffer.get_bounds()
		self.oldRequeriments = txtBuffer.get_text(start,end)



	def __StoreData(self):
		print "StoreData"

		# [To-Do] Check expiration modification
		closeDialog = (self.txtObjective.get_text() and self.txtQuantity.get_text())

		if closeDialog:
			print "\tGuardar datos"

			# Expiration
			if(self.chkExpiration.get_active()):
				self.expiration = self.calExpiration.get_date()
				self.expiration = datetime.datetime(self.expiration[0],
													self.expiration[1]+1,
													self.expiration[2],
													self.sbHour.get_value_as_int(),
													self.sbMinute.get_value_as_int(),
													self.sbSecond.get_value_as_int())
			else:
				self.expiration = None

			# Requeriments
			txtBuffer = self.txtRequeriments.get_buffer()
			start,end = txtBuffer.get_bounds()
			txtBuffer = txtBuffer.get_text(start,end)
			if(txtBuffer==self.oldRequeriments):
				txtBuffer = None

			else:
				self.__controller.DelRequeriments(self.txtObjective.get_text())
				txtBuffer = txtBuffer.splitlines()
				for i in range(0,len(txtBuffer)):
					txtBuffer[i] = txtBuffer[i].split(',')
					for j in range(0,len(txtBuffer[i])):
						txtBuffer[i][j] = txtBuffer[i][j].strip()

			# Add objective
			self.__controller.AddObjective(self.txtObjective.get_text(),
											self.txtQuantity.get_text(),
											self.expiration,
											txtBuffer)

		else:
			print "\tStoreData no cierra"

		return closeDialog


	def __Delete(self):
		print "Delete"
		if self.__objective:
			import preferences
			preferences = preferences.Load()
			self.__controller.DeleteObjective(self.__objective,preferences['deleteCascade'])

		return True


	def __Cancel(self):
		print "Cancel"

		closeDialog = (self.oldObjective == self.txtObjective.get_text())

		if not closeDialog:
			print "\tCancel no cierra"
			dialog = gtk.MessageDialog(self.window,
										0,
										gtk.MESSAGE_QUESTION,
										gtk.BUTTONS_YES_NO,
										"El objetivo se ha modificado")
			dialog.format_secondary_text("El objetivo se ha modificado y los cambios se perderan. Esta seguro que desea continuar?")
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				return True

		return closeDialog


	def __on_AddObjective_deleteevent(self, widget,data=None):
		print "delete-event"

		if not self.__destroy:
			self.window.emit_stop_by_name('delete-event')
			self.__destroy = True

	
	def __on_AddObjective_destroy(self, widget):
		print "destroy"

#		if not self.__destroy:
#		self.window.emit_stop_by_name('destroy')
#			self.__destroy = True


	def __on_AddObjective_response(self, widget, response):
		print "response"

		closeDialog = True

		if response == 1:
			closeDialog = self.__StoreData()
		elif response == 2:
			closeDialog = self.__Delete()
		else:
			print "__on_AddObjective_response",response
			closeDialog = self.__Cancel()

			if response == -4 and not closeDialog:
				self.__destroy = False

		print "closeDialog",closeDialog
		if not closeDialog:
			self.window.emit_stop_by_name('response')


	def __on_chkExpiration_toggled(self, widget):
		self.vbCalendarHour.set_sensitive(widget.get_active())

