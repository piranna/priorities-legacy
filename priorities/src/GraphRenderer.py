import glib
import gtk
import datetime


class Requeriment(gtk.Button):
	margin_x = 20

	def __init__(self, name,objective_id, parent):
		gtk.Button.__init__(self, name)
		self.set_focus_on_click(False)

		self.__layout = parent.layout
		self.__x = 0
		self.__y = 0

		self.connect('clicked',parent.AddObjective, objective_id)
		self.connect('enter_notify_event',parent.IncreaseLineWidth, self)
		self.connect('leave_notify_event',parent.IncreaseLineWidth)

		self.__requeriments = []
		self.__dependents = []
		self.__next = None
#		self.__prev = None

	def Set_Next(self, next):
		self.__next = next

#	def Set_Prev(self, prev):
#		self.__prev = prev

	def __X(self, x=None):
		if(x
		and x!=self.__x):
			print self.get_label(),self.__x,"(",x,self.allocation.width,")",x+self.allocation.width
			self.__x = x
			self.__layout.move(self, self.__x,self.__y)
		return self.__x

	def X(self):
		return self.__x

	def Y(self, y=None):
		if(y
		and y!=self.__y):
			self.__y = y
			self.__layout.move(self, self.__x,self.__y)
		return self.__y

	def Add_Dependency(self, dependency):
		self.__requeriments.append(dependency)
		dependency.__Add_Dependent(self)

	def __Add_Dependent(self, dependent):
		self.__dependents.append(dependent)

	def Get_Requeriments(self):
		return self.__requeriments


	def Adjust_x(self, x):
		def Get_Expansion(buttons):
			min_x = None
			max_x = None

			for button in buttons:
				if(min_x == None
				or button.__x < min_x):
					min_x = button.__x

				if(max_x == None
				or button.__x+button.allocation.width > max_x):
					max_x = button.__x+button.allocation.width

			return min_x,max_x

		def Update_RowWidth(row_width, value):
			if row_width < value:
				row_width = value
			return row_width


#		if self.__prev:
#			row_width = self.__prev.__x + self.__prev.allocation.width + self.margin_x
#			if x < row_width:
#				x = row_width

		row_width = 0

		if len(self.__requeriments) == 1:
			if len(self.__requeriments[0].__dependents) == 1:
				x = (2*self.__requeriments[0].__x+self.__requeriments[0].allocation.width-self.allocation.width)/2
			else:	# > 1
				self.__X(x)

				min_x,max_x = Get_Expansion(self.__requeriments[0].__dependents)

				self.__requeriments[0].__X((min_x+max_x-self.__requeriments[0].allocation.width)/2)

				print "max_x",max_x
				row_width = max_x

		elif len(self.__requeriments) > 1:
			min_x,max_x = Get_Expansion(self.__requeriments)

			x = ((min_x+max_x)-self.allocation.width)/2

		self.__X(x)
		row_width = Update_RowWidth(row_width, x)

		#
		# Recursives

		# Dependents
		if self.__dependents:
			row_width = Update_RowWidth(row_width, self.__dependents[0].Adjust_x(self.__x))

		# Next
		row_width = Update_RowWidth(row_width, self.__x + self.allocation.width)
		if self.__next:
			row_width = Update_RowWidth(row_width, self.__next.Adjust_x(row_width + self.margin_x))

		# Return value of the current row width
		return row_width

#import gobject
#gobject.type_register(Requeriment)


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

