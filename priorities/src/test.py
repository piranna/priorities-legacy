#!/usr/bin/python

class Test:
	def __init__(self, controller):
		self.controller = controller



	def InsertTestData(self):
		self.controller.model.connection.executemany('''
			INSERT INTO objectives(name,quantity)
				VALUES(?,?)
			''',
			[
				('Dinero',10000),
				('Trabajo',0),
				('Loteria',0),
				('Universidad',0),
				('Coche',0),
				('Carnet',1)
			])
		self.controller.model.connection.executemany('''
			INSERT INTO requirements(objective)
				VALUES(?)
			''',
			[
				(1,),
				(2,),
				(5,),
				(5,),
				(6,)
			])
		self.controller.model.connection.executemany('''
			INSERT INTO alternatives(requirement,priority,alternative,quantity)
				VALUES(?,?,?,?)
			''',
			[
				(1,1,2,1),
				(1,2,3,1),
				(2,0,4,1),
				(3,0,1,10000),
				(4,0,6,1),
				(5,0,1,300)
			])


	def InsertTestData2(self):
		self.controller.AddObjective('Dinero', 10000, None, [('Trabajo', 'Loteria')])
		self.controller.AddObjective('Trabajo', 0, None, [('Universidad',)])
		self.controller.AddObjective('Loteria')
		self.controller.AddObjective('Universidad')
		self.controller.AddObjective('Coche', 0, None, [('Dinero:10000',), ('Carnet',)])
		self.controller.AddObjective('Carnet', 1, None, [('Dinero:300',)])



	def ShowTestResults(self):
#		print "ObjectivesWithoutDependences"
#		for objective in self.controller.ObjectivesWithoutDependences():
#			print objective
#
#		print ""
#
#		print "ObjectivesWithDependences"
#		for objective in self.controller.ObjectivesWithDependences():
#			print objective
#
#		print ""
#
#		print "ObjectivesWithDependencesNoSatisfacted"
#		for objective in self.controller.ObjectivesWithDependencesNoSatisfacted():
#			print objective

		print ""

		print "DirectRequirements"
		for objective in self.controller.DirectRequirements():
			print objective

		print ""

		print "DirectRequirements Coche"
		for objective in self.controller.DirectRequirements(7):
			print objective

		print ""

		print "RecursiveRequirements Coche"
		for objective in self.controller.RecursiveRequirements(7):
			print objective

		print ""

		print "RecursiveRequirements"
		for objective in self.controller.RecursiveRequirements():
			print objective

		print ""

		print "ObjectivesSatisfacted"
		for objective in self.controller.ObjectivesSatisfacted():
			print objective

		print ""

#		print "ObjectivesNoSatisfacted"
#		for objective in self.controller.ObjectivesNoSatisfacted():
#			print objective
#
#		print ""

		for level in self.controller.RecursiveRequirements():
			level_objectives = []
			for objective in level:
				if objective['alternative']:
				#	DrawArrow(objective['objective_id'], objective['alternative'])
					print

				if objective['objective_id'] not in level_objectives:
					print "\t"+objective['name'],
					level_objectives.append(objective['objective_id'])

			print


if __name__ == "__main__":
	import Model_SQLite
#	model = Model_SQLite.Model(":memory:")
	model = Model_SQLite.Model("priorities.sqlite")

	import Controller
	controller = Controller.Controller(model)

	interface = Test(controller)
#	interface.InsertTestData()
#	interface.InsertTestData2()
	interface.ShowTestResults()



#	import Tkinter
#	from Tkconstants import *
#	tk = Tkinter.Tk()
#	frame = Tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
#	frame.pack(fill=BOTH,expand=1)
#	label = Tkinter.Label(frame, text="Hello, World")
#	label.pack(fill=X, expand=1)
#	button = Tkinter.Button(frame,text="Exit",command=tk.destroy)
#	button.pack(side=BOTTOM)
#	tk.mainloop()
