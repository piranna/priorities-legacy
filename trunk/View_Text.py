import cmd
import getopt


class View(cmd.Cmd):
	__input = None

	def __init__(self, controller, database,useDefaultDB, input=None,comment_char='#'):
		self.__controller = controller
		self.__comment_char = comment_char

		if not (database and useDefaultDB):
			self.__AskDB(database)

		if input:
			# Parent
			self.__input = open(input, 'rt')
			cmd.Cmd.__init__(self, stdin=self.__input)

			# Disable rawinput module use
			self.use_rawinput = False

			# Do not show a prompt after each command read
			self.prompt = ''

		else:
			# Parent
			cmd.Cmd.__init__(self)

			# Set prompt
			self.prompt = "Priorities :> "

		self.do_ShowTree(None)

		self.cmdloop()


	def __del__(self):
		if self.__input:
			self.__input.close()


	def __AskDB(self, database):
		database = raw_input("Seleccione la base de datos a usar:")
		if database:
			print database, 'selected'
			self.__controller.Connect(database)
		else:
			print 'Closed, no files selected'
			import sys
			sys.exit(0)


	# Overwritten functions
	def emptyline(self):
		pass


	def precmd(self,line):
		return line.split(self.__comment_char)[0]


	# Actions
	def do_AddObjective(self, line):
		quantity = 0
		expiration = None
		requeriments = ""

		line = line.split()

		for option in line[1:]:
			if option[:2]=="-c":
				quantity=option[2:]
			elif option[:2]=="-e":
				expiration=option[2:]
			else:
				requeriments += option.strip()

		if requeriments:
			requeriments = eval(requeriments)

		self.__controller.AddObjective(line[0].strip(), quantity, expiration, requeriments)


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


	def do_EOF(self, line):
		print
		return True
