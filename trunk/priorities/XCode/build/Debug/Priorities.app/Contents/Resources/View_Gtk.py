import gtk
import random
import math

from View_Gtk_About import *
from View_Gtk_AddObjective import *
from View_Gtk_Preferences import *


class View:
	x_step = 100
	y_step = 50


	def __init__(self, controller):
		self.__controller = controller

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("Main")
		self.window.connect('destroy',self.__on_Main_destroy)

		self.layout = builder.get_object("layout")
		self.layout.connect('expose-event',self.__DrawRequerimentsArrows)

		scrolledwindow = builder.get_object("scrolledwindow")
		scrolledwindow.set_hadjustment(self.layout.get_hadjustment())
		scrolledwindow.set_vadjustment(self.layout.get_vadjustment())

		btnAddObjective = builder.get_object("btnAddObjective")
		btnAddObjective.connect('clicked',self.__AddObjective)

		btnPreferences = builder.get_object("btnPreferences")
		btnPreferences.connect('clicked',self.__Preferences)

		btnAbout = builder.get_object("btnAbout")
		btnAbout.connect('clicked',self.__About)

#		btnPreferences = builder.get_object("btnPreferences")
#		btnPreferences.connect('clicked',self.__Preferences)

		self.__CreateTree()

		self.window.show()
		gtk.main()


	def __DrawRequerimentsArrows(self,widget,event):
		def DrawHead(arrow):
			def ArrowPoint(arrow, angle, lenght):
				angle = math.radians(angle)

				cotan = math.atan((arrow[0][0]-arrow[1][0])/(arrow[0][1]-arrow[1][1]))+angle

				return (arrow[1][0]+math.sin(cotan)*lenght, arrow[1][1]+math.cos(cotan)*lenght)

			arrowPoint = ArrowPoint(arrow, 15, 15)
			self.layout.bin_window.draw_line(self.gc, int(arrow[1][0]),int(arrow[1][1]),
																	int(arrowPoint[0]),int(arrowPoint[1]))

			arrowPoint = ArrowPoint(arrow, -15, 15)
			self.layout.bin_window.draw_line(self.gc, int(arrow[1][0]),int(arrow[1][1]),
																	int(arrowPoint[0]),int(arrowPoint[1]))


		self.gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]

#		for x in range(1,5):
#			self.layout.bin_window.draw_line(self.gc, x*self.x_step,0,
#																	x*self.x_step,500)
#			self.layout.bin_window.draw_line(self.gc, 0,x*self.x_step,
#																	500,x*self.x_step)

		for arrow in self.__req_arrows:
			self.layout.bin_window.draw_line(self.gc, int(arrow[0][0]),int(arrow[0][1]),
																	int(arrow[1][0]),int(arrow[1][1]))

			# Arrow head
			DrawHead(arrow)


	def __CreateTree(self):
		def GetCoordinates(objective):
			for obj in obj_coords:
				if obj[0] == objective:
					return obj[1]
			return (0,0)
#			return None


		def CreateButton(label):
			button = gtk.Button(label)
			button.set_focus_on_click(False)
			button.show()
			return button


		self.__CleanTree()

		objectives = []
		obj_coords = []

		self.layout.set_size(self.x_step/2,self.y_step/2)

		y = self.y_step/2.0
		for level in self.__controller.ShowTree():
			x = random.randint(self.x_step/2.0,self.x_step)
			req_coords = None
			level_requeriments = []

			for objective in level:
				def UpdateLayoutSize(width,height):
					layout_size_x = self.layout.get_size()[0]
					layout_size_y = self.layout.get_size()[1]
					if layout_size_x < width:
						layout_size_x = width
					if layout_size_y < height:
						layout_size_y = height
					self.layout.set_size(int(layout_size_x),
												int(layout_size_y))

				# Requeriments
				if objective['requeriment']:

					# [To-Do] Have several requeriment_button in a same level

					# Requeriments with alternatives
					if objective['priority']:
						# If requeriment is not registered before,
						# create it
						if objective['requeriment'] not in level_requeriments:

							# Create requeriment button
							requeriment_button = CreateButton(self.__controller.GetName(objective['alternative']))
							#requeriment_button.set_relief(gtk.RELIEF_NONE)
							requeriment_button.connect('clicked',self.__AddObjective)

							# Put requeriment button
							req_coords = (x,y)
							self.layout.put(requeriment_button, int(req_coords[0]),int(req_coords[1]))

							UpdateLayoutSize(x+self.x_step,y+self.y_step)

							# Increase level requeriments
							level_requeriments.append(objective['requeriment'])
							#x = 0
							x = random.randint(0, self.x_step)
							#x += self.x_step + random.randint(0, self.x_step)
							y += self.y_step

						# Else update it's label
						else:
							requeriment_button.set_label(requeriment_button.get_label()+"\n"
																+self.__controller.GetName(objective['alternative']))

						# Store the requeriment arrow coordinates
						self.__req_arrows.append((req_coords, GetCoordinates(objective['alternative'])))

					# Requeriment without alternatives
					else:
						req_coords = GetCoordinates(objective['alternative'])

				# Objective
				if objective['objective_id'] not in objectives:
					def GetColor(objective):
#						# Red
#						if actual < required:
							return gtk.gdk.Color(65535,32767,32767)

#						# Yellow
#						elif actual>=required:
#							return gtk.gdk.Color(65535,65535,32767)
#
#						# Green
#						elif not required or actual>=required:
#							return gtk.gdk.Color(32767,65535,32767)
#
#						# Blue
#						#return gtk.gdk.Color(32767,32767,65535)


					# Create objective button
					button = CreateButton(objective['name'])
					button.modify_bg(gtk.STATE_NORMAL, GetColor(objective['objective_id']))
					button.connect('clicked',self.__AddObjective)

					# Put objective button
					self.layout.put(button, int(x),int(y))
					obj_coords.append((objective['objective_id'], (x,y)))

					UpdateLayoutSize(x+self.x_step,y+self.y_step)

					# Register objective to prevent be printed twice
					objectives.append(objective['objective_id'])

					x += self.x_step + random.randint(0, self.x_step/2)

				# If objective has requeriments,
				# store the requeriment arrow coordinates
				if req_coords:
					self.__req_arrows.append((GetCoordinates(objective['objective_id']), req_coords))

			y += self.y_step

		layout_size = self.layout.get_size()
		self.layout.set_size(layout_size[0] + self.x_step/2,
									layout_size[1] + self.y_step/2)



	def __CleanTree(self):
		# Clean arrows array
		self.__req_arrows = []

		# Delete old buttons
		for children in self.layout.get_children():
			self.layout.remove(children)

		# Re-draw surface of the layout
		self.layout.queue_draw()


	def __About(self, widget):
		about = About()

		about.window.set_transient_for(self.window)
		about.window.run()
		about.window.destroy()


	def __AddObjective(self, widget):
		addObjective = AddObjective(self.__controller, self.__controller.GetId(widget.get_label()))

		addObjective.window.set_transient_for(self.window)
		response = addObjective.window.run()
		addObjective.window.destroy()

		print "response =",response

		# Redraw the requeriments tree
		if response > 0:
			self.__CreateTree()


	def __Preferences(self, widget):
		preferences = Preferences(self.__controller)

		preferences.window.set_transient_for(self.window)
		preferences.window.run()
		preferences.window.destroy()


	def __on_Main_destroy(self, widget, data=None):
		gtk.main_quit()
