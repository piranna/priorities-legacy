import cmd
import getopt


class View(cmd.Cmd):
	def __init__(self, controller, input=None):
		self.controller = controller

		if input:
			cmd.Cmd.stdin = input

			# Disable rawinput module use
			use_rawinput = False

			# Do not show a prompt after each command read
			prompt = ''

		else:
			prompt = "Priorities :> "

		self.do_ShowTree(None)

		self.cmdloop()


	# Overwritten functions
	def emptyline(self):
		pass


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

		self.controller.AddObjective(line[0].strip(), quantity, expiration, requeriments)


	def do_ShowTree(self, line):
		for level in self.controller.ShowTree(line):
			level_objectives = []
			for objective in level:
				if objective['alternative']:
					if not objective['priority']:
					#	DrawArrow(objective['objective_id'], objective['alternative'])
						print
					else:
						print

				if objective['objective_id'] not in level_objectives:
#					print "\t"+objective['name'],
					level_objectives.append(objective['objective_id'])

			print


	def do_EOF(self, line):
		print
		return True