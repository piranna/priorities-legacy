import curses

class View:
	def __init__(self, controller, database,useDefaultDB):
		self.__controller = controller

		if not (database and useDefaultDB):
			self.__AskDB(database)

		self.__window = curses.initscr()
		self.__window.border(0)
		self.__window.addstr(12, 25, "Python curses in action!")
		self.__window.refresh()
		self.__window.getch()

		self.__ShowTree()


	def __del__(self):
		self.__window.endwin()


	def __ShowTree(self):
#		window = curses.newwin(height, width, begin_y, begin_x)

#		window.border(0)
#		window.addstr(12, 25, "Python curses in action!")
#		window.refresh()
#		window.getch()

		pad = curses.newpad(100, 100)
		#  These loops fill the pad with letters; this is
		# explained in the next section
		for y in range(0, 100):
			for x in range(0, 100):
				try:
					pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
				except curses.error:
					pass

		#  Displays a section of the pad in the middle of the screen
		pad.refresh( 0,0, 5,5, 20,75)
