import gtk


class DeleteCascade:
	def __init__(self, controller,objective_id):
		self.__controller = controller

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("DeleteCascade")

		treeview = builder.get_object("treeview")
		model = treeview.get_model()

		self.window.connect('response',self.__on_DeleteCascade_response, model)

		deleteCell = builder.get_object("deleteCell")
		deleteCell.connect('toggled', self.__on_deleteCell_toggled, model)

		# Fill model
		def Append(parent, tree):
#			print "Append",tree
			for objective_id in tree.keys():
				Append(model.append(parent,
									(objective_id, controller.GetName(objective_id), True,False)),
						tree[objective_id])

		Append(model.append(None,
							(objective_id, controller.GetName(objective_id), True,False)),
				controller.Get_DeleteObjective_Tree(objective_id))

		treeview.expand_all()


	def __on_DeleteCascade_response(self, widget, response,model):
		if response>0:
			def DeleteObjective_recursive(iterator):
				if model.get_value(iterator,2):
					self.__controller.DeleteObjective(model.get_value(iterator,0))

				iterator = model.iter_children(iterator)
				while iterator:
					DeleteObjective_recursive(iterator)
					iterator = model.iter_next(iterator)

			DeleteObjective_recursive(model.get_iter_root())


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

		iterator = model.get_iter(path)
		if model.get_value(iterator,2):
			model.set_value(iterator,2, False)
			SetChildrens(iterator,2, False)
#			SetAncestorsInconsistency(iterator,2, False)
		else:
			model.set_value(iterator,2, True)
			SetChildrens(iterator,2, True)
#			SetAncestorsInconsistency(iterator,2, True)

