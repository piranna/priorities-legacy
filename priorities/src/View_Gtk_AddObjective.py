import datetime
import gtk


class AddObjective:
	def __init__(self, controller, objective=None):
		self.__controller = controller
		self.__objective = objective

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("AddObjective")
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
			self.__controller.DeleteObjective(self.__objective)

		return True


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
		elif response == 2:
			closeDialog = self.__Delete()
		else:
			closeDialog = self.__Cancel()

		if not closeDialog:
			self.window.emit_stop_by_name('response')


	def __on_chkExpiration_toggled(self, widget):
		self.vbCalendarHour.set_sensitive(widget.get_active())

