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
				print "\t",row
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

		for dependencie in dependencies:
			print
			for a in dependencie:
				print a
		print

		return dependencies



	# Add an objective and all it's requeriments to the database
	def AddObjective(self, name, quantity=None, expiration=None, requeriments=None):
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

#	def GetObjective_byName(self, objective_name):
#		return self.__model.GetObjective(objective_name)

	def GetObjective_byId(self, objective_id):
		return self.__model.GetObjective(objective_id)

	def DirectDependencies(self, objective_id):
		return self.__model.DirectDependencies(objective_id)

	def DirectDependents(self, objective_id):
		return self.__model.DirectDependents(objective_id)

	def DirectDependents_minQuantity(self, objective_id):
		return self.__model.DirectDependents_minQuantity(objective_id)

	def Connect(self, db_name):
		return self.__model.Connect(db_name)


	def IsSatisfacted(self, objective_id):
		dependents = self.DirectDependents(objective_id)
		quantity = self.GetObjective_byId(objective_id)['quantity']
		if dependents:
			if quantity<self.DirectDependents_minQuantity(objective_id):
				for dependent in dependents:
					if not self.IsSatisfacted(dependent['objective']):
						return False
			return True
		return quantity>0

	def IsAvailable(self, objective_id):
		req_alt = {}
		for requeriment in self.DirectDependencies(objective_id):
			if requeriment['alternative']:
				if requeriment['priority']:
					if not req_alt.get(requeriment['requeriment'], False):
						req_alt[requeriment['requeriment']] = self.IsSatisfacted(requeriment['alternative'])
				elif not self.IsSatisfacted(requeriment['alternative']):
						return False
		for key,value in req_alt.iteritems():
			if not value:
				return False
		return True

	def IsInprocess(self, objective_id):
		for requeriment in self.DirectDependencies(objective_id):
			if self.IsSatisfacted(requeriment['alternative']):
				return True
		return False

	def DelRequeriments(self, objective_name):
		return self.__model.DelRequeriments(objective_name)