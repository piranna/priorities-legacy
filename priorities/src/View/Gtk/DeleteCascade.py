from View.Gtk import _,Gtk


class DeleteCascade(Gtk):
	def __init__(self, objective):
		Gtk.__init__(self, "DeleteCascade")

		# Model
		treeview = self.builder.get_object("treeview")
		self.__model = treeview.get_model()

		self.__tree = {}

		# Fill model
		def Append(tree, parent=None):
#			self.__tree.get(objective, []).append(path)
			for objective in tree.keys():
				Append(tree[objective],
						self.__model.append(parent,
									(objective, objective, True,False)))

		Append(self.controller.Get_DeleteObjective_Tree(objective),
				self.__model.append(None,
							(objective, objective, True,False)))

		# If confirmDeleteCascade,
		# show window
		confirmDeleteCascade = self.config.Get('confirmDeleteCascade')
		if confirmDeleteCascade:
			self.builder.get_object("chkConfirmDeleteCascade1").set_active(confirmDeleteCascade)

			treeview.expand_all()


	def DeleteObjective_recursive(self, iterator = None):
		if not iterator:
			iterator = self.__model.get_iter_root()

		deleted = 0

		# If objective is marked,
		# delete it
		if self.__model.get_value(iterator,2):
			if not self.__model.get_value(iterator,3):
				self.controller.DeleteObjective(self.__model.get_value(iterator,0),
												self.config.Get('removeOrphanRequirements'))

			deleted += 1

		# Delete objective marqued requirements, if any
		iterator = self.__model.iter_children(iterator)
		while iterator:
			deleted += self.DeleteObjective_recursive(iterator)
			iterator = self.__model.iter_next(iterator)

		return deleted


	def on_DeleteCascade_response(self, widget, response):
		if response>0:
			# [To-Do] Poner response a 0 si no se elimina ningun objetivo
			deleted = self.DeleteObjective_recursive()


	def on_chkConfirmDeleteCascade_toggled(self, widget):
		self.config.Set("confirmDeleteCascade", widget.get_active())
		self.config.Store()


	def on_deleteCell_toggled(self, cell, path):
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
			# Preserve requirement
			self.__model.set_value(iterator,2, False)

			# Preserve requirement requirements
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

			# Set inestability
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