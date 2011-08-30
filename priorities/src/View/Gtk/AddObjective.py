import datetime

import gtk

import View.Gtk
_ = View.Gtk._

from View_Gtk_DeleteCascade import *


class AddObjective(View.Gtk.View_Gtk):
	__destroy = True

	def __init__(self, objective=None):
		View.Gtk.View_Gtk.__init__(self, "AddObjective")

		self.__objective = objective

		# Objective & quantity
		self.txtObjective = self.builder.get_object("txtObjective")
		self.txtQuantity = self.builder.get_object("txtQuantity")

		# Expiration
		self.chkExpiration = self.builder.get_object("chkExpiration")

		self.vbCalendarHour = self.builder.get_object("vbCalendarHour")
		self.calExpiration = self.builder.get_object("calExpiration")
		self.sbHour = self.builder.get_object("sbHour")
		self.sbMinute = self.builder.get_object("sbMinute")
		self.sbSecond = self.builder.get_object("sbSecond")

		# Requeriments
		self.__vbRequeriments = self.builder.get_object("vbRequeriments")
		self.__btnDel = self.builder.get_object("btnDel_Requeriment")

		# Set data
		if objective:
			objective = self.controller.GetObjective(objective)

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

				# Requeriments
				last_requeriment = None
				model = None

				for requeriment in self.controller.DirectRequeriments(objective['id']):
					if(last_requeriment != requeriment['requeriment']):
						last_requeriment=requeriment['requeriment']

						vbRequeriments = self.builder.get_object("vbRequeriments")
						vbRequeriments.pack_end(self.builder.get_object("expRequeriment"))

						model = self.builder.get_object("treeview2").get_model()

					if model:
						model.append((requeriment['alternative'],))

		# Old data
		self.oldObjective = self.txtObjective.get_text()
		self.oldQuantity = self.txtQuantity.get_text()

#		start,end = txtBuffer.get_bounds()
#		self.oldRequeriments = txtBuffer.get_text(start,end)

		self.__btnDel_Requeriment_Sensitivity()



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

			# Requeriments and alternatives
			orphans = None

			if(txtBuffer==self.oldRequeriments):
				print "\tigual"
				txtBuffer = None

			else:
				print "\tdistintos"
				print "\t",self.oldRequeriments
				print "\t",txtBuffer

				objective = self.txtObjective.get_text()

				if self.config.Get('removeOrphanRequeriments'):
					orphans = self.controller.DirectRequeriments(objective)
					print orphans

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
			self.controller.AddObjective(objective,
										self.txtQuantity.get_text(),
										self.expiration,
										requeriments)

			self.controller.DeleteOrphans(orphans)

		return closeDialog


	def __Delete(self):
		if self.__objective:
			if(self.config.Get('deleteCascade')
			and len(self.controller.DirectRequeriments(self.__objective))>1):
				dialog = DeleteCascade(self.__objective)

				dialog.window.set_transient_for(self.window)
				response = dialog.window.run()
				dialog.window.destroy()

#				if response > 0:
#					self.__CreateTree()

			else:
				dialog = gtk.MessageDialog(self.window,
											0,
											gtk.MESSAGE_QUESTION,
											gtk.BUTTONS_YES_NO,
											_("Do you want to delete the objective ")+self.__objective+"?")
				response = dialog.run()
				dialog.destroy()
				if response == gtk.RESPONSE_YES:
					self.controller.DeleteObjective(self.__objective)
#					self.__CreateTree()

		return True


	def __Cancel(self):
		closeDialog = (self.oldObjective == self.txtObjective.get_text())

		if not closeDialog:
			dialog = gtk.MessageDialog(self.window,
										0,
										gtk.MESSAGE_QUESTION,
										gtk.BUTTONS_YES_NO,
										_("The objective have been modified"))
			dialog.format_secondary_text(_("The objective have been modified and the changes will be lost. Are you sure do you want to continue?"))
			response = dialog.run()
			dialog.destroy()
			if response == gtk.RESPONSE_YES:
				return True

		return closeDialog


	def on_AddObjective_delete_event(self, widget,data=None):
		if not self.__destroy:
			self.__destroy = True
			return True


	def on_AddObjective_response(self, widget, response):
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


	def on_chkExpiration_toggled(self, widget):
		self.vbCalendarHour.set_sensitive(widget.get_active())


	def __btnDel_Requeriment_Sensitivity(self):
		self.__btnDel.set_sensitive(len(self.__vbRequeriments.get_children()))

	def on_btnAdd_Requeriment_clicked(self, widget):
		vbRequeriments = self.builder.get_object("vbRequeriments")
		vbRequeriments.pack_end(Alternative())

		self.__btnDel_Requeriment_Sensitivity()

	def on_btnDel_Requeriment_clicked(self, widget):

		self.__btnDel_Requeriment_Sensitivity()


class Alternative(View_Gtk.View_Gtk):

	def __init__(self):
		View_Gtk.View_Gtk.__init__(self, "expRequeriment")

		self.__model = self.builder.get_object("lstAlternatives")
		self.__model.clear()
		self.__btnDel = self.builder.get_object("btnDel_Alternative")

		# Fill model


	def __btnDel_Alternative_Sensitivity(self):
		pass
#		self.__btnDel.set_sensitive(len(self.__model.))


	def on_btnAdd_Alternative_clicked(self, widget):
		self.__model.append()

		self.__btnDel_Alternative_Sensitivity()

	def on_btnDel_Alternative_clicked(self, widget):

		self.__btnDel_Alternative_Sensitivity()

