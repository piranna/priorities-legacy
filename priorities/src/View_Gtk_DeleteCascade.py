import gtk


class DeleteCascade:
	def __init__(self, controller,objective_id):
		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("DeleteCascade")
#		self.window.connect('response',self.__on_Preferences_response)

		treeview = builder.get_object("treeview")
		model = treeview.get_model()

		deleteCell = builder.get_object("deleteCell")
		deleteCell.connect('toggled', self.__on_deleteCell_toggled, model)

		# Fill model
		def Append(parent, tree):
			for objective_id in tree.keys():
				Append(model.append(parent,
									(objective_id, controller.GetName(objective_id), True,False)),
						tree[objective_id])

		Append(model.append(None,
							(objective_id, controller.GetName(objective_id), True,False)),
				controller.Get_DeleteObjective_Tree(objective_id))

		treeview.expand_all()


	def __on_deleteCell_toggled(self, cell, path,model):
		def SetChildrens(iterator,column, value):
			iterator = model.iter_children(iterator)
			while iterator:
				model.set_value(iterator,2, value)
				SetChildrens(iterator,column, value)
				iterator = model.iter_next(iterator)

		def SetAncestorsInconsistency(iterator,column, value):
			iterator = model.iter_parent(iterator)
			while iterator:
#				model.set_value(iterator,2, value)
				SetAncestors(iterator,column, value)
				iterator = model.iter_next(iterator)

		iterator = model.get_iter(path)
		if model.get_value(iterator,2):
			model.set_value(iterator,2, False)
			SetChildrens(iterator,2, False)
#			SetAncestorsInconsistency(iterator,2, False)
		else:
			model.set_value(iterator,2, True)
			SetChildrens(iterator,2, True)
#			SetAncestorsInconsistency(iterator,2, True)

