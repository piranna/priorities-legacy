#!/usr/bin/python


config_path = "~/.priorities"


def ParseArguments(config):
	# Parser
	import optparse
	parser = optparse.OptionParser(version="0.8")

	# Defaults
	if config.Get('useDefaultDB'):
		default_database=config.Get('database')
	else:
		default_database=None

	parser.set_defaults(database=default_database,
						textmode=False)

	# Options

	# Database
	parser.add_option('--database',				help="Database to use",
						dest="database",
						action="store")
	parser.add_option('--in-memory-database',	help="Use a temporal, in RAM memory database",
						dest="database",
						action="store_const",
						const=":memory:")
	parser.add_option('--use-default-database',	help="Force use of config file default database",
						dest="database",
						action="store_const",
						const=config.Get('database'))
	parser.add_option('--ask-database',			help="Force ask the database to use",
						dest="database",
						action="store_const",
						const=None)

	# Import file
	parser.add_option('--import-file',			help="Parse data from script file",
						dest="importFile",
						action="store")

	# User interface
	parser.add_option('--textmode',				help="Use textmode",
						dest="textmode",
						action="store_true")
	parser.add_option('--gui',					help="Use gui (default)",
						dest="textmode",
						action="store_false")

	# Return parsed arguments
	return parser.parse_args()



if __name__ == "__main__":

	# Load config
	import Config
	config = Config.Config(config_path)

	# Parse arguments
	options, remainder = ParseArguments(config)

	# Load model
	import Model_SQLite
	model = Model_SQLite.Model(options.database)

	# Load controller
	import Controller
	controller = Controller.Controller(model)

	# Load view
	import View
	View.View.controller = controller
	View.View.config = config

	def TextMode():
		import View_Text
		View_Text.Main(options.importFile)

	def Gtk():
		import View_Gtk_Main
		View_Gtk_Main.Main(options.importFile)

	if options.textmode:
		TextMode()
	else:
		try:
			Gtk()
		except: #gtk.GtkWarning, e:
#		except ImportError:
			print
			print "An error has ocurred loading GTK interface"
			print "Loading text mode interface"
			TextMode()

