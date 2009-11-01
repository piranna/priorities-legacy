#!/usr/bin/python


config_path = "~/.priorities"


import gettext
gettext.textdomain("priorities")
_ = gettext.gettext


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
	group = optparse.OptionGroup(parser,_("Database options"))
	group.add_option('--database',				help=_("Database to use"),
						dest="database",
						action="store")
	group.add_option('--in-memory-database',	help=_("Use a temporal, in RAM memory database"),
						dest="database",
						action="store_const",
						const=":memory:")
	group.add_option('--config-file-database',	help=_("Use database defined in config file (default)"),
						dest="database",
						action="store_const",
						const=config.Get('database'))
	group.add_option('--ask-database',			help=_("Ask the database to use"),
						dest="database",
						action="store_const",
						const=None)
	parser.add_option_group(group)

	# Import file
	group = optparse.OptionGroup(parser,_("Import file option"))
	group.add_option('--import-file',			help=_("Parse data from script file"),
						dest="importFile",
						action="store")
	parser.add_option_group(group)

	# User interface
	group = optparse.OptionGroup(parser,_("User interface options"))
	group.add_option('--textmode',				help=_("Use textmode"),
						dest="textmode",
						action="store_true")
	group.add_option('--gui',					help=_("Use gui (default)"),
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
#			try:
				Gtk()
#			except(gtk.GtkWarning,ImportError):
#				print
#				print _("An undefined error has ocurred loading GTK interface")
#				print _("Loading text mode interface")
#				TextMode()
	except KeyboardInterrupt:
		pass

