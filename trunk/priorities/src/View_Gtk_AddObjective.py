import datetime

import View_Gtk


class AddObjective(View_Gtk.View_Gtk):
	__destroy = True

	def __init__(self, objective=None):
		View_Gtk.View_Gtk.__init__(self)

		self.__objective = objective

		self.window = self.builder.get_object("AddObjective")
		self.window.connect('delete_event',self.__on_AddObjective_delete_event)
		self.window.connect('response',self.__on_AddObjective_response)

		# Objective & quantity
		self.txtObjective = self.builder.get_object("txtObjective")
		self.txtQuantity = self.builder.get_object("txtQuantity")

		# Expiration
		self.chkExpiration = self.builder.get_object("chkExpiration")
		self.chkExpiration.connect('toggled', self.__on_chkExpiration_toggled)

		self.vbCalendarHour = self.builder.get_object("vbCalendarHour")
		self.calExpiration = self.builder.get_object("calExpiration")
		self.sbHour = self.builder.get_object("sbHour")
		self.sbMinute = self.builder.get_object("sbMinute")
		self.sbSecond = self.builder.get_object("sbSecond")

		# Requeriments
		self.txtRequeriments = self.builder.get_object("txtRequirements")
		txtBuffer = self.txtRequeriments.get_buffer()

		# Set data
		if objective:
			objective = self.controller.GetObjective_byId(objective)

			btnDelete = self.builder.get_object("btnDelete")
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
				for dependency in self.controller.DirectDependencies(objective['id']):
					if(last_requeriment and last_requeriment==dependency['requeriment']):
						dependencies += ','
					else:
						if(last_requeriment):
							dependencies += '\n'
						last_requeriment = dependency['requeriment']
					if(dependency['alternative']):
						dependencies += self.controller.GetName(dependency['alternative'])
				txtBuffer.set_text(dependencies)

		# Old data
		self.oldObjective = self.txtObjective.get_text()
		self.oldQuantity = self.txtQuantity.get_text()

		start,end = txtBuffer.get_bounds()
		self.oldRequeriments = txtBuffer.get_text(start,end)



	def __StoreData(self):

		# [To-Do] Check expiration modification
		closeDialog = (self.txtObjective.get_text() and self.txtQuantity.get_text())

		if closeDialog:

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
			dependencies = None

			txtBuffer = self.txtRequeriments.get_buffer()
			start,end = txtBuffer.get_bounds()
			txtBuffer = txtBuffer.get_text(start,end)
			if(txtBuffer==self.oldRequeriments):
				print "\tigual"
				txtBuffer = None

			else:
				print "\tdistintos"
				print "\t",self.oldRequeriments
				print "\t",txtBuffer

				objective_id = self.controller.GetId(self.txtObjective.get_text())

				if self.config.Get('removeOrphanRequeriments'):
					dependencies = self.controller.DirectDependencies(objective_id)
					print dependencies

				self.controller.DelRequeriments_ById(objective_id)

				# Requeriments
				txtBuffer = txtBuffer.splitlines()
				for i in range(0,len(txtBuffer)):

					# Alternatives
					duplicates = []

					txtBuffer[i] = txtBuffer[i].split(',')
					for j in range(0,len(txtBuffer[i])):
						txtBuffer[i][j] = txtBuffer[i][j].strip()

						# If alternative is previously defined in this requeriment
						# ignore it
						if j>0 and txtBuffer[i][j] in txtBuffer[i][0:(j-1)]:
							#del txtBuffer[i][j]
							duplicates.append(j)

					for j in reversed(duplicates):
						del txtBuffer[i][j]

			# Add objective
			self.controller.AddObjective(self.txtObjective.get_text(),
											self.txtQuantity.get_text(),
											self.expiration,
											txtBuffer)

			self.controller.DeleteOrphans(dependencies)

		return closeDialog


	def __Delete(self):
		if self.__objective:
			if(self.config.Get('deleteCascade')
			and len(self.controller.DirectDependencies(self.__objective))>1):
				dialog = DeleteCascade(self.controller, self.__objective)

				dialog.window.set_transient_for(self.window)
				response = dialog.window.run()
				dialog.window.destroy()

				if response > 0:
					self.__CreateTree()

			else:
				dialog = gtk.MessageDialog(self.window,
											0,
											gtk.MESSAGE_QUESTION,
											gtk.BUTTONS_YES_NO,
											"Desea eliminar el objetivo "+self.controller.GetName(self.__objective)+"?")
				response = dialog.run()
				dialog.destroy()
				if response == gtk.RESPONSE_YES:
					self.controller.DeleteObjective(self.__objective)
					self.__CreateTree()

		return True


	def __Cancel(self):
		closeDialog = (self.oldObjective == self.txtObjective.get_text())

		if not closeDialog:
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


	def __on_AddObjective_delete_event(self, widget,data=None):
		if not self.__destroy:
			self.__destroy = True
			return True


	def __on_AddObjective_response(self, widget, response):
		closeDialog = True

		if response == 1:
			closeDialog = self.__StoreData()
		elif response == 2:
			closeDialog = self.__Delete()
		else:
			closeDialog = self.__Cancel()

			if response == -4 and not closeDialog:
				self.__destroy = False

		if not closeDialog:
			self.window.emit_stop_by_name('response')


	def __on_chkExpiration_toggled(self, widget):
		self.vbCalendarHour.set_sensitive(widget.get_active())

