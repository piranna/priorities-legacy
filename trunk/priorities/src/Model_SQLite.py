import sqlite3


class Model:
	# Contructor & destructor
	def __init__(self, db_name):
		self.__connection = None

		if db_name:
			self.Connect(db_name)


	def __del__(self):
		self.unconnect()


	def Connect(self, db_name):
		self.unconnect()

		self.__connection = sqlite3.connect(db_name)

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
					objective INTEGER NOT NULL,
					requeriment INTEGER NOT NULL,
					priority INTEGER NOT NULL DEFAULT 0,
					alternative INTEGER NOT NULL,
					quantity FLOAT NOT NULL DEFAULT 1,
					PRIMARY KEY(objective,requeriment,priority)
				);
				''')
		except sqlite3.Error, e:
			print "Exception on 'Model_SQLite.py':", e.args[0]


	def unconnect(self):
		if self.__connection:
			self.__connection.close()
			self.__connection = None


	# Access functions
	def GetObjective(self,objective_id):
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

#		print "sql=",sql

		return self.__connection.execute(sql).fetchall()


	def DirectDependents(self, objective_id):
		return self.__connection.execute('''
			SELECT * FROM requeriments
			WHERE alternative==?
			GROUP BY objective
			''',
			(str(objective_id),)).fetchall()


	def DirectDependents_minQuantity(self,objective_id):
		query = self.__connection.execute('''
			SELECT MIN(quantity) AS min_quantity FROM requeriments
			WHERE alternative==?
			LIMIT 1
			''',
			(str(objective_id),))
		return query.fetchone()['min_quantity']


	def GetId(self, name):
		query = self.__connection.execute('''
			SELECT id FROM objectives
				WHERE name==?
				LIMIT 1
			''',
			(name,))
		query = query.fetchone()
		if query:
			return query['id']
		return None


	def AddObjective(self, name, quantity=None, expiration="no valid expiration"):
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
				print "\t\tQuantity:",quantity

			# Update expiration
			if expiration!="no valid expiration":
				self.__connection.execute('''
					UPDATE objectives
					SET expiration=?
					WHERE id=?
					''',
					(expiration, objective_id))

			# Return objective id
			return objective_id

		# If it's not an old objective,
		# create a new one

		# Insert new objective
		if(quantity==None):
			quantity=0

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

#			print

			requeriment = 1
			for row in query:
#				print "dentro",row['requeriment'],requeriment
				if row['requeriment'] != requeriment:
					break
				requeriment += 1

#			print "fuera",requeriment

			# Return requeriment id
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

		print objective,self.GetName(objective),requeriment,priority,alternative,self.GetName(alternative),quantity

		return requeriment


	def GetName(self, objective):
		query = self.__connection.execute('''
			SELECT name FROM objectives
				WHERE id==?
				LIMIT 1
			''',
			(objective,))
		query = query.fetchone()
		if query:
			return query['name']
		return None


	def DelRequeriments_ById(self, objective_id):
		return self.__connection.execute('''
			DELETE FROM requeriments
			WHERE objective==?
			''',
			(objective_id,))


	def DelRequeriments_ByName(self, objective_name):
		return self.DelRequeriments_ById(self.GetId(objective_name))


#	def GetRequeriment(self, objective,alternative):
#		query = self.__connection.execute('''
#			SELECT requeriment FROM requeriments
#			WHERE objective==?
#			AND alternative==?
#			LIMIT 1
#			''',
#			(objective,alternative))
#		query = query.fetchone()
#		if query:
#			return query['requeriment']
#		return None


	def DeleteObjective(self, objective_id):
		# Delete requeriment
		self.DelRequeriments_ById(objective_id)

		# Get dependents
		dependents = self.DirectDependents(objective_id)

#		print "\ndependents 1:",dependents

		# Delete alternatives
		self.__connection.execute('''
			DELETE FROM requeriments
			WHERE alternative==?
			''',
			(objective_id,))

#		print "\ndependents 2:",self.DirectDependents(objective_id)

		# Re-adjust priorities
		checked = []
		for dependent in dependents:

			# If dependency has alternatives
			# update its priority
			if dependent['priority']:
				if dependent['objective'] not in checked:
					checked.append(dependent['objective'])

					count = self.__connection.execute('''
						SELECT COUNT(*) AS count FROM requeriments
						WHERE objective==?
						AND requeriment==?
						''',
						(dependent['objective'],
						dependent['requeriment'])).fetchone()['count']

				self.__connection.execute('''
					UPDATE requeriments
					SET priority=
						CASE
							WHEN(?>1 AND priority>?) THEN
								priority-1
							WHEN(?>1) THEN
								priority
							ELSE
								0
						END
					WHERE objective==?
					AND requeriment==?
					''',
					(count,
					dependent['priority'],
					count,
					dependent['objective'],
					dependent['requeriment']))


#		print "\ndependents 3:",self.DirectDependents(objective_id)

		# Delete objective
		self.__connection.execute('''
			DELETE FROM objectives
			WHERE id==?
			''',
			(objective_id,))

#		print "\ndependents 4:",self.DirectDependents(objective_id)

