import View_Gtk


class DeleteCascade(View_Gtk.View):
	def __init__(self, objective_id):
		View_Gtk.View.__init__(self)

		# Model
		treeview = self.builder.get_object("treeview")
		self.__model = treeview.get_model()

		self.__tree = {}

		# Fill model
		def Append(tree, parent=None):
			print "Append antes", parent,tree
#			self.__tree.get(objective_id, []).append(path)
			for objective_id in tree.keys():
				Append(tree[objective_id],
						self.__model.append(parent,
									(objective_id, self.controller.GetName(objective_id), True,False)))
			print "Append despu", parent,tree
			print

		Append(self.controller.Get_DeleteObjective_Tree(objective_id),
				self.__model.append(None,
							(objective_id, self.controller.GetName(objective_id), True,False)))

		# If confirmDeleteCascade,
		# show window
		confirmDeleteCascade = self.config.Get('confirmDeleteCascade')
		if confirmDeleteCascade:
			self.window = self.builder.get_object("DeleteCascade")
			self.window.connect('response',self.__on_DeleteCascade_response)

			deleteCell = self.builder.get_object("deleteCell")
			deleteCell.connect('toggled', self.__on_deleteCell_toggled)

			chkConfirmDeleteCascade = self.builder.get_object("chkConfirmDeleteCascade1")
			chkConfirmDeleteCascade.connect('toggled', self.__on_chkConfirmDeleteCascade_toggled)
			chkConfirmDeleteCascade.set_active(confirmDeleteCascade)

			treeview.expand_all()


	def DeleteObjective_recursive(self, iterator = None):
		if not iterator:
			iterator = self.__model.get_iter_root()

		deleted = 0

		# If objective is marked,
		# delete it
		if self.__model.get_value(iterator,2):
			if self.__model.get_value(iterator,3):
				print "DelRequeriment",self.__model.get_value(self.__model.iter_parent(iterator),0),self.__model.get_value(iterator,0)
				self.controller.DelAlternatives(self.__model.get_value(iterator,0),
												self.__model.get_value(self.__model.iter_parent(iterator),0))

			else:
				print "DelObjective",self.__model.get_value(iterator,0)
				self.controller.DeleteObjective(self.__model.get_value(iterator,0),
												self.config.Get('removeOrphanRequeriments'))

			deleted += 1

		# Delete objective marqued requeriments, if any
		iterator = self.__model.iter_children(iterator)
		while iterator:
			deleted += self.DeleteObjective_recursive(iterator)
			iterator = self.__model.iter_next(iterator)

		return deleted


	def __on_DeleteCascade_response(self, widget, response):
		if response>0:
			# [To-Do] Poner response a 0 si no se elimina ningun objetivo
			deleted = self.DeleteObjective_recursive()


	def __on_chkConfirmDeleteCascade_toggled(self, widget):
		self.config.Set("confirmDeleteCascade", widget.get_active())
		self.config.Store()


	def __on_deleteCell_toggled(self, cell, path):
		def IsUniform(iterator, objective_id,value):
			while iterator:
				if self.__model.get_value(iterator,0)==objective_id:
					if self.__model.get_value(iterator,2)!=value:
						return False

				elif not IsUniform(self.__model.iter_children(iterator), objective_id,value):
					return False

				iterator = self.__model.iter_next(iterator)

			return True

		def SetIndetermination(iterator, objective_id,value):
			while iterator:
				if self.__model.get_value(iterator,0)==objective_id:
					self.__model.set_value(iterator,3, value)

				else:
					SetIndetermination(self.__model.iter_children(iterator), objective_id,value)

				iterator = self.__model.iter_next(iterator)

		def Preserve(iterator, objective_id):
			# Preserve requeriment
			self.__model.set_value(iterator,2, False)

			# Preserve requeriment requeriments
			iterator = self.__model.iter_children(iterator)
			while iterator:
				Preserve(iterator, self.__model.get_value(iterator,0))
				iterator = self.__model.iter_next(iterator)

			# Set inestability
			SetIndetermination(self.__model.get_iter_root(), objective_id,
								not IsUniform(self.__model.get_iter_root(),
												objective_id,False))

		def Delete(iterator, objective_id):
			# [To-Do] Add recursive code for delete on cascade
			self.__model.set_value(iterator,2, True)

#			# Delete on cascade
#			if self.config.Get('deleteCascade'):
#				iterator = self.__model.iter_children(iterator)
#				while iterator:
#					Delete(iterator, self.__model.get_value(iterator,0))
#					iterator = self.__model.iter_next(iterator)

			# Set inextability
			SetIndetermination(self.__model.get_iter_root(), objective_id,
								not IsUniform(self.__model.get_iter_root(),
												objective_id,True))


		iterator = self.__model.get_iter(path)
		objective_id = self.__model.get_value(iterator,0)

		# Active - Set preserve
		if self.__model.get_value(iterator,2):
			Preserve(iterator, objective_id)

		# Inactive - Set delete
		else:
			Delete(iterator, objective_id)


#	def __on_deleteCell_toggled(self, cell, path):
#		def Preserve(iterator, objective_id):
#
#			# Disable requeriment checkbox
#			self.__model.set_value(iterator,2, False)
#
#			# Preserve childrens
#
#			# Check if all duplicates are uniform
#			def IsUniform(iterator, value):
#				while iterator:
#					if self.__model.get_value(iterator,0)==objective_id:
#						if self.__model.get_value(iterator,2)!=value:
#							return False
#
#					elif not IsUniform(self.__model.iter_children(iterator), value):
#						return False
#
#					iterator = self.__model.iter_next(iterator)
#
#				return True
#
#
#			uniform = IsUniform(self.__model.get_iter_root(), False)
#
#			# Set indetermination
#			def SetIndetermination(iterator, value):
#				while iterator:
#					if self.__model.get_value(iterator,0)==objective_id:
#						self.__model.set_value(iterator,3, value)
#
#					else:
#						SetIndetermination(self.__model.iter_children(iterator), value)
#
#					iterator = self.__model.iter_next(iterator)
#
#
#			SetIndetermination(self.__model.get_iter_root(), not uniform)
#
##			while iterator:
##				if self.__model.get_value(iterator,0)==objective_id:
##
##					if self.__model.get_value(iterator,2):
##						self.__model.set_value(iterator,2, False)
##
##						iter_childs = self.__model.iter_children(iterator)
##						while iter_childs:
##							Preserve(self.__model.get_iter_root(),
##									self.__model.get_value(iter_childs,0))
##							iter_childs = self.__model.iter_next(iter_childs)
##
##				else:
##					Preserve(self.__model.iter_children(iterator), objective_id)
##
##				iterator = self.__model.iter_next(iterator)
#
#
#		def Delete(iterator, objective_id):
#			canBeDeleted = []
#
#			def CanBeDeleted():
#				def Private_CanBeDeleted(iterator):
#					while iterator:
#						if self.__model.get_value(iterator,0)==objective_id:
#							def HasAlternatives():
#								it = self.__model.iter_children(self.__model.iter_parent(iterator))
#								while it:
#									# If it's preserved
#									# and it's diferent of objective to delete,
#									# then it has alternatives
#									if(not self.__model.get_value(it,2)
#									and self.__model.get_value(it,0)!=objective_id):
#										return True
#
#									it = self.__model.iter_next(it)
#
#								return False
#
#							if(not self.__model.get_value(self.__model.iter_parent(iterator),2)
#							and not HasAlternatives()):
#								return False
#
#						elif not Private_CanBeDeleted(self.__model.iter_children(iterator)):
#							return False
#
#						iterator = self.__model.iter_next(iterator)
#
#					return True
#
#				return (objective_id in canBeDeleted
#						or Private_CanBeDeleted(self.__model.get_iter_root()))
#
#
#			while iterator:
#				if self.__model.get_value(iterator,0)==objective_id:
#
#					if(not self.__model.get_value(iterator,2)
#						and CanBeDeleted()):
#						canBeDeleted.append(objective_id)
#						self.__model.set_value(iterator,2, True)
#
#						iter_childs = self.__model.iter_children(iterator)
#						while iter_childs:
#							Delete(self.__model.get_iter_root(),
#									self.__model.get_value(iter_childs,0))
#							iter_childs = self.__model.iter_next(iter_childs)
#
#				else:
#					Delete(self.__model.iter_children(iterator),
#							objective_id)
#
#				iterator = self.__model.iter_next(iterator)
#
#
#		iterator = self.__model.get_iter(path)
#
#		# Active - Set preserve
#		if self.__model.get_value(iterator,2):
#			Preserve(iterator, self.__model.get_value(iterator,0))
##			Preserve(self.__model.get_iter_root(),
##					self.__model.get_value(iterator,0))
#
#		# Inactive - Set delete
#		else:
#			Delete(self.__model.get_iter_root(),
#					self.__model.get_value(iterator,0))

