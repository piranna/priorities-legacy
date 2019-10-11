class DB:
	# Contructor & destructor
	def __init__(self, connection):
		self.__connection = connection
		self.__connection.isolation_level = None

		self.create()

	def __del__(self):
		self.__connection.close()


	def create(self):
		"""
		Make a connection to the database
		or create a new one if it's doesn't exists
		"""
		self.__connection.executescript('''
			PRAGMA foreign_keys = ON;

			CREATE TABLE IF NOT EXISTS objectives
			(
				name       VARCHAR(32) NOT NULL,
				quantity   FLOAT       NOT NULL DEFAULT 0,
				expiration timestamp   DEFAULT NULL,

				PRIMARY KEY(name)
			);

			CREATE TABLE IF NOT EXISTS requirements
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
				requirement INTEGER     NOT NULL,
				priority    INTEGER     NOT NULL DEFAULT 0,
				alternative VARCHAR(32) NOT NULL,
				quantity    FLOAT       NOT NULL DEFAULT 1,

				FOREIGN KEY(objective,requirement)
					REFERENCES requirements(objective,id)
					ON UPDATE CASCADE ON DELETE CASCADE,

				FOREIGN KEY(alternative)
					REFERENCES objectives(name)
					ON UPDATE CASCADE ON DELETE CASCADE,

				PRIMARY KEY(objective,requirement,priority)
			);
			''')


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

		# requirements
		backup.__connection.executemany("""INSERT INTO requirements(objective, requirement, optional)
															VALUES(:objective,:requirement,:optional)""",
										self.__connection.execute("SELECT * FROM requirements"))

		# alternatives
		backup.__connection.executemany("""INSERT INTO alternatives(objective, requirement, priority, alternative, quantity)
															VALUES(:objective,:requirement,:priority,:alternative,:quantity)""",
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

	def ObjectivesNames(self):
		"Get all the objectives name"
		return [objective['name'] for objective in self.__connection.execute('''
													SELECT name FROM objectives
													ORDER BY name
													''')]


	def Requirements(self, objective=None, requirement=None, export=False):
		sql = '''
			SELECT objectives.name AS name,objectives.quantity AS objective_quantity,objectives.expiration AS expiration,
					requirements.id AS requirement,
					priority,alternative,alternatives.quantity AS alternative_quantity
			'''
		if export:
			sql += ",objectives2.name AS alternative_name"
		sql += '''
			FROM objectives
				LEFT OUTER JOIN requirements
					ON objectives.name = requirements.objective
				LEFT OUTER JOIN alternatives
					ON  requirements.objective = alternatives.objective
					AND requirements.id        = alternatives.requirement
			'''
		if export:
			sql += '''
					LEFT OUTER JOIN objectives AS objectives2
						ON alternatives.alternative = objectives2.name
				'''

		if objective:
			sql += "WHERE objectives.name==:objective"
			if requirement:
				sql += "AND requirement==:requirement"

		sql += " ORDER BY "
#		if not export:
#			sql += """
#				expiration ASC,
#				(SELECT COUNT(*) FROM alternatives WHERE objective==name) ASC,		-- Requirements
#				(SELECT COUNT(*) FROM alternatives WHERE alternative==name) DESC,	-- Dependencies
#				alternative_quantity ASC,
#				"""
		sql += "name,requirement,priority"

#		print sql

		return self.__connection.execute(sql,
										{'objective':objective,
										 'requirement':requirement}).fetchall()


	def Dependents(self, objective):
		"Get the dependents of a requirement"
		return self.__connection.execute('''
			SELECT * FROM alternatives
			WHERE alternative==:objective
			GROUP BY objective
			''',
			{'objective':objective}).fetchall()


	def MinQuantity(self,objective):
		"Get the min quantity needed by a objective to satisface a requirement"
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

	def AddRequirement(self, objective, id=None, optional=None):
		# Create objective (if needed)
		self.AddObjective(objective)

		# Create new requirement id if no one was expecified
		if id == None:
			id = self.__connection.execute('''
				SELECT COALESCE(MAX(id)+1,0) AS id
				FROM requirements
				WHERE objective==:objective
				ORDER BY id
				''',
				{'objective':objective}).fetchone()['id']

		# Create new requirement
		self.__connection.execute('''
			INSERT OR IGNORE INTO requirements(objective, id)
									   VALUES(:objective,:id)
			''',
			{'objective':objective, 'id':id})

		# Set optional
		if optional!=None:
			self.__connection.execute('''
				UPDATE requirements
				SET optional=:optional
				WHERE objective==:objective
				AND id==:id
				''',
				{'objective':objective, 'id':id, 'optional':optional})

	def AddAlternative(self, objective, requirement, priority,
							 alternative, quantity=1):
		# Create alternative (if needed)
		self.AddObjective(alternative)

		# Add requirement to the objective
		self.AddRequirement(objective, requirement)

		# Add alternative to the requirement
		self.__connection.execute('''
			INSERT INTO alternatives(objective,requirement,priority,alternative,quantity)
				VALUES(?,?,?,?,?)
			''',
			(objective,requirement,priority,alternative,quantity))


	# Deleters

	def DelObjective(self, name, delete_orphans = False):
		# Get objective requirements if we want to delete orphan ones
		if delete_orphans:
			requirements = self.Requirements(name)

		# Re-adjust priorities
		checked = []
		for dependent in self.Dependents(name):

			# If requirement has alternatives
			# update its priority
			if dependent['priority']:
				dependent['count'] = 0

				# If requirement has not been checked
				# get it's number of alternatives
				if dependent['objective'] not in checked:
					checked.append(dependent['objective'])

					# Get the number of alternatives for a objective
					# and requirement specifics
					dependent['count'] = self.__connection.execute('''
						SELECT COUNT(*) AS count FROM alternatives
						WHERE objective  ==:objective
						  AND requirement==:requirement
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
					  AND requirement==:requirement
					''',
					dependent)


		# Delete objective
		self.__connection.execute('''
			DELETE FROM objectives
			WHERE name==?
			''',
			(name,))

		# Delete orphan requirements (if any)
		if delete_orphans:
			self.DelOrphans(requirements)


	def DelRequirements(self, objective):
		self.__connection.execute('''
			DELETE FROM requirements
			WHERE objective==?
			''',
			(objective,))


	def DelOrphans(self, requirements):
		"""Delete the objectives without dependents
		defined in the `requirements` list
		"""
		for requirement in requirements:
			for alternative in requirement:
				# If requirement doesn't have a dependent,
				# delete the orphan
				if not self.Dependents(alternative):
					self.DelObjective(alternative, True)
	#			if(self.GetObjective(requirement['alternative'])
	#			and not self.Dependents(requirement['alternative'])):
	#				self.DelObjective(requirement['alternative'], True)


	def UpdateName(self, old, new):
		self.__connection.execute('''
			UPDATE objectives
			SET   name=:new
			WHERE name=:old
			''',
			{'new':new, 'old':old})