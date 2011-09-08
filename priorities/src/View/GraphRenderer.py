import glib
import gtk

from datetime import datetime,timedelta


class Requeriment(gtk.Button):
	margin_x = 20

	def __init__(self, name, parent):
		gtk.Button.__init__(self, name)
		self.set_focus_on_click(False)

		self.connect('clicked',parent.AddObjective, name)
		self.connect('enter_notify_event',parent.IncreaseLineWidth, self)
		self.connect('leave_notify_event',parent.IncreaseLineWidth)

		self.prev = None
		self.requeriments = []
		self.__dependents = []

		self.__parent = parent

		self.__x = 0
		self.__y = 0

	def Add_Requeriment(self, requeriment):
		self.requeriments.append(requeriment)
		requeriment.__dependents.append(self)

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

		x_req = Get_Middle(self.requeriments)
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
		if(self.prev
		and x < positions[self.prev][0]+self.prev.allocation.width):
			x = positions[self.prev][0]+self.prev.allocation.width

			# Increase distance between "groups"
			if(self.prev.requeriments != self.requeriments
			or self.prev.__dependents != self.__dependents):
				x += 20

		# Ensure all requeriments are showed in layout
		if  x < 0:
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
	def __init__(self, name, parent, objective, color):
		Requeriment.__init__(self, name, parent)

#		self.connect('button-press-event',parent.__on_objective_clicked)

		# Tooltip
		tooltip = "Cantidad: "+str(objective['quantity'])

		expiration = objective["expiration"]
		if(expiration):
			tooltip += "\nExpiracion: "+expiration

		dependents = parent.controller.Dependents(name)
		if(dependents):
			tooltip += "\nDependents: "+str(len(dependents))

		self.set_tooltip_text(tooltip)

		self.__SetExpirationColor(objective, parent.controller,color)


	def __SetExpirationColor(self, objective, controller,color):
		expiration = objective["expiration"]

		# Expired and not satisfacted - Show warning
		if(expiration
		and not controller.IsSatisfaced(self.get_label())):

			# Expired - Set inverted color
			if datetime.strptime(expiration,"%Y-%m-%d %H:%M:%S") < datetime.now():
				self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
				self.child.modify_fg(gtk.STATE_NORMAL, color)
				return

			# Next to expire - Set color animation
			elif(datetime.strptime(expiration,"%Y-%m-%d %H:%M:%S")
			   < datetime.now()+timedelta(self.config.Get('expirationWarning'))):

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