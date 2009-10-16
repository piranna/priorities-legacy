import glib
import gtk
#import random
import math
import datetime

import navigationbar

import View_Gtk

from View_Gtk_About import *
from View_Gtk_AddObjective import *
from View_Gtk_DeleteCascade import *
from View_Gtk_Preferences import *


class Main(View_Gtk.View):
	x_step = 100
	y_step = 50

	def __init__(self, database,useDefaultDB):
		View_Gtk.View.__init__(self)

		self.__objectiveHI_edit = None
		self.__objectiveHI_delete = None
		self.__objectiveHI_zoomin = None

		self.__cursorObjective = None

		self.__zoomlevel = 0

		if not (database and useDefaultDB):
			self.__AskDB(database)

		self.window = self.builder.get_object("Main")
		self.window.connect('destroy',self.__on_Main_destroy)

		self.layout = self.builder.get_object("layout")
		self.layout.connect('expose-event',self.__DrawRequerimentsArrows)
		self.layout.connect('button-press-event',self.__ShowLayoutMenu)

		# Navigation Bar
		self.navBar = navigationbar.NavigationBar()
		self.navBar.show()
		vbox1 = self.builder.get_object("vbox1")
		vbox1.pack_start(self.navBar, False)
		vbox1.reorder_child(self.navBar, 1)

		# Start button
		self.navBar.add_with_id("gtk-home", self.__Zoom, 0)
		self.navBar.get_button_from_id(0).set_use_stock(True)

		#
		# File

		# New
#		mnuNew = self.builder.get_object("mnuNew")
#		mnuNew.connect('activate',self.__on_Main_destroy)

		# Open
#		mnuOpen = self.builder.get_object("mnuOpen")
#		mnuOpen.connect('activate',self.__on_Main_destroy)

		# Save
#		mnuSave = self.builder.get_object("mnuSave")
#		mnuSave.connect('activate',self.__on_Main_destroy)

		# Save as
#		mnuSaveAs = self.builder.get_object("mnuSaveAs")
#		mnuSaveAs.connect('activate',self.__on_Main_destroy)

		# Import
		mnuImport = self.builder.get_object("mnuImport")
		mnuImport.connect('activate',self.__Import)

		# Export
		mnuExport = self.builder.get_object("mnuExport")
		mnuExport.connect('activate',self.__Export)

		# Exit
		mnuExit = self.builder.get_object("mnuExit")
		mnuExit.connect('activate',self.__on_Main_destroy)

		#
		# Edit

		# Preferences
		mnuPreferences = self.builder.get_object("mnuPreferences")
		mnuPreferences.connect('activate',self.__Preferences)

		#
		# Objective

		# Add
		mnuObjective_Add = self.builder.get_object("mnuObjective_Add")
		mnuObjective_Add.connect('activate',self.__AddObjective)

		# Delete
#		mnuObjective_Del = self.builder.get_object("mnuObjective_Del")
#		mnuObjective_Del.connect('activate',self.__AddObjective)

		#
		# Help

		# About
		mnuAbout = self.builder.get_object("mnuAbout")
		mnuAbout.connect('activate',self.__About)

		#
		# Contextual menues

		# Layout
		self.mnuCtxLayout = self.builder.get_object("mnuCtxLayout")
		mnuLayout_AddObjective = self.builder.get_object("mnuLayout_AddObjective")
		mnuLayout_AddObjective.connect('activate',self.__AddObjective)

		mnuLayout_ZoomIn = self.builder.get_object("mnuLayout_ZoomIn")
		mnuLayout_ZoomIn.connect('activate',self.__ZoomIn)

		mnuLayout_ZoomOut = self.builder.get_object("mnuLayout_ZoomOut")
		mnuLayout_ZoomOut.connect('activate',self.__ZoomOut)

		# Objective
		self.mnuCtxObjective = self.builder.get_object("mnuCtxObjective")
		self.mnuObjective_Edit = self.builder.get_object("mnuObjective_Edit")
		self.mnuObjective_Delete = self.builder.get_object("mnuObjective_Delete")

		self.mnuObjective_ZoomIn = self.builder.get_object("mnuObjective_ZoomIn")

		mnuObjective_ZoomOut = self.builder.get_object("mnuObjective_ZoomOut")
		mnuObjective_ZoomOut.connect('activate',self.__ZoomOut)

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
			self.controller.Connect(dialog.get_filename())

		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, no files selected'
			import sys
			sys.exit(0)

		dialog.destroy()


	def __DrawRequerimentsArrows(self, widget,event):
		# Graphic Context
		gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]


		def DrawHead(arrow):
			def ArrowPoint(arrow, angle, lenght):
				angle = math.radians(angle)

#				print arrow,angle,lenght
				cotan = math.atan((arrow[1][0]-arrow[2][0])/(arrow[1][1]-arrow[2][1]))+angle

				return (arrow[2][0]+math.sin(cotan)*lenght, arrow[2][1]+math.cos(cotan)*lenght)

			arrowPoint = ArrowPoint(arrow, 15, 15)
			self.layout.bin_window.draw_line(gc, int(arrow[2][0]),int(arrow[2][1]),
												int(arrowPoint[0]),int(arrowPoint[1]))

			arrowPoint = ArrowPoint(arrow, -15, 15)
			self.layout.bin_window.draw_line(gc, int(arrow[2][0]),int(arrow[2][1]),
												int(arrowPoint[0]),int(arrowPoint[1]))


#		self.layout.queue_draw()

		# Background sharp
		if(self.config.Get('showSharp')):
			layout_size = self.layout.get_size()
			for x in range(1,layout_size[0]/self.x_step):
				self.layout.bin_window.draw_line(gc, x*self.x_step,0,
													x*self.x_step,layout_size[1])
			for y in range(1,layout_size[1]/self.y_step):
				self.layout.bin_window.draw_line(gc, 0,y*self.y_step,
													layout_size[0],y*self.y_step)

			# Left
#			self.layout.bin_window.draw_line(gc, 0,0,
#												x*self.x_step,layout_size[1])
			# Top
#			self.layout.bin_window.draw_line(gc, 0,0,
#												layout_size[0],y*self.y_step)
			# Right
			self.layout.bin_window.draw_line(gc, layout_size[0],0,
												layout_size[0],layout_size[1])
			# Down
			self.layout.bin_window.draw_line(gc, 0,layout_size[1],
												layout_size[0],layout_size[1])

		# Arrows
#		print self.__req_arrows
		for arrow in self.__req_arrows:
#			print "\t",arrow

			if arrow[0]==self.__cursorObjective:
				gc.set_line_attributes(2, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)
			else:
				gc.set_line_attributes(0, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)

			# Arrow line
			self.layout.bin_window.draw_line(gc, int(arrow[1][0]),int(arrow[1][1]),
												int(arrow[2][0]),int(arrow[2][1]))
			# Arrow head
			if self.config.Get("showArrowHeads"):
				DrawHead(arrow)

		gc.set_line_attributes(0, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)
#		print


	def __CreateTree(self, objective_name=None):
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
		for level in self.controller.ShowTree(objective_name):
			def UpdateLayoutSize(width,height):
				layout_size_x = self.layout.get_size()[0]
				layout_size_y = self.layout.get_size()[1]
				if layout_size_x < width:
					layout_size_x = width
				if layout_size_y < height:
					layout_size_y = height
				self.layout.set_size(int(layout_size_x),
											int(layout_size_y))

			def CreateButton(label,objective_id):
				button = gtk.Button(label)
				button.set_focus_on_click(False)
				button.show()
				button.connect('clicked',self.__AddObjective, objective_id)
				button.connect('enter_notify_event',self.__IncreaseLineWidth, objective_id)
				button.connect('leave_notify_event',self.__IncreaseLineWidth)
				return button

			x = self.x_step/2.0
#			x = random.randint(self.x_step/2.0,self.x_step)
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
														+self.controller.GetName(objective['alternative']))

						# else create a new one
						else:
							# Create requeriment button
							requeriment_button = CreateButton(self.controller.GetName(objective['alternative']),
																objective['objective_id'])

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
							x += self.x_step
#							x += self.x_step + random.randint(0, self.x_step/2)

						# Store the requeriment arrow coordinates
						self.__req_arrows.append((objective['objective_id'],coords, GetCoordinates(objective['alternative'])))

			# If level has had requeriments,
			# reset objectives coordinates
			if(level_requeriments):
				x = 0
#				x = random.randint(0, self.x_step)
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
#						print coords,objective

				# Objective
				if objective['objective_id'] not in objectives:

					# Get color of the requeriment
					def GetColor():
						# Blue - Satisfacted
						if self.controller.IsSatisfacted(objective['objective_id']):
							show = self.config.Get('showExceededDependencies')
							if(show):
								if(show==1
								and objective['expiration']
								and objective['expiration']<datetime.datetime):
									return None
								return gtk.gdk.color_parse(self.config.Get('color_satisfacted'))
							return None

						# Green - Available
						elif self.controller.IsAvailable(objective['objective_id']):
							return gtk.gdk.color_parse(self.config.Get('color_available'))

						# Yellow - InProgress
						elif self.controller.IsInprocess(objective['objective_id']):
							return gtk.gdk.color_parse(self.config.Get('color_inprocess'))

						# Red - Unabordable
						return gtk.gdk.color_parse(self.config.Get('color_unabordable'))


					color = GetColor()
					if(color):
						# Create objective button
						button = CreateButton(objective['name'], objective['objective_id'])
						button.connect('button-press-event',self.__on_objective_clicked)

						# Tooltip
						button.set_tooltip_text("Cantidad: "+str(objective['objective_quantity']))
						if(objective["expiration"]):
							button.set_tooltip_text(button.get_tooltip_text()+"\nExpiracion: "+objective['expiration'])
						dependents = self.controller.DirectDependents(objective['objective_id'])
						if(dependents):
							button.set_tooltip_text(button.get_tooltip_text()+"\nDependents: "+str(len(dependents)))

						def SetExpirationColor():

							# Expired and not satisfacted - Show warning
							if(objective["expiration"]
							and not self.controller.IsSatisfacted(objective['objective_id'])):

								# Expired - Set inverted color
								if(datetime.datetime.strptime(objective["expiration"],"%Y-%m-%d %H:%M:%S")
								<datetime.datetime.now()):
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
										button.modify_bg(gtk.STATE_NORMAL, color)
										button.child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))

										glib.timeout_add_seconds(1, button_expires_inverted, button, color)
										return False

									button_expires_normal(button, color)
									return

							# Non expired - Set background color
							button.modify_bg(gtk.STATE_NORMAL, color)

						SetExpirationColor()

						# Put objective button
						self.layout.put(button, int(x),int(y))
						obj_coords[objective['objective_id']] = (x,y)

						UpdateLayoutSize(x+self.x_step,y+self.y_step)

						# Register objective to prevent be printed twice
						objectives.append(objective['objective_id'])

						x += self.x_step
#						x += self.x_step + random.randint(0, self.x_step/2)

				# If objective has requeriments,
				# store the requeriment arrow coordinates
				if(coords	# [To-Do] Optimizar para requisitos sin alternativas
				and level_requeriments.has_key(objective['objective_id'])
				and objective['requeriment'] not in level_requeriments[objective['objective_id']]):
					self.__req_arrows.append((objective['objective_id'],GetCoordinates(objective['objective_id']), coords))
					level_requeriments[objective['objective_id']].append(objective['requeriment'])
#					print self.__req_arrows

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


	def __AddObjective(self, widget, objective_id=None):
		addObjective = AddObjective(objective_id)
		addObjective.window.set_transient_for(self.window)

		if addObjective.window.run() > 0:
			self.__CreateTree()

		addObjective.window.destroy()


	def __DelObjective(self, menuitem,objective_id):
		if(self.config.Get('deleteCascade')
		and len(self.controller.DirectDependencies(objective_id))>1):
			dialog = DeleteCascade(objective_id)

			if self.config.Get('confirmDeleteCascade'):
				dialog.window.set_transient_for(self.window)
				response = dialog.window.run()
				dialog.window.destroy()

			else:
				response = dialog.DeleteObjective_recursive()

			if response > 0:
				self.__CreateTree()

		else:
			dialog = gtk.MessageDialog(self.window,
										0,
										gtk.MESSAGE_QUESTION,
										gtk.BUTTONS_YES_NO,
										"Desea eliminar el objetivo "+self.controller.GetName(objective_id)+"?")
			if dialog.run() == gtk.RESPONSE_YES:
				self.controller.DeleteObjective(objective_id,
												self.config.Get('removeOrphanRequeriments'))
				self.__CreateTree()
			dialog.destroy()


	def __on_objective_clicked(self, widget,event):
		if(event.button == 3):	# Secondary button
			objective_id = self.controller.GetId(widget.get_label())

			if self.__objectiveHI_edit:
				self.mnuObjective_Edit.disconnect(self.__objectiveHI_edit)
			self.__objectiveHI_edit = self.mnuObjective_Edit.connect('activate',self.__AddObjective, objective_id)

			if self.__objectiveHI_delete:
				self.mnuObjective_Delete.disconnect(self.__objectiveHI_delete)
			self.__objectiveHI_delete = self.mnuObjective_Delete.connect('activate',self.__DelObjective, objective_id)

			if self.__objectiveHI_zoomin:
				self.mnuObjective_ZoomIn.disconnect(self.__objectiveHI_zoomin)
			self.__objectiveHI_zoomin = self.mnuObjective_ZoomIn.connect('activate',self.__ZoomIn, widget.get_label())


			self.mnuCtxObjective.popup(None,None,None, event.button,event.time)


	def __ShowLayoutMenu(self, widget,event):
		print "__ShowLayoutMenu"
		if(event.button == 3):	# Secondary button
			print "\tsecondary button"
			self.mnuCtxLayout.popup(None,None,None, event.button,event.time)


	def __Preferences(self, widget):
		dialog = Preferences()
		dialog.window.set_transient_for(self.window)

		# Redraw tree if necesary
		if(dialog.window.run() > 0
		and dialog.redraw_tree):
			self.__CreateTree()

		dialog.window.destroy()


	def __on_Main_destroy(self, widget, data=None):
		gtk.main_quit()


	def __SetFileFilters(self, dialog):
		"""Create and add the priorities exported file filter"""
		filter = gtk.FileFilter()
		filter.set_name("Priorities exported file")
		filter.add_pattern("*.priorities")
		dialog.add_filter(filter)
		"""Create and add the 'all files' filter"""
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)


	def __Export(self, widget):
		dialog = gtk.FileChooserDialog("Export priorities database",
										None,
										gtk.FILE_CHOOSER_ACTION_SAVE,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
											gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		dialog.set_current_name("export.priorities")

		self.__SetFileFilters(dialog)

		if dialog.run()==gtk.RESPONSE_OK:
			try:
				file = open(dialog.get_filename(), "w")
				file.write(self.controller.Export())
				file.close()
			except:
				print "Exception exporting database"
		dialog.destroy()


	def __Import(self, widget):
		dialog = gtk.FileChooserDialog("Export priorities database",
										None,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
											gtk.STOCK_SAVE,gtk.RESPONSE_OK))
#		dialog.set_current_name("export.priorities")

		self.__SetFileFilters(dialog)

		if dialog.run()==gtk.RESPONSE_OK:
			try:
				import Parser
				parser = Parser.Parser(self.controller, dialog.get_filename())
				parser.cmdloop()
			except:
				print "Exception importing database"
		dialog.destroy()


	def __IncreaseLineWidth(self, widget,event, objective_id=None):
		self.__cursorObjective = objective_id
		self.layout.queue_draw()


	def __Zoom(self):
		self.__CreateTree(objective_name)


	def __ZoomIn(self, widget, objective_name=None):
		print "__ZoomIn"
		if objective_name:
			self.__zoomlevel += 1
			self.navBar.add_with_id(objective_name, self.__CreateTree, self.__zoomlevel)
			self.__CreateTree(objective_name)

		else:
			pass


	def __ZoomOut(self, widget):
		print "__ZoomOut"
		self.__zoomlevel -= 1
		self.__CreateTree(objective_name)