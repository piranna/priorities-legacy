class Controller:

	# Constructor
	def __init__(self, model):
		self.__model = model


	def RecursiveRequeriments(self, name=None, export=False):
		"""Get all the requeriments tree of an objective

		If name is not defined return the full objectives tree
		"""

		requeriments = []

		def Priv_RecursiveRequeriments(name,checked=None):
			"""Get all the requeriments tree of an objective storing them inside
			requeriments and returning the current top level
			"""

			def Insert_array_tree_2d(data, index, array, head=False):
				"Append data to the indexed array of arrays"
				while len(array)<=index:
					array.append([])
				if head:
					array[index].insert(0,data)
				else:
					array[index].append(data)

			def GetDepth(name, array):
				"""Get the depth of a name inside an array

				If don't exist, return -1 as error message
				"""
				depth = 0
				for array_level in array:
					for requeriment in array_level:
						if requeriment['name']==name:
							return depth
					depth += 1
				return -1


			# Init top level
			depth=0

			# If objective is not checked
			# set objective as checked
			# and get it's requeriments
			if checked == None:
				checked=[]

			if name not in checked:
				checked.append(name)

				for row in self.__model.Requeriments(name, export=export):

					# If objective has an alternative,
					# get the new depth
					if row['alternative']:

						# If alternative have been checked,
						# get its next level
						if row['alternative'] in checked:
							depth = GetDepth(row['alternative'], requeriments)+1

						# Else check if we have to get it's new level or not
						else:
							r_depth = Priv_RecursiveRequeriments(row['alternative'])
							if  depth < r_depth:
								depth = r_depth

					g_depth = GetDepth(row['name'],requeriments)
					if  depth < g_depth:
						depth = g_depth
					Insert_array_tree_2d(row, depth, requeriments, row['expiration'])

			# Return next top level
			return depth+1


		for row in self.__model.Requeriments(name, export=export):
			Priv_RecursiveRequeriments(row['name'])

		return requeriments


	def AddObjective(self, name, quantity=None, expiration=None, requeriments=None):
		"Add an objective and all it's requeriments to the database"
		print requeriments
		# Add objective or update it's data
		self.__model.AddObjective(name,
								  quantity, expiration)

		# Objective has requeriments
		if requeriments == None:
			requeriments = []
		for requeriment,alternatives in requeriments.items():
			self.__model.AddRequeriment(name, requeriment,
										optional=False)

			# Alternatives
			for priority,(alternative,quantity) in alternatives.items():
				self.__model.AddAlternative(alternative,
											name, requeriment, priority,
											quantity)


	def IsSatisfaced(self, name):
		dependents = self.Dependents(name)
		quantity = self.GetObjective(name)['quantity']

		if dependents:
			if quantity<self.MinQuantity(name):
				# Quantity is less than the minimum required quantity of all
				# dependents, check if all dependents are satisfaced by others
				for dependent in dependents:
					if not self.IsSatisfaced(dependent['objective']):
						return False

			# Quantity is greater than the minimun required quantity of at least
			# one dependent, or all dependents are satisfaced by others
			return True

		# No dependents
		return quantity>0

	def IsAvailable(self, name):
		req_alt = {}
		for requeriment in self.__model.Requeriments(name):
			alternative = requeriment['alternative']

			if requeriment['priority']:
				requeriment = requeriment['requeriment']
				if not req_alt.get(requeriment, False):
					req_alt[requeriment] = self.IsSatisfaced(alternative)

			elif alternative and not self.IsSatisfaced(alternative):
				return False

		for value in req_alt.itervalues():
			if not value:
				return False

		return True

	def IsInprocess(self, name):
		"At least one objective requeriment (but NOT all) is satisfaced"
		for requeriment in self.__model.Requeriments(name):
			if self.IsSatisfaced(requeriment['alternative']):
				return True
		return False


	def Get_DeleteObjective_Tree(self, name):
		"Get the tree of the objectives that are going to be deleted"

		# Checked objectives stack
		checked = []

		def Private_Get_DeleteObjective_Tree(parent):
			def MergeDependents(dependents):
				''' Merge the requeriments that has name as an ancestor
					removing duplicates
				'''
				def IsDescendent(objective):
					''' Check if objective is a descendent of name
						in the requeriments tree
					'''
					if objective==name:
						return True
					for dependent in self.__model.Dependents(objective):
						if(dependent['objective'] == name
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

			for requeriment in self.__model.DirectRequeriments(parent):
				if(requeriment['alternative']
				and requeriment['alternative'] not in checked):
					dependents = self.Dependents(requeriment['alternative'])

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


		return Private_Get_DeleteObjective_Tree(name)


	def Import(self, file):
		try:
			import Parser
			parser = Parser.Parser(self, file)
			parser.cmdloop()
			return True

		except:
			return False

	def Export(self, name=None):
		txt = ""
		obj = None
		req = None
		for level in self.RecursiveRequeriments(name, True):
			for objective in level:
				if(obj and obj!=objective['name']):
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
							obj = objective['name']
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

	def DelObjective(self, name, delete_orphans = False):
		self.__model.DelObjective(name, delete_orphans)

	def DelOrphans(self, requeriments=None):
		self.__model.DelOrphans(requeriments)

	def GetRequeriments(self, name):
		result = {}

		last_requeriment = None
		for requeriment in self.__model.Requeriments(name):
			req = requeriment['requeriment']

			if req != None:
				pri = requeriment['priority']
				alt = requeriment['alternative']
				qua = requeriment['alternative_quantity']

				if last_requeriment != req:
					last_requeriment = req
					result[req] = {}

				result[req][pri] = (alt,qua)

		return result

	def Dependents(self, name):
		return self.__model.Dependents(name)

	def MinQuantity(self, name):
		return self.__model.MinQuantity(name)

	def GetObjective(self, name):
		return self.__model.GetObjective(name)

	def Objectives(self):
		return self.__model.Objectives()

	def UpdateName(self, old, new):
		return self.__model.UpdateName(old, new)