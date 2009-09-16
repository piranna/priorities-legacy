#!/usr/bin/python

import sys


def usage():
	print "usage:",sys.argv[0],"[-t|--textmode]"


if __name__ == "__main__":

	# Check args
	try:
		import getopt
		opts,args = getopt.getopt(sys.argv[1:], "i:t", ["input=","textmode"])

	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

#	import preferences
#	preferences = preferences.Load()

	textmode = False
	input = None

	for o,a in opts:
		if o in ("-i", "--input"):
			textmode = True
			input = a
		elif o in ("-t", "--textmode"):
			textmode = True

	# Load model
	import Model_SQLite
#	model = Model_SQLite.Model(":memory:")
	model = Model_SQLite.Model("priorities.sqlite")
#	model = Model_SQLite.Model(preferences['default_db'])

	# Load controller
	import Controller
	controller = Controller.Controller(model)

	# Load view
	if not textmode:
#		try:
		import View_Gtk
		interface = View_Gtk.View(controller)
#		except gtk.GtkWarning, e:
#			print "Loading text mode interface"
#			textmode = True

	if textmode:
		import View_Text
		if input:
			input = open(input, 'rt')

			try:
				interface = View_Text.View(controller,stdin=input)

			finally:
				input.close()

		else:
			interface = View_Text.View(controller)
