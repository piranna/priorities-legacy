import gtk


class DeleteCascade:
	def __init__(self):
		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("DeleteCascade")
#		self.window.connect('response',self.__on_Preferences_response)

		treeview = builder.get_object("treeview")

