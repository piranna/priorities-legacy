import gtk


class DeleteCascade:
	def __init__(self, controller,objective_id):
		self.__controller = controller

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("DeleteCascade")
#		self.window.connect('response',self.__on_Preferences_response)

		treeview = builder.get_object("treeview")
		model = treeview.get_model()

		deleteCell = builder.get_object("deleteCell")
		deleteCell.connect('toggled', self.__on_deleteCell_toggled, model)

		# Fill model
		def Append(parent, tree = {}):
			for objective_id in tree.keys():
				Append(model.append(parent,
									(objective_id,True)),
						tree[objective_id])

		Append(model.append(None,
							(objective_id,True)),
				self.__controller.Get_DeleteObjective_Tree(objective_id))

		treeview.expand_all()


	def __on_deleteCell_toggled(self, cell, path,model):
		# [To-Do] Modify recursively
		# [To-Do] Add inconsistent
		model[path][1] = not model[path][1]

