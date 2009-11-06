import gtk


class Requeriment(gtk.Button):
	def __init__(self, label,objective_id, layout):
		gtk.Button.__init__(self, label)
		self.set_focus_on_click(False)
		self.connect('clicked',layout.AddObjective, objective_id)
		self.connect('enter_notify_event',layout.__IncreaseLineWidth, objective_id)
		self.connect('leave_notify_event',layout.__IncreaseLineWidth)


class Objective(Requeriment):
	def __init__(self, label,objective_id, layout):
		Requeriment.__init__(self, label,objective_id, layout)

		self.connect('button-press-event',layout.__on_objective_clicked)

		# Tooltip
		self.set_tooltip_text("Cantidad: "+str(objective['objective_quantity']))
		if(objective["expiration"]):
			self.set_tooltip_text(button.get_tooltip_text()+"\nExpiracion: "+objective['expiration'])
		dependents = layout.controller.DirectDependents(objective['objective_id'])
		if(dependents):
			self.set_tooltip_text(self.get_tooltip_text()+"\nDependents: "+str(len(dependents)))

		self.__SetExpirationColor()


	def __SetExpirationColor():
		# Expired and not satisfacted - Show warning
		if(objective["expiration"]
		and not self.controller.IsSatisfacted(objective['objective_id'])):

			# Expired - Set inverted color
			if datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
				button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
				button.child.modify_fg(gtk.STATE_NORMAL, color)
				return

			# Next to expire - Set color animation
			elif(datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S")
			< datetime.datetime.now()+datetime.timedelta(self.config.Get('expirationWarning'))):

				def button_expires_inverted(button, color):
					button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
					button.child.modify_fg(gtk.STATE_NORMAL, color)

					glib.timeout_add_seconds(1, button_expires_normal, button, color)
					return False

				def button_expires_normal(button, color):
					self.modify_bg(gtk.STATE_NORMAL, color)
					self.child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))

					glib.timeout_add_seconds(1, button_expires_inverted, self, color)
					return False

				button_expires_normal(self, color)
				return

		# Non expired - Set background color
		self.modify_bg(gtk.STATE_NORMAL, color)