import gtk


class About:
	def __init__(self):
		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("About")
