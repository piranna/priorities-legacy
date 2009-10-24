import View

import gtk


glade_file = "View_Gtk.glade"


class View_Gtk(View.View):
	builder = None

	def __init__(self):
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.add_from_file(glade_file)

