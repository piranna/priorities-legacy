import View

import Parser


class TextmodeParser(Parser.Parser):
	def __init__(self, controller, input=None):
		Parser.Parser.__init__(controller, input):


	# Actions
	def do_ShowTree(self, line):
		for level in self.__controller.ShowTree(line):
			level_objectives = []

			# Alternatives
			for objective in level:
				if objective['requeriment']:
					if objective['priority']:
						print "\talternative",self.__controller.GetName(objective['alternative'])

					else:
					#	DrawArrow(objective['objective_id'], objective['alternative'])
						print "\tarrow",self.__controller.GetName(objective['alternative'])

			# Objectives
			for objective in level:
				if objective['objective_id'] not in level_objectives:
					print objective['name']+'\t',
					level_objectives.append(objective['objective_id'])

			print


	def do_DirectDependents(self, line):
		try:
			int(line)
		except:
			line = self.__controller.GetId(line)

		for dependent in self.__controller.DirectDependents(line):
			print dependent



class View(View.View):
	def __init__(self, database,useDefaultDB, input=None):
		if not (database and useDefaultDB):
			self.__AskDB(database)

		if input:
			self.__parser = TextmodeParser(stdin=open(input, 'rt'))
		else:
			self.__parser = TextmodeParser()

		self.__parser.do_ShowTree(None)
		self.__parser.cmdloop()


	def __AskDB(self, database):
		database = raw_input("Seleccione la base de datos a usar:")
		if database:
			print database, 'selected'
			self.controller.Connect(database)
		else:
			print 'Closed, no files selected'
			import sys
			sys.exit(0)

