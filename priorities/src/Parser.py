import cmd


class Parser(cmd.Cmd):
	def __init__(self, controller, input=None,comment_char='#'):
		self.__controller = controller
		self.__input = None
		self.__comment_char = comment_char

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


	def __del__(self):
		if self.__input:
			self.__input.close()


	# Overwritten functions
	def emptyline(self):
		pass


	def precmd(self,line):
		return line.split(self.__comment_char)[0]


	# Actions
	def do_AddObjective(self, line):
		# Objective
		if line[0:2]=="'''":
			line = line[3:].split("'''",1)
		elif line[0:2]=='"""':
			line = line[3:].split('"""',1)
		elif line[0]=="'":
			line = line[1:].split("'",1)
		elif line[0]=='"':
			line = line[1:].split('"',1)
		else:
			line = line.split(None,1)

		objective = line[0].strip()
		quantity = 0
		expiration = None
		requeriments = []

		if len(line)>1:
			# Requeriments
			line = line[1].split('[',1)
			if len(line)>1:
				requeriments = eval('['+line[1].strip())

			# Options
			for option in line[0].split():
				if option[:2]=="-c":
					quantity=option[2:]
				elif option[:2]=="-e":
					expiration=option[2:]

		self.__controller.AddObjective(objective, quantity, expiration, requeriments)

