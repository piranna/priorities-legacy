import gtk


class View:
	controller = None
	builder = None

	def __init__(self):
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.add_from_file("View_Gtk.glade")