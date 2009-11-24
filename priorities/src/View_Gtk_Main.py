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
	margin_x = 20
	margin_y = 50

	def __init__(self, input=None):
		View_Gtk.View_Gtk.__init__(self, "Main")

		if input and not self.controller.Import(input):
			print _("Exception importing database")

		self.__objectiveHI_edit = None
		self.__objectiveHI_delete = None
		self.__objectiveHI_zoomin = None

		self.__cursorObjective = None

		self.__needRenderGraph = False

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
		if self.__objectives:


			self.__RenderGraph()


			# Graphic Context
			gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]


			def DrawHead(x1,y1, x2,y2):
				def ArrowPoint(angle, lenght):
					angle = math.radians(angle)

					cotan = y1-y2
					if cotan:
						cotan = math.atan((x1-x2)/cotan)+angle

					return (x2 + math.sin(cotan)*lenght, y2 + math.cos(cotan)*lenght)

				arrowPoint = ArrowPoint(15, 30)
				self.layout.bin_window.draw_line(gc, x2,y2,
													int(arrowPoint[0]),int(arrowPoint[1]))

				arrowPoint = ArrowPoint(-15, 30)
				self.layout.bin_window.draw_line(gc, x2,y2,
													int(arrowPoint[0]),int(arrowPoint[1]))


			# Background sharp
			layout_size = self.layout.get_size()
			print "\t",layout_size

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

			# Arrows
			for level in self.__objectives:
				for button in self.__objectives[level]:
					line_width = 0
					if button==self.__cursorObjective:
						line_width = 2
					gc.set_line_attributes(line_width, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)

					for requeriment in button.Get_Requeriments():
						# Arrow coordinates
						x1=button.X() + button.allocation.width/2
						y1=button.Y() + button.allocation.height/2
						x2=requeriment.X() + requeriment.allocation.width/2
						y2=requeriment.Y() + requeriment.allocation.height/2

						# Arrow line
						self.layout.bin_window.draw_line(gc, x1,y1, x2,y2)
						# Arrow head
						if self.config.Get("showArrowHeads"):
							DrawHead(x1,y1, x2,y2)

			gc.set_line_attributes(0, gtk.gdk.LINE_SOLID,gtk.gdk.CAP_BUTT,gtk.gdk.JOIN_MITER)


	def __RenderGraph(self):
		if self.__needRenderGraph:
			self.__needRenderGraph = False

			if self.__objectives:
#				biggest_row_width = 0
				y = self.margin_y/2

				keys = self.__objectives.keys()
				keys.sort()

#				self.__objectives[keys[0]][0].Adjust_x(self.margin_x/2)

				for level in keys:
					biggest_height = 0

					for button in self.__objectives[level]:
						if y!=button.Y():
							button.Y(y)

						if button.allocation.height > biggest_height:
							biggest_height = button.allocation.height

					# Set new y coordinate
					y += biggest_height + self.margin_y

				# Set layout size
				# and show all buttons

				biggest_row_width = self.__objectives[keys[0]][0].Adjust_x(self.margin_x/2)

#				self.layout.set_size(int(self.layout.get_size()[0] + self.margin_x/2),
#									int(y - self.margin_y/2))
				self.layout.set_size(int(biggest_row_width + self.margin_x/2), int(y - self.margin_y/2))

				self.layout.show_all()


	def __CreateGraph(self, objective_name=None):

		# Clean arrows array
		self.__objectives = {}

		# Delete old buttons
		for children in self.layout.get_children():
			self.layout.remove(children)

		# Re-draw surface of the layout
		self.layout.queue_draw()


		import GraphRenderer

		tree = self.controller.ShowTree(objective_name)
		if tree:

			self.__needRenderGraph = True

			# Level index
			y = 0

			checked_objectives = {}

			# Niveles
			for level in tree:
				def PutButton(button):
					self.layout.put(button, 0,0)
					if not self.__objectives.has_key(y):
						self.__objectives[y] = []
					else:
						self.__objectives[y][-1].Set_Next(button)
					self.__objectives[y].append(button)

				def Requeriments():
					button = None
					level_requeriments = {}

					for objective in level:
						# Requeriments
						if objective['requeriment']:
							if not level_requeriments.has_key(objective['objective_id']):
								level_requeriments[objective['objective_id']] = {}

							# Requeriment with alternatives
							if objective['priority']:

								# If requeriment is registered,
								# add alternative
								if objective['requeriment'] in level_requeriments[objective['objective_id']]:
									button.set_label(button.get_label()+"\n"
													+self.controller.GetName(objective['alternative']))

								# else create a new one
								else:
									# Put old requeriment button, if any
									if button:
										PutButton(button)

									# Create new requeriment button
									button = GraphRenderer.Requeriment(self.controller.GetName(objective['alternative']),
																		objective['objective_id'],
																		self)

									# Add requeriment
									level_requeriments[objective['objective_id']][objective['requeriment']] = button

								button.Add_Dependency(checked_objectives[objective['alternative']])

					print "level_requeriments",level_requeriments

					if button:
						PutButton(button)
					return level_requeriments

				def Objectives(level_requeriments):
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
								button = GraphRenderer.Objective(objective, self,
																self.controller, color)
								if objective['requeriment']:
									if objective['priority']:
										button.Add_Dependency(level_requeriments[objective['objective_id']][objective['requeriment']])
									else:
										button.Add_Dependency(checked_objectives[objective['alternative']])

								PutButton(button)

								# Register objective button to prevent be printed twice
								checked_objectives[objective['objective_id']] = button


				level_requeriments = Requeriments()
				if level_requeriments:
					y += 1
				Objectives(level_requeriments)
				y += 1

		self.__ExportSaveSensitivity()
		self.__ShowZoom()


	def __ExportSaveSensitivity(self):
		"Set the sensitivity of the export buttons"
		self.builder.get_object("tbSaveAs").set_sensitive(len(self.__objectives))
		self.mnuSaveAs.set_sensitive(len(self.__objectives))
		self.mnuExport.set_sensitive(len(self.__objectives))


	def __ShowZoom(self):
		actual = self.navBar.get_active_position()

		# Zoom In
		self.mnuZoomIn.set_sensitive(actual<len(self.navBar.get_children())-1)
		self.builder.get_object("tbZoomIn").set_sensitive(actual<len(self.navBar.get_children())-1)

		# Zoom Out
		self.mnuZoomOut.set_sensitive(actual>0)
		self.builder.get_object("tbZoomOut").set_sensitive(actual>0)
		self.mnuObjective_ZoomOut.set_sensitive(actual>0)


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


	def IncreaseLineWidth(self, widget,event, objective_id=None):
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

