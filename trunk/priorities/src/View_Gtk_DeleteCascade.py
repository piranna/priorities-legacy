import View_Gtk


class DeleteCascade(View_Gtk.View):
	def __init__(self, objective_id):
		View_Gtk.View.__init__(self)

		# Model
		treeview = self.builder.get_object("treeview")
		model = treeview.get_model()

		# Fill model
		def Append(parent, tree):
			print "Append",tree
			for objective_id in tree.keys():
				Append(model.append(parent,
									(objective_id, self.controller.GetName(objective_id), True,False)),
						tree[objective_id])

		Append(model.append(None,
							(objective_id, self.controller.GetName(objective_id), True,False)),
				self.controller.Get_DeleteObjective_Tree(objective_id))

		# If confirmDeleteCascade,
		# show window
		if config['confirmDeleteCascade']:
			self.window = self.builder.get_object("DeleteCascade")
			self.window.connect('response',self.__on_DeleteCascade_response, model)

			deleteCell = self.builder.get_object("deleteCell")
			deleteCell.connect('toggled', self.__on_deleteCell_toggled, model)

			chkConfirmDeleteCascade = self.builder.get_object("chkConfirmDeleteCascade")
#			chkConfirmDeleteCascade.connect('toggled', self.__on_chkConfirmDeleteCascade_toggled)
#			chkConfirmDeleteCascade.set_active(self.config['confirmDeleteCascade'])

			treeview.expand_all()

		# If not,
		# delete requeriments directly
		else:
			self.__DeleteObjective_recursive(model, model.get_iter_root())


	def __DeleteObjective_recursive(model, iterator):
		if model.get_value(iterator,2):
			self.controller.DeleteObjective(model.get_value(iterator,0))

		iterator = model.iter_children(iterator)
		while iterator:
			DeleteObjective_recursive(model, iterator)
			iterator = model.iter_next(iterator)


	def __on_DeleteCascade_response(self, widget, response,model):
		if response>0:
			DeleteObjective_recursive(model, model.get_iter_root())


#	def __on_chkConfirmDeleteCascade_toggled(self, widget):
#		self.config["confirmDeleteCascade"] = widget.get_active()


	def __on_deleteCell_toggled(self, cell, path,model):
		def SetChildrens(iterator,column, value):
			iterator = model.iter_children(iterator)
			if(iterator
			and value != model.get_value(iterator,2)):
				while iterator:
					model.set_value(iterator,2, value)
					SetChildrens(iterator,column, value)
					iterator = model.iter_next(iterator)

#		def SetAncestorsInconsistency(iterator,column, value):
#			iterator = model.iter_parent(iterator)
#			while iterator:
##				model.set_value(iterator,2, value)
#				SetAncestors(iterator,column, value)
#				iterator = model.iter_next(iterator)


		def Preserve(iterator, objective_id):
			while iterator:
				if model.get_value(iterator,0)==objective_id:

					if model.get_value(iterator,2):
						model.set_value(iterator,2, False)

						iter_childs = model.iter_children(iterator)
						while iter_childs:
							Preserve(model.get_iter_root(), model.get_value(iter_childs,0))
							iter_childs = model.iter_next(iter_childs)

				else:
					Preserve(model.iter_children(iterator), objective_id)

				iterator = model.iter_next(iterator)


		def Delete(iterator, objective_id):
			canBeDeleted = []

			def CanBeDeleted():
				def Private_CanBeDeleted(iterator):
					while iterator:
						if model.get_value(iterator,0)==objective_id:

							def HasAlternatives():
								it = model.iter_children(model.iter_parent(iterator))
								preserved = 0
								while it:
									if not model.get_value(it,2):
										preserved += 1
										if preserved > 1:
											return True
									it = model.iter_next(it)
								return False


							if(not model.get_value(model.iter_parent(iterator),2)
							and not HasAlternatives()):
								return False

						elif not Private_CanBeDeleted(model.iter_children(iterator)):
							return False

						iterator = model.iter_next(iterator)

					return True

				return (objective_id in canBeDeleted
						or Private_CanBeDeleted(model.get_iter_root()))


			while iterator:
				if model.get_value(iterator,0)==objective_id:

					if(not model.get_value(iterator,2)
						and CanBeDeleted()):
						canBeDeleted.append(objective_id)
						model.set_value(iterator,2, True)

						iter_childs = model.iter_children(iterator)
						while iter_childs:
							Delete(model.get_iter_root(), model.get_value(iter_childs,0))
							iter_childs = model.iter_next(iter_childs)

				else:
					Delete(model.iter_children(iterator), objective_id)

				iterator = model.iter_next(iterator)


		iterator = model.get_iter(path)

		# Active - Set preserve
		if model.get_value(iterator,2):
			Preserve(model.get_iter_root(), model.get_value(iterator,0))
#			SetChildrens(iterator,2, False)
#			SetAncestorsInconsistency(iterator,2, False)

		# Inactive - Set delete
		else:
			Delete(model.get_iter_root(), model.get_value(iterator,0))
#			model.set_value(iterator,2, True)
#			SetChildrens(iterator,2, True)
#			SetAncestorsInconsistency(iterator,2, True)

