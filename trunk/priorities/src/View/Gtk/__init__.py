from View import _,APP,View

import gtk


glade_file = "View/Gtk/Gtk.glade"


class Gtk(View):
	builder = None

	def __init__(self, id):
		View.__init__(self)

		# Create builder
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.set_translation_domain(APP)
			self.builder.add_from_file(glade_file)

		self.window = self.builder.get_object(id)

		# Connect signals
		import warnings
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			self.builder.connect_signals(self)