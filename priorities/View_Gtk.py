import glib
import gtk
import random
import math
import datetime

from View_Gtk_About import *
from View_Gtk_AddObjective import *
from View_Gtk_Preferences import *

import preferences


class View:
	x_step = 100
	y_step = 50


	def __init__(self, controller, database,useDefaultDB):
		self.__controller = controller
		self.preferences = preferences.Load()

		if not (database and useDefaultDB):
			self.__AskDB(database)

		builder = gtk.Builder()
		builder.add_from_file("View_Gtk.glade")

		self.window = builder.get_object("Main")
		self.window.connect('destroy',self.__on_Main_destroy)

		self.layout = builder.get_object("layout")
		self.layout.connect('expose-event',self.__DrawRequerimentsArrows)

		btnAddObjective = builder.get_object("btnAddObjective")
		btnAddObjective.connect('clicked',self.__AddObjective)

		btnPreferences = builder.get_object("btnPreferences")
		btnPreferences.connect('clicked',self.__Preferences)

		btnAbout = builder.get_object("btnAbout")
		btnAbout.connect('clicked',self.__About)

		self.__CreateTree()

		self.window.show()
		gtk.main()


	def __AskDB(self, database):
		dialog = gtk.FileChooserDialog("Seleccione la base de datos a usar",
												None,
												gtk.FILE_CHOOSER_ACTION_OPEN,
												(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
												gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_filename(database)

#		dialogFilter = gtk.FileFilter()
#		dialogFilter.set_name("All files")
#		dialogFilter.add_pattern("*")
#		dialog.add_filter(dialogFilter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			print dialog.get_filename(), 'selected'
			self.__controller.Connect(dialog.get_filename())

		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, no files selected'
			import sys
			sys.exit(0)

		dialog.destroy()


	def __DrawRequerimentsArrows(self,widget,event):

		# Graphic Context
		gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]


		def DrawHead(arrow):
			def ArrowPoint(arrow, angle, lenght):
				angle = math.radians(angle)

				print arrow,angle,lenght
				cotan = math.atan((arrow[0][0]-arrow[1][0])/(arrow[0][1]-arrow[1][1]))+angle

				return (arrow[1][0]+math.sin(cotan)*lenght, arrow[1][1]+math.cos(cotan)*lenght)

			arrowPoint = ArrowPoint(arrow, 15, 15)
			self.layout.bin_window.draw_line(gc, int(arrow[1][0]),int(arrow[1][1]),
																	int(arrowPoint[0]),int(arrowPoint[1]))

			arrowPoint = ArrowPoint(arrow, -15, 15)
			self.layout.bin_window.draw_line(gc, int(arrow[1][0]),int(arrow[1][1]),
																	int(arrowPoint[0]),int(arrowPoint[1]))


		# Background sharp
		if(self.preferences['showSharp']):
			layout_size = self.layout.get_size()
			for x in range(1,layout_size[0]/self.x_step):
				self.layout.bin_window.draw_line(gc, x*self.x_step,0,
													x*self.x_step,layout_size[1])
			for y in range(1,layout_size[1]/self.y_step):
				self.layout.bin_window.draw_line(gc, 0,y*self.y_step,
													layout_size[0],y*self.y_step)

#			self.layout.bin_window.draw_line(gc, 0,0,
#												x*self.x_step,layout_size[1])
#			self.layout.bin_window.draw_line(gc, 0,0,
#												layout_size[0],y*self.y_step)
			self.layout.bin_window.draw_line(gc, layout_size[0],0,
												layout_size[0],layout_size[1])
			self.layout.bin_window.draw_line(gc, 0,layout_size[1],
												layout_size[0],layout_size[1])

		# Arrows
		for arrow in self.__req_arrows:
#			print "\t",arrow
			# Arrow line
			self.layout.bin_window.draw_line(gc, int(arrow[0][0]),int(arrow[0][1]),
												int(arrow[1][0]),int(arrow[1][1]))
			# Arrow head
#			DrawHead(arrow)


	def __CreateTree(self):
		self.__CleanTree()

		objectives = []
		req_coords = {}
		obj_coords = {}

		def GetCoordinates(objective, requeriment=None):
			if(requeriment):
				req = req_coords.get(objective, None)
				if req:
					return req.get(requeriment, None)
			else:
				return obj_coords.get(objective, None)

			return None

		self.layout.set_size(self.x_step/2,self.y_step/2)

		y = self.y_step/2.0

		# Niveles
		for level in self.__controller.ShowTree():
			def UpdateLayoutSize(width,height):
				layout_size_x = self.layout.get_size()[0]
				layout_size_y = self.layout.get_size()[1]
				if layout_size_x < width:
					layout_size_x = width
				if layout_size_y < height:
					layout_size_y = height
				self.layout.set_size(int(layout_size_x),
											int(layout_size_y))

			def CreateButton(label):
				button = gtk.Button(label)
				button.set_focus_on_click(False)
				button.show()
				return button

			x = random.randint(self.x_step/2.0,self.x_step)
			coords = None
			level_requeriments = {}

			# Requeriments
			for objective in level:
				if objective['requeriment']:
					# Requeriments with alternatives
					if objective['priority']:
						# If requeriment is registered,
						# add alternative
						if(level_requeriments.has_key(objective['objective_id'])
						and objective['requeriment'] in level_requeriments[objective['objective_id']]):
							requeriment_button.set_label(requeriment_button.get_label()+"\n"
														+self.__controller.GetName(objective['alternative']))

						# else create a new one
						else:
							# Create requeriment button
							requeriment_button = CreateButton(self.__controller.GetName(objective['alternative']))
							requeriment_button.connect('clicked',self.__AddObjective)

							# Put requeriment button
							coords = (x,y)
							self.layout.put(requeriment_button, int(coords[0]),int(coords[1]))
							if not req_coords.has_key(objective['objective_id']):
								req_coords[objective['objective_id']] = {}
							req_coords[objective['objective_id']][objective['requeriment']] = coords

							UpdateLayoutSize(x+self.x_step,y+self.y_step)

							# Increase level requeriments
							if not level_requeriments.has_key(objective['objective_id']):
								level_requeriments[objective['objective_id']] = []
							level_requeriments[objective['objective_id']].append(objective['requeriment'])
							x += self.x_step + random.randint(0, self.x_step/2)

						# Store the requeriment arrow coordinates
						self.__req_arrows.append((coords, GetCoordinates(objective['alternative'])))

			# If level has had requeriments,
			# reset objectives coordinates
			if(level_requeriments):
				x = random.randint(0, self.x_step)
				y += self.y_step

				level_requeriments = {}

			# Objectives
			for objective in level:
				# Objective arrow
				if objective['requeriment']:
					if(not level_requeriments.has_key(objective['objective_id'])):
						level_requeriments[objective['objective_id']] = []

					# Requeriments with alternatives
					if objective['priority']:
						if(objective['requeriment'] not in level_requeriments[objective['objective_id']]):
							coords = GetCoordinates(objective['objective_id'], objective['requeriment'])

					# Requeriment without alternatives
					else:
						coords = GetCoordinates(objective['alternative'])
						print coords,objective

				# Objective
				if objective['objective_id'] not in objectives:

					# Get color of the requeriment
					def GetColor():
						# Blue - Satisfacted
						if self.__controller.IsSatisfacted(objective['objective_id']):
							show = self.preferences['showExceededDependencies']
							if(show):
								if(show==1 and objective['expiration'] and objective['expiration']<datetime.datetime):
									print show,objective['expiration'],datetime.datetime
									return None
								return gtk.gdk.color_parse(self.preferences['color_satisfacted'])
							return None

						# Green - Available
						elif self.__controller.IsAvailable(objective['objective_id']):
							return gtk.gdk.color_parse(self.preferences['color_available'])

						# Yellow - InProgress
						elif self.__controller.IsInprocess(objective['objective_id']):
							return gtk.gdk.color_parse(self.preferences['color_inprocess'])

						# Red - Unabordable
						return gtk.gdk.color_parse(self.preferences['color_unabordable'])


					color = GetColor()
					if(color):
						# Create objective button
						button = CreateButton(objective['name'])

						# Tooltip
						button.set_tooltip_text("Cantidad: "+str(objective['objective_quantity']))
						if(objective["expiration"]):
							button.set_tooltip_text(button.get_tooltip_text()+"\nExpiracion: "+objective['expiration'])
						dependents = self.__controller.DirectDependents(objective['objective_id'])
						if(dependents):
							button.set_tooltip_text(button.get_tooltip_text()+"\nDependents: "+str(len(dependents)))

						def SetExpirationColor():

							# Expired and not satisfacted - Show warning
							if(objective["expiration"]
							and not self.__controller.IsSatisfacted(objective['objective_id'])):

								# Expired - Set inverted color
								if(datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S")
								<datetime.datetime.now()):
									button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
									button.child.modify_fg(gtk.STATE_NORMAL, color)
									return

								# Next to expire - Set color animation
								elif(datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S")
								< datetime.datetime.now()+datetime.timedelta(self.preferences['expirationWarning'])):

									def button_expires_inverted(button, color):
										button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
										button.child.modify_fg(gtk.STATE_NORMAL, color)

										glib.timeout_add_seconds(1, button_expires_normal, button, color)
										return False

									def button_expires_normal(button, color):
										button.modify_bg(gtk.STATE_NORMAL, color)
										button.child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))

										glib.timeout_add_seconds(1, button_expires_inverted, button, color)
										return False

									button_expires_normal(button, color)
									return

							# Non expired - Set background color
							button.modify_bg(gtk.STATE_NORMAL, color)

						SetExpirationColor()

						button.connect('clicked',self.__AddObjective)

						# Put objective button
						self.layout.put(button, int(x),int(y))
						obj_coords[objective['objective_id']] = (x,y)

						UpdateLayoutSize(x+self.x_step,y+self.y_step)

						# Register objective to prevent be printed twice
						objectives.append(objective['objective_id'])

						x += self.x_step + random.randint(0, self.x_step/2)

				# If objective has requeriments,
				# store the requeriment arrow coordinates
				if(coords	# [To-Do] Optimizar para requisitos sin alternativas
				and level_requeriments.has_key(objective['objective_id'])
				and objective['requeriment'] not in level_requeriments[objective['objective_id']]):
					self.__req_arrows.append((GetCoordinates(objective['objective_id']), coords))
					level_requeriments[objective['objective_id']].append(objective['requeriment'])
					print self.__req_arrows

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
		dialog = Preferences(self.__controller)

		dialog.window.set_transient_for(self.window)
		response = dialog.window.run()
		dialog.window.destroy()

		# Reload preferences if neccesary
		if response > 0:
			self.preferences = preferences.Load()
			self.__CreateTree()

	def __on_Main_destroy(self, widget, data=None):
		gtk.main_quit()
