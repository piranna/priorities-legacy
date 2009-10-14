import gtk


glade_file = "View_Gtk.glade"


class View:
	controller = None

	builder = None
	config = None

	def __init__(self):
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.add_from_file(glade_file)

