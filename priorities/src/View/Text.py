import View

import Parser


class TextmodeParser(Parser.Parser):
	def __init__(self, controller, input=None):
		self.__controller = controller

		Parser.Parser.__init__(self, controller,input)


	# Actions
	def do_ShowTree(self, line):
		for level in self.__controller.RecursiveRequirements(line):
			level_objectives = []

			# Alternatives
			for objective in level:
				if objective['requirement']:
					if objective['priority']:
						print "\talternative",objective['alternative']

					else:
					#	DrawArrow(objective['objective_id'], objective['alternative'])
						print "\tarrow",objective['alternative']

			# Objectives
			for objective in level:
				if objective['objective_id'] not in level_objectives:
					print objective['name']+'\t',
					level_objectives.append(objective['objective_id'])

			print


	def do_DirectDependents(self, line):
		for dependent in self.__controller.DirectDependents(line):
			print dependent



class Main(View.View):
	def __init__(self, input=None):
		View.View.__init__(self)

		self.__parser = TextmodeParser(self.controller, input)

		self.__parser.do_ShowTree(None)
		self.__parser.cmdloop()


	def __AskDB(self, database):
		database = raw_input(_("Select the database to use:"))
		if database:
			print database, 'selected'
			self.controller.Connect(database)
		else:
			print 'Closed, no files selected'
			import sys
			sys.exit(0)