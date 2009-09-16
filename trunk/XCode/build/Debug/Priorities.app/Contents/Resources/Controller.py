class Controller:

	# Constructor
	def __init__(self, model):
#	def __init__(self, model, preferences):
		self.__model = model


	# Get all the requeriments tree of an objective.
	# If objective_id is not defined return the all objectives tree
	def RecursiveDependencies(self, objective_id=None):
		def PrivateRecursiveDependencies(objective_id, dependencies, checked=[]):
			def GetDepth(objective_id, dependencies):
				depth = 0
				for level in dependencies:
					for dependency in level:
						if dependency['objective_id']==objective_id:
							return depth
					depth += 1
				return depth


			def Insert_array_tree_2d(data, depth, requeriments):
				while len(requeriments)<=depth:
					requeriments.append([])
				requeriments[depth].append(data)


			def SetDepth(depth, objective_id, dependencies):
				level = 0
				for dependency_level in dependencies:
					if level != depth:
						index = 0
						for dependency in dependency_level:
							if dependency['objective_id']==objective_id:
								Insert_array_tree_2d(dependency_level.pop(index), depth, dependencies)
							index += 1
					level += 1


			depth=0

			checked.append(objective_id)

			for row in self.__model.DirectDependencies(objective_id):
				if row['alternative']:
					if row['alternative'] in checked:
						depth = GetDepth(row['alternative'], dependencies)+1

					else:
						r_depth = PrivateRecursiveDependencies(row['alternative'], dependencies, checked)
						if r_depth > depth:
							depth = r_depth

				SetDepth(depth, row['objective_id'], dependencies)
				Insert_array_tree_2d(row, depth, dependencies)

			return depth+1


		dependencies = []
		checked = []

		for row in self.__model.DirectDependencies(objective_id):
			if row['objective_id'] not in checked:
				PrivateRecursiveDependencies(row['objective_id'], dependencies, checked)

		return dependencies



	# Add an objective and all it's requeriments to the database
	def AddObjective(self, name, quantity=0, expiration=None, requeriments=None):
		# Add objective or update it's data
		objective_id = self.__model.AddObjective(name, quantity, expiration)

		# Objective has requeriments
		if requeriments:
			for requeriment in requeriments:
				# Alternatives
				requeriment_id = None
				priority=0
				for alternative in requeriment:

					# Alternative necesary quantity
					alternative = alternative.split(':')

					quantity = 1
					if len(alternative)>1:
						quantity = alternative[1]

					# Alternative priority
					if len(requeriment)>1:
						priority += 1

					# Insert alternative
					requeriment_id = self.__model.AddAlternative(alternative[0], objective_id, requeriment_id, priority, quantity)


	def ShowTree(self, objective=None):
		# Get id of the objective
		if objective:
			objective = self.__model.GetId(objective)

			# If objective is not registered,
			# return none
			if not objective:
				return None

		return self.RecursiveDependencies(objective)


	def GetName(self, objective_id):
		return self.__model.GetName(objective_id)

	def GetId(self, objective_name):
		return self.__model.GetId(objective_name)

	def DirectDependencies(self, objective_id=None):
		return self.__model.DirectDependencies(objective_id)

	def ObjectivesSatisfacted(self):
		return self.__model.ObjectivesSatisfacted()

#	def GetObjective_byName(self, objective_name):
#		return self.__model.GetObjective(objective_name)

	def GetObjective_byId(self, objective_id):
		return self.__model.GetObjective(objective_id)
