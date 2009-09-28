#!/usr/bin/python

import sys

#from optparse import OptionParser


def usage():
	print("usage:",sys.argv[0],
					"[(-d|--database) <database path>]",
					"[(-i|--input) <input file>]",
					"[-t|--textmode]",
					"[-T|--test]",
					"[-A|--askDB]",
					"[-D|--defaultDB]")


def CheckArgs(args):
	try:
		import getopt
		return getopt.getopt(args,
							"d:i:tTAD",
							["database=","input=","textmode","test","askDB","defaultDB"])

	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)



if __name__ == "__main__":

	# Load preferences
	import preferences
	preferences = preferences.Load()

	# Set default vars
	useDefaultDB = preferences['useDefaultDB']
	db = preferences['database']
	textmode = False
	input = None

	# Check arguments
	opts,args = CheckArgs(sys.argv[1:])
#	parser = OptionParser()
#	parser.add_option(None,"--database")

	# Parse arguments
	for o,a in opts:
		if o in ("-d", "--database"):
			db = a
			useDefaultDB = True

		elif o in ("-i", "--input"):
			textmode = True
			input = a

		elif o in ("-t", "--textmode"):
			textmode = True

		elif o in ("-T", "--teat"):
			db = ":memory:"
			useDefaultDB = True

		elif o in ("-A", "--askDB"):
			useDefaultDB = False

		elif o in ("-D", "--defaultDB"):
			useDefaultDB = True

	# Load model
	import Model_SQLite
	model = Model_SQLite.Model(db)

	# Load controller
	import Controller
	controller = Controller.Controller(model)

	# Load view
	if not textmode:
#		try:
			import View_Gtk
			interface = View_Gtk.View(controller, db,useDefaultDB)
#		except: #gtk.GtkWarning, e:
			print
			print "An error has ocurred loading GTK interface"
			print "Loading text mode interface"
			textmode = True

#		import View_Curses
#		interface = View_Curses.View(controller, db,useDefaultDB)

	if textmode:
		import View_Text
		interface = View_Text.View(controller, db,useDefaultDB,input)

