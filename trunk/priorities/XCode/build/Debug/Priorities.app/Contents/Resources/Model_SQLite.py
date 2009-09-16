import sqlite3


class Model:

	# Contructor & destructor
	def __init__(self, db_name):
		self.connection = sqlite3.connect(db_name)

		self.connection.row_factory = sqlite3.Row
		self.connection.isolation_level = None

		try:
			self.connection.executescript('''
				CREATE TABLE objectives
				(
					id INTEGER NOT NULL,
					name VARCHAR(32) NOT NULL,
					quantity FLOAT NOT NULL DEFAULT 0,
					expiration timestamp DEFAULT NULL,
					PRIMARY KEY(id)
				);
				CREATE TABLE requeriments
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


	def __del__(self):
		self.connection.close()



	# Access functions
	def GetObjective(self,objective_id):
		query = self.connection.execute('''
			SELECT * FROM objectives
				WHERE objectives.id == ?
			''',
			(objective_id,))
		query = query.fetchone()
		if query:
			return query
		return None


	def ObjectivesWithoutDependences(self):
		return self.connection.execute('''
			SELECT name,quantity,expiration FROM objectives
				WHERE objectives.id NOT IN
				(
					SELECT DISTINCT objective FROM requeriments
				)
			''')


	def ObjectivesWithDependences(self):
		return self.connection.execute('''
			SELECT name,quantity,expiration,COUNT(*) AS num_dependencies
				FROM objectives,requeriments
				WHERE objectives.id==requeriments.objective
				GROUP BY name
				ORDER BY num_dependencies
			''')


	def ObjectivesWithDependencesNoSatisfacted(self):
		return self.connection.execute('''
			SELECT name FROM objectives,requeriments
				WHERE objectives.id==requeriments.objective
				AND COUNT(
					SELECT * FROM objectives,requeriments
						WHERE objectives.id==requeriments.alternative
				)==0
			''')


	def DirectDependencies(self, objective_id=None):
		sql = '''
			SELECT objectives.id AS objective_id,name,objectives.quantity AS objective_quantity,expiration,
					requeriment,priority,alternative,requeriments.quantity AS requeriment_quantity
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.id=requeriments.objective
			'''

		if objective_id:
			sql += "WHERE objectives.id=="+str(objective_id)

		return self.connection.execute(sql)


	def ObjectivesSatisfacted(self):
		return self.connection.execute('''
			SELECT objectives.id AS objective_id,name,objectives.quantity,expiration
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.id=requeriments.objective
				LEFT OUTER JOIN
				(
					SELECT id,quantity FROM objectives
				) AS objectives2
					ON requeriments.alternative==objectives2.id
			WHERE requeriments.quantity<=objectives2.quantity
				OR requeriments.quantity IS NULL
			GROUP BY objective_id
			ORDER BY expiration,COUNT(*)DESC,objectives.quantity
			''')


	def ObjectivesNoSatisfacted(self):
		return self.connection.execute('''
			SELECT objectives.id AS objective_id,name,objectives.quantity,expiration
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.id=requeriments.objective
				LEFT OUTER JOIN
				(
					SELECT id,quantity FROM objectives
				) AS objectives2
					ON requeriments.alternative==objectives2.id
			WHERE requeriments.quantity>objectives2.quantity
			GROUP BY objective_id
			ORDER BY expiration,COUNT(*)DESC
			''')


	def GetId(self, name):
		query = self.connection.execute('''
			SELECT id FROM objectives
				WHERE name==?
			''',
			(name,))
		query = query.fetchone()
		if query:
			return query['id']
		return None


	def AddObjective(self, name, quantity=0, expiration=None):
		# Update old objective
		objective_id = self.GetId(name)

		if objective_id:

			# Increase quantity
			if quantity:
				self.connection.execute('''
					UPDATE objectives
					SET quantity=quantity+?
					WHERE id==?
					''',
					(quantity, objective_id))

			# Update expiration
			if expiration:
				self.connection.execute('''
					UPDATE objectives
					SET expiration=?
					WHERE (expiration IS NULL
							OR expiration>?)
						AND id==?
					''',
					(expiration, expiration, objective_id))

			# Return objective id
			return objective_id

		# Insert new objective
		cursor = self.connection.cursor()
		cursor.execute('''
			INSERT INTO objectives(name,quantity,expiration)
				VALUES(?,?,?)
			''',
			(name,quantity,expiration))

		# Return objective id
		return cursor.lastrowid


	def AddAlternative(self, alternative, objective, requeriment=None, priority=0, quantity=1):
		def AddRequeriment(objective):
			query = self.connection.execute('''
				SELECT DISTINCT requeriment FROM requeriments
				WHERE objective==?
				ORDER BY requeriment
				''',
				(objective,))

			print

			requeriment = 1
			for row in query:
				print "dentro",row['requeriment'],requeriment
				if row['requeriment'] != requeriment:
					break
				requeriment += 1

			print "fuera",requeriment

			# Return requeriment id
			return requeriment


		alternative = self.self.AddObjective(alternative)

		# Search for old requeriment id
		for row in self.DirectDependencies(objective):
			if row['alternative']==alternative:
				requeriment = row['requeriment']
				break

		# If there's no old requeriment id,
		# create a new one
		if not requeriment:
			requeriment = AddRequeriment(objective)


		self.connection.execute('''
			INSERT INTO requeriments(objective,requeriment,priority,alternative,quantity)
				VALUES(?,?,?,?,?)
			''',
			(objective,requeriment,priority,alternative,quantity))

		print objective,self.GetName(objective),requeriment,priority,alternative,self.GetName(alternative),quantity

		return requeriment


	def GetName(self, objective):
		query = self.connection.execute('''
			SELECT name FROM objectives
				WHERE id==?
			''',
			(objective,))
		query = query.fetchone()
		if query:
			return query['name']
		return None
