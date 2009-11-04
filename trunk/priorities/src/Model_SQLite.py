import sqlite3


class Model:
	# Contructor & destructor
	def __init__(self, db_path):
		self.__connection = None

		if db_path:
			self.Connect(db_path)


	def __del__(self):
		self.__Unconnect()


	def Connect(self, db_path):
		"""
		Make a connection to the database
		or create a new one if it's doesn't exists
		"""
		self.__Unconnect()

		self.__connection = sqlite3.connect(db_path)

		self.__connection.row_factory = sqlite3.Row
		self.__connection.isolation_level = None

		try:
			self.__connection.executescript('''
				CREATE TABLE IF NOT EXISTS objectives
				(
					id INTEGER NOT NULL,
					name VARCHAR(32) NOT NULL,
					quantity FLOAT NOT NULL DEFAULT 0,
					expiration timestamp DEFAULT NULL,
					PRIMARY KEY(id)
				);
				CREATE TABLE IF NOT EXISTS requeriments
				(
					objective INTEGER NOT NULL, --FOREIGN KEY objectives ON UPDATE CASCADE ON DESTROY CASCADE
					requeriment INTEGER NOT NULL,
					priority INTEGER NOT NULL DEFAULT 0,
					alternative INTEGER NOT NULL, --FOREIGN KEY objectives ON UPDATE CASCADE ON DESTROY CASCADE
					quantity FLOAT NOT NULL DEFAULT 1,
					PRIMARY KEY(objective,requeriment,priority)
				);
				''')
		except sqlite3.Error, e:
			print _("Exception on 'Model_SQLite.py':"), e.args[0]


	def __Unconnect(self):
		if self.__connection:
			self.__connection.close()
			self.__connection = None


	def Get_Connection(self):
		"Get the current connection"
		return self.__connection


	def Backup(self, db_name):
		"Make a backup of the database in the defined new database file"
		backup = Model(db_name)

		# objectives
		for row in self.__connection.execute("SELECT * FROM objectives"):
			backup.__connection.execute("INSERT INTO objectives(id,name,quantity,expiration) VALUES(?,?,?,?)",
										(row['id'],row['name'],row['quantity'],row['expiration']))

		# requeriments
		for row in self.__connection.execute("SELECT * FROM requeriments"):
			backup.__connection.execute("INSERT INTO requeriments(objective,requeriment,priority,alternative,quantity) VALUES(?,?,?,?,?)",
										(row['objective'],row['requeriment'],row['priority'],row['alternative'],row['quantity']))


	def Get_db_path(self):
		return self.__connection.execute("PRAGMA database_list")[0].split('|')[2]


	def Get_db_version(self):
		return self.__connection.execute("PRAGMA user_cookie")


	def Set_db_version(self, value):
		return self.__connection.execute("PRAGMA user_cookie=?",(value,))


	# Access functions
	def GetObjective(self,objective_id):
		"Get the data of an objective from its objective_id"
		query = self.__connection.execute('''
			SELECT * FROM objectives
			WHERE id == ?
			LIMIT 1
			''',
			(objective_id,))
		query = query.fetchone()
		if query:
			return query
		return None


	def DirectDependencies(self, objective_id=None, requeriment=None, export=False):
		sql = '''
			SELECT objectives.id AS objective_id,objectives.name AS name,objectives.quantity AS objective_quantity,objectives.expiration AS expiration,
					requeriment,priority,alternative,requeriments.quantity AS requeriment_quantity
			'''
		if export:
			sql += ",objectives2.name AS alternative_name"
		sql += '''
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.id=requeriments.objective
			'''
		if export:
			sql += '''
					LEFT OUTER JOIN objectives AS objectives2
						ON requeriments.alternative=objectives2.id
				'''

		if objective_id:
			sql += "WHERE objectives.id=="+str(objective_id)
		if requeriment:
			sql += "AND requeriment=="+str(requeriment)

		sql += " ORDER BY"
		if not export:
			sql += " expiration DESC,"
		sql += " objective_id,requeriment,priority ASC"

		return self.__connection.execute(sql).fetchall()


	def DirectDependents(self, objective_id):
		"Get the dependents of a requeriment"
		return self.__connection.execute('''
			SELECT * FROM requeriments
			WHERE alternative==?
			GROUP BY objective
			''',
			(str(objective_id),)).fetchall()


	def DirectDependents_minQuantity(self,objective_id):
		"Get the min quantity needed by a objective to satisface a requeriment"
		return self.__connection.execute('''
			SELECT MIN(quantity) AS min_quantity FROM requeriments
			WHERE alternative==?
			LIMIT 1
			''',
			(str(objective_id),)).fetchone()['min_quantity']


	def GetId(self, name):
		"Get the id of the objective with the specified name"
		query = self.__connection.execute('''
			SELECT id FROM objectives
			WHERE name==?
			LIMIT 1
			''',
			(name,)).fetchone()

		if query:
			return query['id']
		return None


	def GetName(self, objective_id):
		"Get the name of the objective with the specified id"
		return self.__connection.execute('''
			SELECT name FROM objectives
			WHERE id==?
			LIMIT 1
			''',
			(objective_id,)).fetchone()['name']


	def AddObjective(self, name, quantity=None, expiration="no valid expiration"):
		"Add a new objective"
		# If it's an old objective,
		# update it
		objective_id = self.GetId(name)
		if objective_id:
			# Increase quantity
			if quantity!=None:
				self.__connection.execute('''
					UPDATE objectives
					SET quantity=?
					WHERE id=?
					''',
					(quantity, objective_id))

			# Update expiration
			if expiration!="no valid expiration":
				self.__connection.execute('''
					UPDATE objectives
					SET expiration=?
					WHERE id=?
					''',
					(expiration, objective_id))

			return objective_id

		# If it's not an old objective,
		# create a new one

		# Insert new objective
		if(quantity==None):
			quantity=0

		if(expiration=="no valid expiration"):
			expiration=None

		cursor = self.__connection.cursor()
		cursor.execute('''
			INSERT INTO objectives(name,quantity,expiration)
				VALUES(?,?,?)
			''',
			(name,quantity,expiration))

		# Return objective id
		return cursor.lastrowid


	def AddAlternative(self, alternative, objective, requeriment=None, priority=0, quantity=1):
		# Get first empty requeriment for this objective
		def AddRequeriment(objective):
			query = self.__connection.execute('''
				SELECT DISTINCT requeriment FROM requeriments
				WHERE objective==?
				ORDER BY requeriment
				''',
				(objective,))

			requeriment = 1
			for row in query:
				if row['requeriment'] != requeriment:
					return requeriment
				requeriment += 1
			return requeriment


		alternative = self.AddObjective(alternative)

		# Search for old requeriment id
		for row in self.DirectDependencies(objective):
			if row['alternative']==alternative:
				requeriment = row['requeriment']
				break

		# If there's no old requeriment id,
		# create a new one
		if not requeriment:
			requeriment = AddRequeriment(objective)


		self.__connection.execute('''
			INSERT INTO requeriments(objective,requeriment,priority,alternative,quantity)
				VALUES(?,?,?,?,?)
			''',
			(objective,requeriment,priority,alternative,quantity))

		return requeriment


	def DeleteAlternatives(self, objective_id,parent_id=None):			# Overseed by Foreign Key
		sql = '''
			DELETE FROM requeriments
			WHERE alternative==?
			'''
		bindings = [objective_id]

		if parent_id:
			sql += "AND objective==?"
			bindings.append(parent_id)

			dependency = self.__connection.execute('''
				SELECT * FROM requeriments
				WHERE objective==?
				AND alternative==?
				LIMIT 1
				''',
				(parent_id,objective_id)).fetchone()

		self.__connection.execute(sql,bindings)

		if parent_id:
			self.__UpdateDependencyPriority(self.__Count(dependency['objective'],
														dependency['requeriment']),
											dependency['objective'],
											dependency['requeriment'],
											dependency['priority'])


	def DelRequeriments_ById(self, objective_id):			# Overseed by Foreign Key
		return self.__connection.execute('''
			DELETE FROM requeriments
			WHERE objective==?
			''',
			(objective_id,))


	def DeleteObjective(self, objective_id, delete_orphans = False):
		# Delete requeriments
		if delete_orphans:
			dependencies = self.DirectDependencies(objective_id)
		self.DelRequeriments_ById(objective_id)

		# Get dependents
		dependents = self.DirectDependents(objective_id)

		# Delete alternatives
		self.DeleteAlternatives(objective_id)

		# Re-adjust priorities
		checked = []
		count = None
		for dependent in dependents:

			# If dependency has alternatives
			# update its priority
			if dependent['priority']:
				# If dependency has not been checked
				# get it's number of alternatives
				if dependent['objective'] not in checked:
					checked.append(dependent['objective'])
					count = self.__Count(dependent['objective'],
										dependent['requeriment'])

				self.__UpdateDependencyPriority(count,
												dependent['objective'],
												dependent['requeriment'],
												dependent['priority'])


		# Delete objective
		self.__connection.execute('''
			DELETE FROM objectives
			WHERE id==?
			''',
			(objective_id,))

		if delete_orphans:
			self.DeleteOrphans(dependencies)


	def DeleteOrphans(self, dependencies=None):
		if dependencies:
			for dependency in dependencies:
				# If dependency doesn't have a dependent,
				# delete the orphan
				if(self.GetObjective(dependency['alternative'])
				and not len(self.DirectDependents(dependency['alternative']))):
					self.DeleteObjective(dependency['alternative'], True)


	def __Count(self, objective_id,requeriment):
		"Get the number of alternatives for a objective and requeriment specifieds"
		return self.__connection.execute('''
			SELECT COUNT(*) AS count FROM requeriments
			WHERE objective==?
				AND requeriment==?
			''',
			(objective_id,requeriment)).fetchone()['count']


	def __UpdateDependencyPriority(self, count, objective,requeriment,priority):
		self.__connection.execute('''
			UPDATE requeriments
			SET priority=
				CASE
					WHEN(?>1) THEN
						CASE
							WHEN(priority>?) THEN
								priority-1
							ELSE
								priority
						END
					ELSE
						0
				END
			WHERE objective==?
			AND requeriment==?
			''',
			(count,
			priority,
			objective,
			requeriment))
#		self.__connection.execute('''
#			UPDATE requeriments
#			SET priority=
#				CASE
#					WHEN(?>1 AND priority>?) THEN
#						priority-1
#					WHEN(?>1) THEN
#						priority
#					ELSE
#						0
#				END
#			WHERE objective==?
#			AND requeriment==?
#			''',
#			(count,priority,
#			count,
#			objective,
#			requeriment))

