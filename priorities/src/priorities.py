#!/usr/bin/python


config_path = "~/.priorities"


def ParseArguments(config):
	# Parser
	import optparse
	parser = optparse.OptionParser(version="0.9")

	# Defaults
	if config.Get('useDefaultDB'):
		default_database=config.Get('database')
	else:
		default_database=None

	parser.set_defaults(database=default_database,
						textmode=False)

	# Options

	# Database
	group = optparse.OptionGroup(parser,"Database options")
	group.add_option('--database',				help="Database to use",
						dest="database",
						action="store")
	group.add_option('--in-memory-database',	help="Use a temporal, in RAM memory database",
						dest="database",
						action="store_const",
						const=":memory:")
	group.add_option('--use-default-database',	help="Force use of config file default database",
						dest="database",
						action="store_const",
						const=config.Get('database'))
	group.add_option('--ask-database',			help="Force ask the database to use",
						dest="database",
						action="store_const",
						const=None)
	parser.add_option_group(group)

	# Import file
	group = optparse.OptionGroup(parser,"Import file option")
	group.add_option('--import-file',			help="Parse data from script file",
						dest="importFile",
						action="store")
	parser.add_option_group(group)

	# User interface
	group = optparse.OptionGroup(parser,"User interface options")
	group.add_option('--textmode',				help="Use textmode",
						dest="textmode",
						action="store_true")
	group.add_option('--gui',					help="Use gui (default)",
						dest="textmode",
						action="store_false")
	parser.add_option_group(group)

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

	try:
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
	except KeyboardInterrupt:
		pass

