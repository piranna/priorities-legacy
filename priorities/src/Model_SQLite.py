import sqlite3


class Model:
	connection = None

	# Contructor & destructor
	def __init__(self, db_name):
		if db_name:
			self.Connect(db_name)


	def __del__(self):
		self.unconnect()


	def Connect(self, db_name):
		self.unconnect()

		self.connection = sqlite3.connect(db_name)

		self.connection.row_factory = sqlite3.Row
		self.connection.isolation_level = None

		try:
			self.connection.executescript('''
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
		if self.connection:
			self.connection.close()
			self.connection = None


	# Access functions
	def GetObjective(self,objective_id):
		query = self.connection.execute('''
			SELECT * FROM objectives
			WHERE objectives.id == ?
			LIMIT 1
			''',
			(objective_id,))
		query = query.fetchone()
		if query:
			return query
		return None


	def DirectDependencies(self, objective_id=None, requeriment=None):
#		sql = '''
#			SELECT objectives.quantity AS objective_quantity,expiration,
		sql = '''
			SELECT objectives.id AS objective_id,name,objectives.quantity AS objective_quantity,expiration,
					requeriment,priority,alternative,requeriments.quantity AS requeriment_quantity
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.id=requeriments.objective
			'''

		if objective_id:
			sql += "WHERE objectives.id=="+str(objective_id)
		if requeriment:
			sql += "AND requeriment=="+str(requeriment)

#		sql += " ORDER BY objective_id,requeriment,priority"
#		sql += " ORDER BY objective,requeriment,priority"
		sql += " ORDER BY expiration DESC, objective_id,requeriment,priority ASC"


		return self.connection.execute(sql)


	def DirectDependents(self, objective_id):
		return self.connection.execute('''
			SELECT * FROM requeriments
			WHERE alternative==?
			GROUP BY objective
			''',
			(str(objective_id),)).fetchall()


	def DirectDependents_minQuantity(self,objective_id):
		query = self.connection.execute('''
			SELECT MIN(quantity) AS min_quantity FROM requeriments
			WHERE alternative==?
			LIMIT 1
			''',
			(str(objective_id),))
		return query.fetchone()['min_quantity']


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


	def AddObjective(self, name, quantity=None, expiration=None):
		# Update old objective
		objective_id = self.GetId(name)

		if objective_id:

			# Increase quantity
			if quantity!=None:
				self.connection.execute('''
					UPDATE objectives
					SET quantity=?
					WHERE id=?
					''',
					(quantity, objective_id))
				print "\t\tQuantity:",quantity

			# Update expiration
			self.connection.execute('''
				UPDATE objectives
				SET expiration=?
				WHERE id=?
				''',
				(expiration, objective_id))

			# Return objective id
			return objective_id

		# Insert new objective
		if(quantity==None):
			quantity=0

		cursor = self.connection.cursor()
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
			query = self.connection.execute('''
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
				LIMIT 1
			''',
			(objective,))
		query = query.fetchone()
		if query:
			return query['name']
		return None


	def DelRequeriments_ById(self, objective_id):
		return self.connection.execute('''
			DELETE FROM requeriments
			WHERE objective==?
			''',
			(objective_id,))


	def DelRequeriments_ByName(self, objective_name):
		return self.DelRequeriments_ById(self.GetId(objective_name))


#	def GetRequeriment(self, objective,alternative):
#		query = self.connection.execute('''
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

		# Delete alternatives
		self.connection.execute('''
			DELETE FROM requeriments
			WHERE alternative==?
			''',
			(objective_id,))

		# Re-adjust priorities
		checked = []
		for dependent in dependents:

			# If dependency has alternatives
			# update its priority
			if dependent['priority']:
				if dependent['objective'] not in checked:
					checked.append(dependent['objective'])

####
					count = self.connection.execute('''
						SELECT COUNT(*) AS count FROM requeriments
						WHERE objective==?
						AND requeriment==?
						''',
						(dependent['objective'],
						dependent['requeriment'])).fetchone()['count']

					print "DeleteObjective:",count,dependent
####

				self.connection.execute('''
					UPDATE requeriments
					SET priority=
						CASE
							WHEN(?>1) THEN
								priority
							ELSE
								0
						END
					WHERE objective==?
					AND requeriment==?
					''',
					(count,
					dependent['objective'],
					dependent['requeriment']))

#						CASE
#							WHEN
#							(
#								SELECT COUNT(*) FROM requeriments
#								WHERE objective==?
#								AND requeriment==?
#								AND priority==?
#							)>1 THEN
#								priority-1
#							ELSE
#								0
#						END

		# Delete objective
		self.connection.execute('''
			DELETE FROM objectives
			WHERE id==?
			''',
			(objective_id,))

