import View_Gtk


class About(View_Gtk.View):
	def __init__(self):
		View_Gtk.View.__init__(self)

		self.window = self.builder.get_object("About")

