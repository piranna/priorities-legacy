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

		self.__connection.executescript('''
			PRAGMA foreign_keys = ON;

			CREATE TABLE IF NOT EXISTS objectives
			(
				name       VARCHAR(32) NOT NULL,
				quantity   FLOAT       NOT NULL DEFAULT 0,
				expiration timestamp   DEFAULT NULL,

				PRIMARY KEY(name)
			);

			CREATE TABLE IF NOT EXISTS requeriments
			(
				objective VARCHAR(32) NOT NULL,
				id        INTEGER     NOT NULL,
				optional  BOOLEAN     NOT NULL DEFAULT false,

				FOREIGN KEY(objective)
					REFERENCES objectives(name)
					ON UPDATE CASCADE ON DELETE CASCADE,

				PRIMARY KEY(objective,id)
			);

			CREATE TABLE IF NOT EXISTS alternatives
			(
				objective   VARCHAR(32) NOT NULL,
				requeriment INTEGER     NOT NULL,
				priority    INTEGER     NOT NULL DEFAULT 0,
				alternative VARCHAR(32) NOT NULL,
				quantity    FLOAT       NOT NULL DEFAULT 1,

				FOREIGN KEY(objective,requeriment)
					REFERENCES requeriments(objective,id)
					ON UPDATE CASCADE ON DELETE CASCADE,

				FOREIGN KEY(alternative)
					REFERENCES objectives(name)
					ON UPDATE CASCADE ON DELETE CASCADE,

				PRIMARY KEY(objective,requeriment,priority)
			);
			''')


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
		backup.__connection.executemany("""INSERT INTO objectives(name, quantity, expiration)
														  VALUES(:name,:quantity,:expiration)""",
										self.__connection.execute("SELECT * FROM objectives"))

		# requeriments
		backup.__connection.executemany("""INSERT INTO requeriments(objective, requeriment, optional)
															VALUES(:objective,:requeriment,:optional)""",
										self.__connection.execute("SELECT * FROM requeriments"))

		# alternatives
		backup.__connection.executemany("""INSERT INTO alternatives(objective, requeriment, priority, alternative, quantity)
															VALUES(:objective,:requeriment,:priority,:alternative,:quantity)""",
										self.__connection.execute("SELECT * FROM alternatives"))


	def Get_db_path(self):
		return self.__connection.execute("PRAGMA database_list")[0].split('|')[2]


	def Get_db_version(self):
		return self.__connection.execute("PRAGMA user_cookie")


	def Set_db_version(self, value):
		return self.__connection.execute("PRAGMA user_cookie=?",(value,))


	# Access functions
	def GetObjective(self,name):
		"Get the data of an objective from its name"
		return self.__connection.execute('''
			SELECT * FROM objectives
			WHERE name == ?
			LIMIT 1
			''',
			(name,)).fetchone()


	def Requeriments(self, objective=None, requeriment=None, export=False):
		sql = '''
			SELECT objectives.name AS name,objectives.quantity AS objective_quantity,objectives.expiration AS expiration,
					requeriments.requeriment AS requeriment,
					priority,alternative,requeriments.quantity AS requeriment_quantity
			'''
		if export:
			sql += ",objectives2.name AS alternative_name"
		sql += '''
			FROM objectives
				LEFT OUTER JOIN requeriments
					ON objectives.name = requeriments.objective
				LEFT OUTER JOIN alternatives
					ON  requeriments.objective   = alternatives.objective
					AND requeriments.requeriment = alternatives.requeriment
			'''
		if export:
			sql += '''
					LEFT OUTER JOIN objectives AS objectives2
						ON alternatives.alternative = objectives2.name
				'''

		if objective:
			sql += "WHERE objectives.name=="+objective
			if requeriment:
				sql += "AND requeriment=="+str(requeriment)

		sql += " ORDER BY "
		if not export:
			sql += "expiration DESC,"
		sql += "name,requeriment,priority ASC"

		return self.__connection.execute(sql).fetchall()


	def Dependents(self, objective):
		"Get the dependents of a requeriment"
		return self.__connection.execute('''
			SELECT * FROM alternatives
			WHERE alternative==:objective
			GROUP BY objective
			''',
			{'objective':objective}).fetchall()


	def MinQuantity(self,objective):
		"Get the min quantity needed by a objective to satisface a requeriment"
		return self.__connection.execute('''
			SELECT MIN(quantity) AS min_quantity FROM alternatives
			WHERE alternative==:objective
			LIMIT 1
			''',
			{'objective':objective}).fetchone()['min_quantity']


	# Adders

	def AddObjective(self, name, quantity=None, expiration="no valid expiration"):
		"Add / update an objective"

		self.__connection.execute('''
			INSERT OR IGNORE INTO objectives(name)
				VALUES(?)
			''',
			(name,))

		# Increase quantity
		if quantity!=None:
			self.__connection.execute('''
				UPDATE objectives
				SET quantity=?
				WHERE name=?
				''',
				(quantity, name))

		# Update expiration
		if expiration!="no valid expiration":
			self.__connection.execute('''
				UPDATE objectives
				SET expiration=?
				WHERE name=?
				''',
				(expiration, name))

	def AddRequeriment(self, objective, id=None, optional=None):
		# Create objective (if needed)
		self.AddObjective(objective)

		# Create new requeriment id if no one was expecified
		if id == None:
			id = self.__connection.execute('''
				SELECT COALESCE(MAX(id)+1,0) AS id
				FROM requeriments
				WHERE objective==:objective
				ORDER BY id
				''',
				{'objective':objective}).fetchone()['id']

		# Create new requeriment
		self.__connection.execute('''
			INSERT OR IGNORE INTO requeriments(objective, id)
									   VALUES(:objective,:id)
			''',
			{'objective':objective, 'id':id})

		# Set optional
		if optional!=None:
			self.__connection.execute('''
				UPDATE requeriments
				SET optional=:optional
				WHERE objective==:objective
				AND id==:id
				''',
				{'objective':objective, 'id':id, 'optional':optional})

	def AddAlternative(self, alternative, objective, requeriment=None, priority=0, quantity=1):
		# Create alternative (if needed)
		self.AddObjective(alternative)

		# Add requeriment to the objective
		self.AddRequeriment(objective, requeriment)

		# Add alternative to the requeriment
		self.__connection.execute('''
			INSERT INTO alternatives(objective,requeriment,priority,alternative,quantity)
				VALUES(?,?,?,?,?)
			''',
			(objective,requeriment,priority,alternative,quantity))


	# Deleters

	def DelObjective(self, name, delete_orphans = False):
		# Get objective requeriments if we want to delete orphan ones
		if delete_orphans:
			requeriments = self.Requeriments(name)

		# Re-adjust priorities
		checked = []
		for dependent in self.Dependents(name):

			# If requeriment has alternatives
			# update its priority
			if dependent['priority']:
				dependent['count'] = 0

				# If requeriment has not been checked
				# get it's number of alternatives
				if dependent['objective'] not in checked:
					checked.append(dependent['objective'])

					# Get the number of alternatives for a objective
					# and requeriment specifics
					dependent['count'] = self.__connection.execute('''
						SELECT COUNT(*) AS count FROM alternatives
						WHERE objective  ==:objective
						  AND requeriment==:requeriment
						''',
						dependent).fetchone()['count']

				# Update alternative priority
				self.__connection.execute('''
					UPDATE alternatives
					SET priority=
						CASE
							WHEN(:count>1) THEN
								CASE
									WHEN(priority>:priority) THEN
										priority-1
									ELSE
										priority
								END
							ELSE
								0
						END
					WHERE objective  ==:objective
					  AND requeriment==:requeriment
					''',
					dependent)


		# Delete objective
		self.__connection.execute('''
			DELETE FROM objectives
			WHERE name==?
			''',
			(name,))

		# Delete orphan requeriments (if any)
		if delete_orphans:
			self.DelOrphans(requeriments)


	def DelOrphans(self, requeriments=None):
		"""Delete the objectives without dependents
		defined in the `requeriments` list
		"""
		if requeriments:
			for requeriment in requeriments:
				# If requeriment doesn't have a dependent,
				# delete the orphan
				if not self.Dependents(requeriment['alternative']):
					self.DelObjective(requeriment['alternative'], True)
	#			if(self.GetObjective(requeriment['alternative'])
	#			and not self.Dependents(requeriment['alternative'])):
	#				self.DelObjective(requeriment['alternative'], True)