import gtk

import Config


glade_file = "View_Gtk.glade"
config_path = "~/.priorities"


class View:
	controller = None

	builder = None
	config = None

	def __init__(self):
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.add_from_file(glade_file)

		if not self.config:
			self.config = Config.Config(config_path)