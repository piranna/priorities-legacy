import glib
import gtk
import datetime


class Requeriment(gtk.Button):
	margin_x = 20

	def __init__(self, name, parent):
		gtk.Button.__init__(self, name)
		self.set_focus_on_click(False)

		self.connect('clicked',parent.AddObjective, name)
		self.connect('enter_notify_event',parent.IncreaseLineWidth, self)
		self.connect('leave_notify_event',parent.IncreaseLineWidth)

		self.__prev = None
		self.__requeriments = []
		self.__dependents = []

		self.__parent = parent

		self.__x = 0
		self.__y = 0

	def Set_Prev(self, prev):
		self.__prev = prev

	def Add_Requeriment(self, requeriment):
		self.__requeriments.append(requeriment)
		requeriment.__dependents.append(self)

	def Get_Requeriments(self):
		return self.__requeriments

	def Adjust(self, positions, y):
		def Get_Middle(array):
			x_min = 0
			x_max = 0
			for button in array:
				if(x_min==0
				or x_min > positions[button][0]):
					x_min = positions[button][0]
				if(x_max==0
				or x_max < positions[button][0] + button.allocation.width):
					x_max = positions[button][0] + button.allocation.width
			return (x_min + x_max)/2

		x = 0
		div = 0

		x_req = Get_Middle(self.__requeriments)
		if x_req:
			x += x_req
			div += 1

#		x_dep = Get_Middle(self.__dependents)
#		if x_dep:
#			x += x_dep
#			div += 1

		if div:
			x = x/div - self.allocation.width/2

		# Prevent overlapping with previous requeriment at the same level
		if(self.__prev
		and x < positions[self.__prev][0]+self.__prev.allocation.width):
			x = positions[self.__prev][0]+self.__prev.allocation.width

			# Increase distance between "groups"
			if(self.__prev.__requeriments != self.__requeriments
			or self.__prev.__dependents != self.__dependents):
				x += 20

		# Ensure all requeriments are showed in layout
		if x < 0:
			x = 0

		# Update requeriment position
		if(self.__x != x
		or self.__y != y):
			self.__x = x
			self.__y = y

			self.__parent.layout.move(self, self.__x,self.__y)

			return True

		return False

	def X(self):
		return self.__x

	def Y(self):
		return self.__y


#import gobject
#gobject.type_register(Requeriment)


class Objective(Requeriment):
	def __init__(self, objective, parent,
				controller, color):
		Requeriment.__init__(self, objective['name'], parent)

#		self.connect('button-press-event',parent.__on_objective_clicked)

		# Tooltip
		self.set_tooltip_text("Cantidad: "+str(objective['objective_quantity']))
		if(objective["expiration"]):
			self.set_tooltip_text(button.get_tooltip_text()+"\nExpiracion: "+objective['expiration'])
		dependents = parent.controller.Dependents(objective['name'])
		if(dependents):
			self.set_tooltip_text(self.get_tooltip_text()+"\nDependents: "+str(len(dependents)))

		self.__SetExpirationColor(objective, controller,color)


	def __SetExpirationColor(self, objective, controller,color):
		# Expired and not satisfacted - Show warning
		if(objective["expiration"]
		and not controller.IsSatisfaced(objective['objective_id'])):

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

