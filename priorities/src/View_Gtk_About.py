import View_Gtk


class About(View_Gtk.View_Gtk):
	def __init__(self):
		View_Gtk.View_Gtk.__init__(self)

		self.window = self.builder.get_object("About")