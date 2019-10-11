from collections import OrderedDict


class Controller:

	# Constructor
	def __init__(self, model):
		self.__model = model


	def RecursiveRequeriments(self, name=None, export=False):
		"""Get all the requirements tree of an objective

		If name is None defined return the full objectives tree
		"""

		requeriments = []
		checked = []

		def Priv_RecursiveRequeriments(name):
			"""Get all the requeriments tree of an objective storing them inside
			requeriments and returning the current top level
			"""

			def Insert_array_tree_2d(data, index, array, head=False):
				"Insert data to the indexed array of arrays"
				while len(array)<=index:
					array.append([])
				if head:
					array[index].insert(0,data)
				else:
					array[index].append(data)

			# Init top level
			depth=0

			# If objective is not checked
			# set objective as checked
			# and get it's requeriments
			if name not in checked:
				checked.append(name)
				print name

				for row in self.__model.Requeriments(name, export=export):
					print "\t",row

					# If objective has an alternative,
					# get the new depth
					alternative = row['alternative']
					if alternative:

						# If alternative have been checked,
						# get its next level
						if alternative in checked:
							depth = GetDepth(alternative, requeriments)+1

					# Insert requeriment at the calc level
					g_depth = GetDepth(row['name'],requeriments)
					if  depth < g_depth:
						depth = g_depth
					Insert_array_tree_2d(row, depth, requeriments, row['expiration'])

			# Return next top level
			return depth+1


		for row in self.__model.Requeriments(name, export=export):
			print name,row
			Priv_RecursiveRequeriments(row['name'])

		print
		for level in requeriments:
			print level
		return requeriments


	def GenTree(self, objective=None):
		"""Generate the `objective` requeriments tree

		If `objective` is None then it generates the full objectives
		requeriments tree

		@return: generator of levels
		"""
		levels = []
		pendings = {}

		for name,objective in self.Objectives(objective).items():
			def IsRequeriment(requeriment,objective):
				for alternatives in objective['requeriments']:
					if requeriment in alternatives:
						return True

			level = 0
			dependents = []

			# Calc objective level from it's requeriments and alternatives
			requeriments = objective['requeriments']
			for requeriment,alternatives in enumerate(requeriments):

				if len(alternatives) > 1:
					print name,alternatives
					print "\t",name+":"+str(requeriment)
					print "\t",{'requeriments': alternatives}

				for alternative in alternatives:
					def GetDepth(name, levels):
						"""Get the depth of a name inside an array

						If don't exist, return -1 as error message
						"""
						depth = 0
						for level in levels:
							if name in level:
								return depth
							depth += 1
						return -1

					# Alternative was registered previously,
					# check if it's a mutual requeriment
					# and calc the level of the objective
					depth = GetDepth(alternative, levels)
					if depth >= 0:
#					if depth >= level:

						# Objective is a requeriment of alternative and also
						# it has more requeriments that the alternative, change
						# alternative level and put objective in it's place
						alt = self.Objective(alternative)
						if(IsRequeriment(name,alt)
						and len(alt['requeriments']) < len(requeriments)):
							dependents.append(alternative)

						# Put objective one level below
						else:
							depth += 1

						# Get highest alternatives level
						if level < depth:
							level = depth

					# Alternative was not registered previously,
					# add it to the pending ones
					else:
						if alternative not in pendings:
							pendings[alternative] = []
						pendings[alternative].append(name)

			def MoveDown(objective, level):
				# Add new levels if necessary
				while len(levels) <= level+1:
					levels.append(OrderedDict())

				# Move down objective one level
				levels[level+1][objective] = levels[level].pop(objective)

				# Recursive
				for dep in levels[level+1].keys():
					if IsRequeriment(objective,self.Objective(dep)):
						MoveDown(dep,level+1)

			# If objective has dependencies,
			# move them down and set level to the lower one
			if dependents:
				for l,objectives in enumerate(levels):
					for obj in objectives:
						if obj in dependents:
							MoveDown(obj, l)
							dependents.remove(obj)

							if level > l:
								level = l

			# Objective was pending, move down it's dependencies
			if name in pendings:
				dependents = pendings[name]

				for l,objectives in enumerate(levels):
					for obj in objectives:
						if obj in dependents:
							MoveDown(obj, l)
							dependents.remove(obj)

				del pendings[name]

			# Put objective at it's level
			while len(levels) <= level:
				levels.append(OrderedDict())
			levels[level][name] = objective

		# Sort objectives in every level accord to configuration
		def compare(a,b):
			"""Function to sort the objectives inside a same level"""
			# Expirationobj
#			def Expiration(a,b):
#				if a == None:
#					if b == None:	return 0
#					else:			return b
#				elif b == None:		return a
#				return a - b
#			c = Expiration(a[1]['expiration'],b[1]['expiration'])
			c = cmp(a[1]['expiration'],b[1]['expiration'])
			if c: return c

			# Number of requeriments
			# Lower number of requeriments, or higher number of alternatives
			def NumRequeriments(a,b):
				c = len(a) - len(b)
				if c: return c
				for index in range(len(a)):
					c = len(b[index]) - len(a[index])
					if c: return c
				return 0
			c = NumRequeriments(a[1]['requeriments'],b[1]['requeriments'])
			if c: return c

			# Number of dependencies
			def NumDependencies(objective):
				return len(self.__model.Dependents(objective))
			c = NumDependencies(b[0]) - NumDependencies(a[0])
			if c: return c

			# Alternative quantity
			c = cmp(a[1]['requeriments'],b[1]['requeriments'])
			if c: return c

			# Objectives has the same priority on that level
			return 0

		for level in levels:
			yield OrderedDict(sorted(level.iteritems(), cmp=compare))


	def AddObjective(self, name, quantity=None, expiration=None):
		"Add/update an objective to the database"
		# Add objective or update it's data
		self.__model.AddObjective(name, quantity, expiration)


	def SetRequeriments(self, objective, requeriments):
		"Set an objective requeriments in the database"
		# Delete old requeriments
		self.__model.DelRequeriments(objective)

		# Add new requeriments
		for requeriment,alternatives in enumerate(requeriments):
			self.__model.AddRequeriment(objective, requeriment,
										optional=False)

			# Alternatives
			for priority,(alternative,quantity) in enumerate(alternatives.items()):
				self.__model.AddAlternative(objective, requeriment, priority,
											alternative, quantity)


	def IsSatisfaced(self, name):
		quantity = self.GetObjective(name)['quantity']

		return self.IsAvailable(name) and quantity>0


	def IsAvailable(self, name):
		"All it's requeriments are satisfacted or doesn't have any one"
		for alternatives in self.Requeriments(name):
			for alternative,quantity in alternatives.items():
				if self.GetObjective(alternative)['quantity'] < quantity:
					return False

		return True

	def IsInprocess(self, name):
		"At least one objective requeriment (but NOT all) is satisfaced"
		for alternatives in self.Requeriments(name):
			for alternative,quantity in alternatives.items():
#				if self.IsSatisfaced(requeriment['alternative']):
				if self.GetObjective(alternative)['quantity'] >= quantity:
					return True


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
				if obj and obj!=objective['name']:
					if req:
						txt += ")"
						req=None
					txt += "]\n"
					obj=None
				if req and req!=objective['requeriment']:
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

	def DelObjective(self, objective, delete_orphans = False):
		self.__model.DelObjective(objective, delete_orphans)

	def DelOrphans(self, requeriments):
		self.__model.DelOrphans(requeriments)

	def Objective(self, objective):
		result = None
		last_requeriment = None

		for requeriment in self.__model.Requeriments(objective):
			# Objective
			if result == None:
				result = {'quantity':     requeriment['objective_quantity'],
						  'expiration':   requeriment['expiration'],
						  'requeriments': []}

			# Requeriments and alternatives
			req = requeriment['requeriment']
			alt = requeriment['alternative']
			qua = requeriment['alternative_quantity']

			if req != None and alt != None:
				reqs = result['requeriments']

				if last_requeriment != req:
					last_requeriment = req
					reqs.append(OrderedDict())

				reqs[-1][alt] = qua

		return result

	def Objectives(self, objective=None):
		result = OrderedDict()
		last_requeriment = None

		for requeriment in self.__model.Requeriments(objective):
			# Objective
			name = requeriment['name']

			if name not in result:
				result[name] = {'quantity':     requeriment['objective_quantity'],
								'expiration':   requeriment['expiration'],
								'requeriments': []}
				last_requeriment = None

			# Requeriments and alternatives
			req = requeriment['requeriment']
			alt = requeriment['alternative']
			qua = requeriment['alternative_quantity']

			if req != None and alt != None:
				reqs = result[name]['requeriments']

				if last_requeriment != req:
					last_requeriment = req
					reqs.append(OrderedDict())

				reqs[-1][alt] = qua

		return result

	def Requeriments(self, objective):
		return self.Objective(objective)['requeriments']

	def Dependents(self, objective):
		return self.__model.Dependents(objective)

	def MinQuantity(self, objective):
		return self.__model.MinQuantity(objective)

	def GetObjective(self, objective):
		return self.__model.GetObjective(objective)

	def ObjectivesNames(self):
		return self.__model.ObjectivesNames()

	def UpdateName(self, old, new):
		return self.__model.UpdateName(old, new)
