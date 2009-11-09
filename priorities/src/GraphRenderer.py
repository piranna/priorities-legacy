import glib
import gtk
import datetime


class Requeriment(gtk.Button):
	def __init__(self, name,objective_id, parent):
		gtk.Button.__init__(self, name)
		self.set_focus_on_click(False)
		self.connect('clicked',parent.AddObjective, objective_id)
#		self.connect('enter_notify_event',parent.__IncreaseLineWidth, objective['objective_id'])
#		self.connect('leave_notify_event',parent.__IncreaseLineWidth)


class Objective(Requeriment):
	def __init__(self, objective,parent,
				controller, color):
		Requeriment.__init__(self, objective['name'],objective['objective_id'], parent)

#		self.connect('button-press-event',parent.__on_objective_clicked)

		# Tooltip
		self.set_tooltip_text("Cantidad: "+str(objective['objective_quantity']))
		if(objective["expiration"]):
			self.set_tooltip_text(button.get_tooltip_text()+"\nExpiracion: "+objective['expiration'])
		dependents = parent.controller.DirectDependents(objective['objective_id'])
		if(dependents):
			self.set_tooltip_text(self.get_tooltip_text()+"\nDependents: "+str(len(dependents)))

		self.__SetExpirationColor(objective, controller,color)


	def __SetExpirationColor(self, objective, controller,color):
		# Expired and not satisfacted - Show warning
		if(objective["expiration"]
		and not controller.IsSatisfacted(objective['objective_id'])):

			# Expired - Set inverted color
			if datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
				self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
				self.child.modify_fg(gtk.STATE_NORMAL, color)
				return

			# Next to expire - Set color animation
			elif(datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S")
			< datetime.datetime.now()+datetime.timedelta(self.config.Get('expirationWarning'))):

				def expires_inverted(color):
					self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
					self.child.modify_fg(gtk.STATE_NORMAL, color)

					glib.timeout_add_seconds(1, expires_normal, color)
					return False

				def expires_normal(color):
					self.modify_bg(gtk.STATE_NORMAL, color)
					self.child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))

					glib.timeout_add_seconds(1, expires_inverted, color)
					return False

				expires_normal(color)
				return

		# Non expired - Set background color
		self.modify_bg(gtk.STATE_NORMAL, color)

