import View
_ = View._

import gtk


glade_file = "View_Gtk.glade"


class View_Gtk(View.View):
	builder = None

	def __init__(self, id):
#		View.View.__init__(self)

		# Create builder
		if not self.builder:
			self.builder = gtk.Builder()
			self.builder.set_translation_domain(View.APP)
			self.builder.add_from_file(glade_file)

		self.window = self.builder.get_object(id)

		# Connect signals
		import warnings
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			self.builder.connect_signals(self)

