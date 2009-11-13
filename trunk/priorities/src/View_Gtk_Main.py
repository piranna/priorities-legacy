import gtk
import math
import datetime

import navigationbar

import View_Gtk
_ = View_Gtk._

from View_Gtk_About import *
from View_Gtk_AddObjective import *
from View_Gtk_DeleteCascade import *
from View_Gtk_Preferences import *


class Main(View_Gtk.View_Gtk):
	margin_x = 50
	margin_y = 50

	def __init__(self, input=None):
		View_Gtk.View_Gtk.__init__(self, "Main")

		if input and not self.controller.Import(input):
			print _("Exception importing database")

		self.__objectiveHI_edit = None
		self.__objectiveHI_delete = None
		self.__objectiveHI_zoomin = None

		self.__needRenderGraph = False
		self.__objectives = None
		self.__levels = None

		self.__cursorObjective = None

		self.layout = self.builder.get_object("layout")
		self.layout.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

		# Navigation Bar
		self.navBar = navigationbar.NavigationBar()
		self.navBar.show()
		vbox1 = self.builder.get_object("vbox1")
		vbox1.pack_start(self.navBar, False)
		vbox1.reorder_child(self.navBar, 2)

		#
		# File

		self.mnuSaveAs = self.builder.get_object("mnuSaveAs")
		self.mnuExport = self.builder.get_object("mnuExport")

		#
		# View

		self.mnuZoomIn = self.builder.get_object("mnuZoomIn")
		self.mnuZoomOut = self.builder.get_object("mnuZoomOut")

		#
		# Contextual menues

		# Layout
#		mnuLayout_ZoomIn = self.builder.get_object("mnuLayout_ZoomIn")
#		mnuLayout_ZoomOut = self.builder.get_object("mnuLayout_ZoomOut")

		# Objective
		self.mnuCtxObjective = self.builder.get_object("mnuCtxObjective")
		self.mnuObjective_Edit = self.builder.get_object("mnuObjective_Edit")
		self.mnuObjective_Delete = self.builder.get_object("mnuObjective_Delete")

		self.mnuObjective_ZoomIn = self.builder.get_object("mnuObjective_ZoomIn")
		self.mnuObjective_ZoomOut = self.builder.get_object("mnuObjective_ZoomOut")

		#
		# Toolbar

		# Start button
		self.navBar.add_with_id("gtk-home", self.__NavbarHome, 0)
		self.navBar.get_button_from_id(0).set_use_stock(True)

		self.window.show()
		gtk.main()


	def __OpenDB_dialog(self):
		dialog = gtk.FileChooserDialog(_("Select the database to use"),
										None,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		# sqlite files
		dialogFilter = gtk.FileFilter()
		dialogFilter.set_name("SQLite database")
		dialogFilter.add_pattern("*.sqlite")
		dialog.add_filter(dialogFilter)
		# Priorities export file
		dialogFilter = gtk.FileFilter()
		dialogFilter.set_name(_("Priorities export file"))
		dialogFilter.add_pattern("*.priorities")
		dialog.add_filter(dialogFilter)
		# All files
		dialogFilter = gtk.FileFilter()
		dialogFilter.set_name("All files")
		dialogFilter.add_pattern("*")
		dialog.add_filter(dialogFilter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			response = dialog.get_filename()

			# Export file
			if response[-11:] == ".priorities":
				self.controller.Connect(":memory:")
				if not self.controller.Import(response):
					print _("Exception importing database")
					dialog.destroy()
					return False

			# Database
			else:
				self.controller.Connect(response)

			dialog.destroy()
			return True

		else:
			dialog.destroy()
			return False


	def __AskDB(self):
		if not self.__OpenDB_dialog():
			import sys
			sys.exit(0)


	def OpenDB(self, widget):
		if self.__OpenDB_dialog():
			self.__CreateGraph()


	def __SaveDB_dialog(self):
		dialog = gtk.FileChooserDialog(_("Select the database to create"),
										None,
										gtk.FILE_CHOOSER_ACTION_SAVE,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
										gtk.STOCK_NEW,gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_do_overwrite_confirmation(True)

		# sqlite files
		dialogFilter = gtk.FileFilter()
		dialogFilter.set_name(_("SQLite database"))
		dialogFilter.add_pattern("*.sqlite")
		dialog.add_filter(dialogFilter)
		# All files
		dialogFilter = gtk.FileFilter()
		dialogFilter.set_name("All files")
		dialogFilter.add_pattern("*")
		dialog.add_filter(dialogFilter)

		return dialog


	def NewDB(self, widget):
		dialog = self.__SaveDB_dialog()

		if dialog.run() == gtk.RESPONSE_OK:
			self.controller.Connect(dialog.get_filename()+".sqlite")
			self.__CreateGraph()

		dialog.destroy()


	def SaveDBAs(self, widget):
		dialog = self.__SaveDB_dialog()

		if dialog.run() == gtk.RESPONSE_OK:
			self.controller.Backup(dialog.get_filename()+".sqlite")
			self.controller.Connect(dialog.get_filename()+".sqlite")

		dialog.destroy()


	def DrawRequerimentsArrows(self, widget,event):
		if self.__needRenderGraph:
			self.__needRenderGraph = False
			self.__RenderGraph()

		if self.__levels:
			# Graphic Context
			gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]


			def DrawHead(arrow):
				def ArrowPoint(arrow, angle, lenght):
					angle = math.radians(angle)

					cotan = arrow[1][1]-arrow[2][1]
					if cotan:
						cotan = math.atan((arrow[1][0]-arrow[2][0])/cotan)+angle

					return (arrow[2][0]+math.sin(cotan)*lenght, arrow[2][1]+math.cos(cotan)*lenght)

				arrowPoint = ArrowPoint(arrow, 15, 30)
				self.layout.bin_window.draw_line(gc, int(arrow[2][0]),int(arrow[2][1]),
													int(arrowPoint[0]),int(arrowPoint[1]))

				arrowPoint = ArrowPoint(arrow, -15, 30)
				self.layout.bin_window.draw_line(gc, int(arrow[2][0]),int(arrow[2][1]),
													int(arrowPoint[0]),int(arrowPoint[1]))


			# Background sharp
			layout_size = self.layout.get_size()

			if(self.config.Get('showSharp')):
				for x in range(1,layout_size[0]/self.margin_x+1):
					self.layout.bin_window.draw_line(gc, x*self.margin_x,0,
														x*self.margin_x,layout_size[1])
				for y in range(1,layout_size[1]/self.margin_y+1):
					self.layout.bin_window.draw_line(gc, 0,y*self.margin_y,
														layout_size[0],y*self.margin_y)

			# Left
			self.layout.bin_window.draw_line(gc, 0,0,
												0,layout_size[1])
			# Top
			self.layout.bin_window.draw_line(gc, 0,0,
												layout_size[0],0)
			# Right
			self.layout.bin_window.draw_line(gc, layout_size[0],0,
												layout_size[0],layout_size[1])
			# Down
			self.layout.bin_window.draw_line(gc, 0,layout_size[1],
												layout_size[0],layout_size[1])

#			# Arrows
#			for arrow in self.__req_arrows:
#				line_width = 0
#				if arrow[0]==self.__cursorObjective:
#					line_width = 2
#				gc.set_line_attributes(line_width, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)
#
#				# Arrow line
#				self.layout.bin_window.draw_line(gc, int(arrow[1][0]),int(arrow[1][1]),
#													int(arrow[2][0]),int(arrow[2][1]))
#				# Arrow head
#				if self.config.Get("showArrowHeads"):
#					DrawHead(arrow)

			gc.set_line_attributes(0, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)


	def __RenderGraph(self):
		if self.__objectives:
			biggest_row_width = 0
			y = self.margin_y/2

			print "self.__objectives",self.__objectives

			keys = self.__objectives.keys()
			keys.sort()
			for level in keys:

				print level

				biggest_height = 0
				x = self.margin_x/2
				for button in self.__objectives[level]:

#####
					# Get requeriment coordinates
					def Get_RequerimentCoordinate_X():
						min_x = None
						max_x = None
###
						requeriments = button.Get_Requeriments()
						print "requeriments"
						print requeriments
						print
						if requeriments:
							for req in requeriments:
								print "\t",req.get_label(),req.allocation.x
								if(min_x == None
								or req.allocation.x < min_x):
									min_x = req.allocation.x

								if(max_x == None
								or req.allocation.x+req.allocation.width > max_x):
									max_x = req.allocation.x+req.allocation.width

							print min_x
							print max_x
							print "x =",(min_x+max_x)/2

							return (min_x+max_x)/2
###
						return None

					def Set_DependenceCoordinate_X():
						pass


					req_x = Get_RequerimentCoordinate_X()
					if req_x > x:
						x = req_x
#					else:
#						Set_DependenceCoordinate_X()
#####

					# Set button position
#					print "button",button.allocation
					self.layout.move(button, x,y)
#					print "\t",button.allocation

					# Set new x coordinate
					# and layout sizes
					x += button.allocation.width
					if x > biggest_row_width:
						biggest_row_width = x

					x += self.margin_x

					if button.allocation.height > biggest_height:
						biggest_height = button.allocation.height

				# Set new y coordinate
				y += biggest_height + self.margin_y

			# Set layout size
			# and show all buttons
			self.layout.set_size(int(biggest_row_width + self.margin_x/2), int(y - self.margin_y/2))
			self.layout.show_all()


	def __CreateGraph(self, objective_name=None):
		self.__CleanGraph()

		import GraphRenderer

		self.__levels = self.controller.ShowTree(objective_name)
		if self.__levels:

			# Level index
			y = 0

			self.__needRenderGraph = True
			self.__objectives = {}

			checked_objectives = {}

			# Niveles
			for level in self.__levels:
				def PutButton(button):
					self.layout.put(button, 0,0)
					if not self.__objectives.has_key(y):
						self.__objectives[y] = []
					self.__objectives[y].append(button)


				# Requeriments
				requeriment_button = None

				level_requeriments = {}
				level_need_alternatives = False

				for objective in level:
					# Requeriments
					if objective['requeriment']:
						if not level_requeriments.has_key(objective['objective_id']):
							level_requeriments[objective['objective_id']] = []

						# Requeriment with alternatives
						if objective['priority']:

							# If requeriment is registered,
							# add alternative
							if objective['requeriment'] in level_requeriments[objective['objective_id']]:
								requeriment_button.set_label(requeriment_button.get_label()+"\n"
															+self.controller.GetName(objective['alternative']))
								requeriment_button.Add_Dependency(checked_objectives[objective['alternative']])
								continue

							# else create a new one
							else:
								# Put old requeriment button, if any
								if requeriment_button:
									PutButton(requeriment_button)

								# Create new requeriment button
								requeriment_button = GraphRenderer.Requeriment(self.controller.GetName(objective['alternative']),
																				objective['objective_id'],
																				self)
								level_need_alternatives = True

								requeriment_button.Add_Dependency(checked_objectives[objective['alternative']])

						# Add requeriment
#						if requeriment_button:
#							requeriment_button.Add_Dependency(checked_objectives[objective['alternative']])
						level_requeriments[objective['objective_id']].append(objective['requeriment'])

				# Put remanent requeriment button, if any
				if requeriment_button:
					PutButton(requeriment_button)

#				print "level_requeriments",level_requeriments

				# If level has had requeriments,
				# reset objectives coordinates
				if(level_need_alternatives):
#				if(level_requeriments and level_need_alternatives):
					y += 1


				# Objectives
				for objective in level:
					# Objective
					if objective['objective_id'] not in checked_objectives:

						# Get color of the requeriment
						def GetColor():
							# Blue - Satisfacted
							if self.controller.IsSatisfacted(objective['objective_id']):
								show = self.config.Get('showExceededDependencies')
								if(show):
									if(show==1					# 1 == Only not expired
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


						# Check if objective has to be printed and with what color
						color = GetColor()
						if(color):
							# Create objective button
							# and register to prevent be printed twice
							checked_objectives[objective['objective_id']] = GraphRenderer.Objective(objective, self,
																									self.controller, color)

							# Create objective button
							PutButton(checked_objectives[objective['objective_id']])

				# Increase level index
				y += 1


		self.__ExportSaveSensitivity()
		self.__ShowZoom()


	def __ExportSaveSensitivity(self):
		"Set the sensitivity of the export buttons"
		self.builder.get_object("tbSaveAs").set_sensitive(len(self.__levels))
		self.mnuSaveAs.set_sensitive(len(self.__levels))
		self.mnuExport.set_sensitive(len(self.__levels))


	def __ShowZoom(self):
		actual = self.navBar.get_active_position()

		# Zoom In
		self.mnuZoomIn.set_sensitive(actual<len(self.navBar.get_children())-1)
		self.builder.get_object("tbZoomIn").set_sensitive(actual<len(self.navBar.get_children())-1)

		# Zoom Out
		self.mnuZoomOut.set_sensitive(actual>0)
		self.builder.get_object("tbZoomOut").set_sensitive(actual>0)
		self.mnuObjective_ZoomOut.set_sensitive(actual>0)


	def __CleanGraph(self):
		# Clean arrows array
#		self.__req_arrows = []
		self.__objectives = {}

		# Delete old buttons
		for children in self.layout.get_children():
			self.layout.remove(children)

		# Re-draw surface of the layout
		self.layout.queue_draw()


	def About(self, widget):
		about = About()
		about.window.set_transient_for(self.window)

		about.window.run()

		about.window.destroy()


	def AddObjective(self, widget, objective_id=None):
		addObjective = AddObjective(objective_id)
		addObjective.window.set_transient_for(self.window)

		if addObjective.window.run() > 0:
			self.__CreateGraph()

		addObjective.window.destroy()


	def DelObjective(self, menuitem,objective_id):
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
				self.__CreateGraph()

		else:
			dialog = gtk.MessageDialog(self.window,
										0,
										gtk.MESSAGE_QUESTION,
										gtk.BUTTONS_YES_NO,
										_("Do you want to delete the objetive ")+self.controller.GetName(objective_id)+"?")
			if dialog.run() == gtk.RESPONSE_YES:
				self.controller.DeleteObjective(objective_id,
												self.config.Get('removeOrphanRequeriments'))
				self.__CreateGraph()
			dialog.destroy()


	def __on_objective_clicked(self, widget,event):
		if(event.button == 3):	# Secondary button
			objective_id = self.controller.GetId(widget.get_label())

			if self.__objectiveHI_edit:
				self.mnuObjective_Edit.disconnect(self.__objectiveHI_edit)
			self.__objectiveHI_edit = self.mnuObjective_Edit.connect('activate',self.AddObjective, objective_id)

			if self.__objectiveHI_delete:
				self.mnuObjective_Delete.disconnect(self.__objectiveHI_delete)
			self.__objectiveHI_delete = self.mnuObjective_Delete.connect('activate',self.DelObjective, objective_id)

			if self.__objectiveHI_zoomin:
				self.mnuObjective_ZoomIn.disconnect(self.__objectiveHI_zoomin)
			self.__objectiveHI_zoomin = self.mnuObjective_ZoomIn.connect('activate',self.ZoomIn, widget.get_label())


			self.mnuCtxObjective.popup(None,None,None, event.button,event.time)


	def ShowLayoutMenu(self, widget,event):
		print "ShowLayoutMenu"
		if(event.button == 3):		# Secondary button
			print "\tsecondary button"
			self.builder.get_object("mnuCtxLayout").popup(None,None,None, event.button,event.time)


	def Preferences(self, widget):
		dialog = Preferences()
		dialog.window.set_transient_for(self.window)

		# Redraw tree if necesary
		if dialog.window.run() > 0:
			if dialog.redraw == "arrows":
				pass
			elif dialog.redraw == "tree":
				self.__CreateGraph()

		dialog.window.destroy()


	def on_Main_destroy(self, widget, data=None):
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


	def Export(self, widget):
		dialog = gtk.FileChooserDialog(_("Export priorities database"),
										None,
										gtk.FILE_CHOOSER_ACTION_SAVE,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
											gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		dialog.set_current_name("export")

		self.__SetFileFilters(dialog)

		"""PNG"""
		filter = gtk.FileFilter()
		filter.set_name(_("PNG image"))
		filter.add_pattern("*.png")
#		filter.add_pixbuf_formats()
		dialog.add_filter(filter)
		"""JPEG"""
		filter = gtk.FileFilter()
		filter.set_name(_("JPEG image"))
		filter.add_pattern("*.jpeg")
#		filter.add_pixbuf_formats()
		dialog.add_filter(filter)

		if dialog.run()==gtk.RESPONSE_OK:
			filter_name = dialog.get_filter().get_name()

			try:
				if(filter_name == _("PNG image")
				or filter_name == _("JPEG image")):
					layout_size = self.layout.get_size()
					if self.config.Get('showSharp'):
						layout_size = (layout_size[0]+1,layout_size[1]+1)

					pixbuf = (gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True,8,
											layout_size[0],layout_size[1])
										.get_from_drawable(self.layout.get_bin_window(),
														gtk.gdk.colormap_get_system(),
														0,0,0,0,
														layout_size[0],layout_size[1]))

					if filter_name == _("PNG image"):
						pixbuf.save(dialog.get_filename()+".png", "png")

					elif filter_name == _("JPEG image"):
						pixbuf.save(dialog.get_filename()+".jpeg", "jpeg")

				else:
					file = open(dialog.get_filename()+".priorities", "w")
					file.write(self.controller.Export(self.navBar.get_active_id()))
					file.close()

			except:
				print _("Exception exporting database")

		dialog.destroy()


	def Import(self, widget):
		dialog = gtk.FileChooserDialog(_("Import priorities database"),
										None,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
											gtk.STOCK_OPEN,gtk.RESPONSE_OK))
#		dialog.set_current_name("export.priorities")

		self.__SetFileFilters(dialog)

		if dialog.run()==gtk.RESPONSE_OK:
			if self.controller.Import(dialog.get_filename()):
				self.__CreateGraph(self.navBar.get_active_id())
			else:
				print _("Exception importing database")

		dialog.destroy()


	def __IncreaseLineWidth(self, widget,event, objective_id=None):
		self.__cursorObjective = objective_id
		self.layout.queue_draw()


	# Zoom
	def __NavbarHome(self, widget):
		self.__CreateGraph()


	def __NavbarZoom(self, widget):
		self.__CreateGraph(widget.get_label())


	def ZoomIn(self, widget, objective_name=None):
		print "__ZoomIn"

		if objective_name:
			self.navBar.remove_remanents()
			self.navBar.add_with_id(objective_name, self.__NavbarZoom, self.controller.GetId(objective_name))
			self.__CreateGraph(objective_name)

		else:
			try:
				self.navBar.get_children()[self.navBar.get_active_position()+1].clicked()
			except:
				pass


	def ZoomOut(self, widget):
		print "__ZoomOut"

		position = self.navBar.get_active_position()
		if position:
			self.navBar.get_children()[position-1].clicked()

