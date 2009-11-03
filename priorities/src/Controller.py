class Controller:

	# Constructor
	def __init__(self, model):
		self.__model = model


	# Get all the requeriments tree of an objective.
	# If objective_id is not defined return the all-objectives tree
	def RecursiveDependencies(self, objective_id=None, export=False):

		dependencies = []

		# Get all the requeriments tree of an objective
		# storing them in dependencies and returning the current top level
		def PrivateRecursiveDependencies(objective_id,checked=[]):

			# Append data to the indexed array of array
			def Insert_array_tree_2d(data, index, array, head=False):
				while len(array)<=index:
					array.append([])
				if head:
					array[index].insert(0,data)
				else:
					array[index].append(data)

			# Get the depth of an objective_id inside an array
			# If not, return the array length
			def GetDepth(objective_id, array):
				depth = 0
				for array_level in array:
					for dependency in array_level:
						if dependency['objective_id']==objective_id:
							return depth
					depth += 1
				return -1


			# Init top level
			depth=0

			# If objective is not checked
			# set objective as checked
			# and get it's dependencies
			if objective_id not in checked:
				checked.append(objective_id)

				for row in self.__model.DirectDependencies(objective_id, export=export):

					# If objective has an alternative,
					# get the new depth
					if row['alternative']:

						# If alternative have been checked,
						# get its next level
						if row['alternative'] in checked:
							depth = GetDepth(row['alternative'], dependencies)+1

						# Else check if we have to get it's new level or not
						else:
							r_depth = PrivateRecursiveDependencies(row['alternative'])
							if r_depth >= depth:
								depth = r_depth

					g_depth = GetDepth(row['objective_id'],dependencies)
					if g_depth > depth:
						depth = g_depth
					Insert_array_tree_2d(row, depth, dependencies, row['expiration'])

			# Return next top level
			return depth+1


		for row in self.__model.DirectDependencies(objective_id, export=export):
			PrivateRecursiveDependencies(row['objective_id'])

###
#		for level in dependencies:
#			for dependency in level:
#				print dependency
#			print
###

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
		for requeriment in self.__model.DirectDependencies(objective_id):
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
		for requeriment in self.__model.DirectDependencies(objective_id):
			if self.IsSatisfacted(requeriment['alternative']):
				return True
		return False


	def Get_DeleteObjective_Tree(self, objective_id):
		"Get the tree of the objectives that are going to be deleted"

		# Checked objectives stack
		checked = []

		def Private_Get_DeleteObjective_Tree(parent):
			def MergeDependents(dependents):
				''' Merge the dependencies that has objective_id as an ancestor
					removing duplicates
				'''
				def IsDescendent(objective):
					''' Check if objective is a descendent of objective_id
						in the requeriments tree
					'''
					if objective==objective_id:
						return True
					for dependent in self.__model.DirectDependents(objective):
						if(dependent['objective'] == objective_id
						or IsDescendent(dependent['objective'])):
							return True
					return False

				# [To-Do] It seems it's called twice when has several dependent
				# that are from the same requeriment

				ancestors = []

				for index in range(0, len(dependents)):
					if(IsDescendent(dependents[index]['objective'])):
						ancestors.append(index)

				# Remove merged dependents
				ancestors.reverse()
				for index in ancestors:
					dependents.pop(index)


			# Increment checked objectives stack
			# and init subtree
			checked.append(parent)
			tree = {}

			for requeriment in self.__model.DirectDependencies(parent):
				if(requeriment['alternative']
				and requeriment['alternative'] not in checked):
					dependents = self.DirectDependents(requeriment['alternative'])

					# If objective has several dependents
					# merge the ones that are requeriments of the objetive to delete
					if len(dependents) >= 2:
						MergeDependents(dependents)

					# If objective doesn't have several dependents
					# include it as deletable
					if len(dependents) < 2:
						tree[requeriment['alternative']] = Private_Get_DeleteObjective_Tree(requeriment['alternative'])

			# Decrement checked objectives stack
			# and return subtree
			checked.pop()
			return tree


		return Private_Get_DeleteObjective_Tree(objective_id)


	def Import(self, file):
		try:
			import Parser
			parser = Parser.Parser(self, file)
			parser.cmdloop()
			return True

		except:
			return False

	def Export(self, objective_id=None):
		txt = ""
		obj = None
		req = None
		for level in self.RecursiveDependencies(objective_id, True):
			for objective in level:
				if(obj and obj!=objective['objective_id']):
					if req:
						txt += ")"
						req=None
					txt += "]\n"
					obj=None
				if(req and req!=objective['requeriment']):
					txt += ")"
					req=None

				if not obj:
					txt += "AddObjective '''"+objective['name']+"'''"

					# Quantity
					if objective['objective_quantity']:
						txt += " -c"+str(objective['objective_quantity'])

					# Expiration
					if objective['expiration']:
						txt += " -e'''"+objective['expiration']+"'''"

				# Alternative
				if objective['alternative_name']:
					if obj:
						txt += ","
					else:
						txt += " [("

					txt += "'''"+objective['alternative_name']
					if objective['requeriment_quantity']:
						txt += ":"+str(objective['requeriment_quantity'])
					txt += "'''"

					if not req:
						if objective['priority']:
							obj = objective['objective_id']
							req = objective['requeriment']
						else:
							txt += ",)]\n"
				else:
					txt += "\n"
		if req:
			txt += ")]\n"

		return txt


	"Interface functions"
	def Backup(self, db_name):
		return self.__model.Backup(db_name)

	def Connect(self, db_name):
		return self.__model.Connect(db_name)

	def Get_Connection(self):
		return self.__model.Get_Connection()

	def DelAlternatives(self, objective_id,parent_id):
		return self.__model.DeleteAlternatives(objective_id, parent_id)

	def DelRequeriments_ById(self, objective_id):
		return self.__model.DelRequeriments_ById(objective_id)

	def DeleteObjective(self, objective_id, delete_orphans = False):
		self.__model.DeleteObjective(objective_id, delete_orphans)

	def DeleteOrphans(self, dependencies=None):
		self.__model.DeleteOrphans(dependencies)

	def DirectDependencies(self, objective_id):
		return self.__model.DirectDependencies(objective_id)

	def DirectDependents(self, objective_id):
		return self.__model.DirectDependents(objective_id)

	def DirectDependents_minQuantity(self, objective_id):
		return self.__model.DirectDependents_minQuantity(objective_id)

	def GetId(self, objective_name):
		return self.__model.GetId(objective_name)

	def GetName(self, objective_id):
		return self.__model.GetName(objective_id)

	def GetObjective_byId(self, objective_id):
		return self.__model.GetObjective(objective_id)