import math

from datetime import datetime

from gtk import STATE_NORMAL
from gtk import FileChooserDialog
from gtk.gdk import CAP_BUTT,JOIN_MITER,LINE_SOLID
from gtk.gdk import color_parse

import navigationbar

from View.Gtk import Gtk,_

from View.Gtk.About import About
from View.Gtk.AddObjective import AddObjective
from View.Gtk.DeleteCascade import DeleteCascade
from View.Gtk.Preferences import *

from View.GraphRenderer import Objective,Requeriment


class Main(Gtk):
	margin_x = 20
	margin_y = 50

	def __init__(self, input=None):
		Gtk.__init__(self, "Main")

		if input and not self.controller.Import(input):
			print _("Exception importing database")

		self.__objectiveHI_edit = None
		self.__objectiveHI_delete = None
		self.__objectiveHI_zoomin = None

		self.__cursorObjective = None

		self.__needRenderGraph = False

		self.layout = self.builder.get_object("layout")
		self.layout.modify_bg(STATE_NORMAL, color_parse('white'))

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

		# Maximize
		if self.config.Get('maximized'):
			self.window.maximize()

		# Show window and start GTK main loop
		self.window.show()
		gtk.main()


	def __OpenDB_dialog(self):
		dialog = FileChooserDialog(_("Select the database to use"),
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

			# Get graphic Context
			gc = self.layout.get_style().fg_gc[gtk.STATE_NORMAL]

			# Background sharp
			layout_size = self.layout.get_size()

			bin_window = self.layout.bin_window

			if(self.config.Get('showSharp')):
				for x in range(1, layout_size[0]-1, self.margin_x):
					bin_window.draw_line(gc, x,0, x,layout_size[1])

				for y in range(1, layout_size[1]-1, self.margin_y):
					bin_window.draw_line(gc, 0,y, layout_size[0],y)

			# Layout borders
			if(self.config.Get('showLayoutBorders')):
				bin_window.draw_line(gc, 0,0,              0,layout_size[1])
				bin_window.draw_line(gc, 0,0,              layout_size[0],0)
				bin_window.draw_line(gc, layout_size[0],0, layout_size[0],layout_size[1])
				bin_window.draw_line(gc, 0,layout_size[1], layout_size[0],layout_size[1])

			# Arrows
			for level in self.__objectives.values():
				for button in level:
					gc.set_line_attributes(2 if button.objective==self.__cursorObjective else 0,
											LINE_SOLID,CAP_BUTT,JOIN_MITER)

					for requeriment in button.requeriments:

						# Arrow coordinates
						x1=button.X() + button.allocation.width/2
						y1=button.Y() + button.allocation.height/2
						x2=requeriment.X() + requeriment.allocation.width/2
						y2=requeriment.Y() + requeriment.allocation.height/2

						# Arrow line
						bin_window.draw_line(gc, x1,y1, x2,y2)

						# Arrow head
						if self.config.Get("showArrowHeads"):
							def DrawHead(x1,y1, x2,y2):
								def ArrowPoint(angle, lenght):
									angle = math.radians(angle)

									cotan = y1-y2
									if cotan:
										cotan = math.atan((x1-x2)/cotan)+angle

									return (x2 + math.sin(cotan)*lenght,
											y2 + math.cos(cotan)*lenght)

								arrowPoint = ArrowPoint(15, 30)
								bin_window.draw_line(gc, x2,y2, int(arrowPoint[0]),int(arrowPoint[1]))

								arrowPoint = ArrowPoint(-15, 30)
								bin_window.draw_line(gc, x2,y2, int(arrowPoint[0]),int(arrowPoint[1]))

							DrawHead(x1,y1, x2,y2)

			gc.set_line_attributes(0, LINE_SOLID,CAP_BUTT,JOIN_MITER)


	def __RenderGraph(self):
		if self.__needRenderGraph:
			self.__needRenderGraph = False

			if self.__objectives:
				y = self.margin_y/2

				biggest_width = self.margin_x/2

				# Get positions
				positions = {}
				for level in self.__objectives:
					for button in self.__objectives[level]:
						positions[button] = (button.allocation.x, button.allocation.y)

				# Adjust buttons
				levels = self.__objectives.keys()
				levels.sort()

				for level in levels:
					biggest_height = 0

					for button in self.__objectives[level]:
						if button.Adjust(positions,y):
							self.__needRenderGraph = True

						width = button.X() + button.allocation.width
						if  biggest_width < width:
							biggest_width = width

						if  biggest_height < button.allocation.height:
							biggest_height = button.allocation.height

					# Set new y coordinate
					y += biggest_height + self.margin_y

				# Set layout size
#				self.layout.set_size(int(self.layout.get_size()[0] + self.margin_x/2),
#									int(y - self.margin_y/2))
				self.layout.set_size(int(biggest_width + self.margin_x/2),
									int(y - self.margin_y/2))

				# Show all buttons
				self.layout.show_all()


	def __CreateGraph(self, objective=None):

		# Clean arrows array
		self.__objectives = {}

		# Delete old buttons
		for children in self.layout.get_children():
			self.layout.remove(children)

		# Re-draw surface of the layout
		self.layout.queue_draw()

		# Level index
		y = 0

		checked_objectives = {}
		pending_requeriments = {}

		for level in self.controller.GenTree(objective):

			self.__needRenderGraph = True

			level_objectives = []
			level_requeriments = []

			for name,objective in level.items():

				# Get color of the requeriment
				def GetColor():
					# Blue - Satisfacted
					if self.controller.IsSatisfaced(name):
						show = self.config.Get('showExceededDependencies')
						if show:
							expiration = objective['expiration']

							if(show == 1	# 1 == Only not expired
							and(expiration == None
							or expiration < datetime.now())):
								return color_parse(self.config.Get('color_satisfacted'))

						return None

					# Green - Available
					elif self.controller.IsAvailable(name):
						return color_parse(self.config.Get('color_available'))

					# Yellow - InProgress
					elif self.controller.IsInprocess(name):
						return color_parse(self.config.Get('color_inprocess'))

					# Red - Unabordable
					return color_parse(self.config.Get('color_unabordable'))

				# Check if objective has to be printed and with what color
				color = GetColor()
				if color:

					# Objective
					btnObj = Objective(name, self, objective, color)
					level_objectives.append(btnObj)

					# Requeriments
					for alternatives in objective['requeriments']:
						def AddAlternative(button, alternative):
							"""Try to add an alternative to an objective

							If the alternative is not checked previously (for
							example because circular references) it's stored as
							pending to be re-tried later
							"""
							try:
								requeriment = checked_objectives[alternative]

							except KeyError:
								if button not in pending_requeriments:
									pending_requeriments[button] = []
								pending_requeriments[button].append(alternative)

							else:
								button.Add_Requeriment(requeriment)

						# Requeriment don't have alternative (shouldn't happen)
						if not alternatives:
							pass

						# Requeriment has only one alternative, link it directly
						elif len(alternatives) == 1:
							AddAlternative(btnObj, alternatives.keys()[0])

						# Requeriment has several alternatives, create it and
						# link the alternatives
						else:
							btnReq = Requeriment(name, self)
							btnReq.set_label("\n".join(alternatives))

							for alternative in alternatives:
								AddAlternative(btnReq, alternative)

							level_requeriments.append(btnReq)

							btnObj.Add_Requeriment(btnReq)

					# Register objective button to prevent be printed twice
					checked_objectives[name] = btnObj

			def PutButton(button):
				self.layout.put(button, 0,0)
				if self.__objectives.has_key(y):
					button.prev = self.__objectives[y][-1]
				else:
					self.__objectives[y] = []
				self.__objectives[y].append(button)

			# Create level alternatives
			if level_requeriments:
				for requeriment in level_requeriments:
					PutButton(requeriment)
				y += 1

			# Create level objectives
			for objective in level_objectives:
				PutButton(objective)
			y += 1

		for button,alternatives in pending_requeriments.items():
			for alternative in alternatives:
				try:
					requeriment = checked_objectives[alternative]

				except KeyError:	# Definitively, alternative was not on the
					pass			# tree, I should raise error

				else:
					button.Add_Requeriment(requeriment)

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


	def AddObjective(self, widget, objective=None):
		addObjective = AddObjective(objective)
		addObjective.window.set_transient_for(self.window)

		if addObjective.window.run() > 0:
			self.__CreateGraph()

		addObjective.window.destroy()


	def DelObjective(self, menuitem,name):
		if(self.config.Get('deleteCascade')
		and len(self.controller.DirectRequeriments(name))>1):
			dialog = DeleteCascade(name)

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
										_("Do you want to delete the objetive ")+name+"?")
			if dialog.run() == gtk.RESPONSE_YES:
				self.controller.DeleteObjective(name,
												self.config.Get('removeOrphanRequeriments'))
				self.__CreateGraph()
			dialog.destroy()


	def __on_objective_clicked(self, widget,event):
		if(event.button == 3):	# Secondary button
			objective_id = widget.get_label()

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
		if(event.button == 3):		# Secondary button
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


	def IncreaseLineWidth(self, widget,event, objective=None):
		self.__cursorObjective = objective
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
			self.navBar.add_with_id(objective_name, self.__NavbarZoom, objective_name)
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


	def on_Main_window_state_event(self, widget, event):
		self.config.Set("maximized", bool(event.new_window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED))
		self.config.Store()