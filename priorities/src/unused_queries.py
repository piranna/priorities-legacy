	def ObjectivesWithoutDependences(self):
		return self.connection.execute('''
			SELECT name,quantity,expiration FROM objectives
				WHERE objectives.id NOT IN
				(
					SELECT DISTINCT objective FROM requirements
				)
			''')


	def ObjectivesWithDependences(self):
		return self.connection.execute('''
			SELECT name,quantity,expiration,COUNT(*) AS num_requirements
				FROM objectives,requirements
				WHERE objectives.id==requirements.objective
				GROUP BY name
				ORDER BY num_requirements
			''')


	def ObjectivesWithDependencesNoSatisfacted(self):
		return self.connection.execute('''
			SELECT name FROM objectives,requirements
				WHERE objectives.id==requirements.objective
				AND COUNT(
					SELECT * FROM objectives,requirements
						WHERE objectives.id==requirements.alternative
				)==0
			''')


	def ObjectivesSatisfacted(self):
		return self.connection.execute('''
			SELECT objectives.id AS objective_id,name,objectives.quantity,expiration
			FROM objectives
				LEFT OUTER JOIN requirements
					ON objectives.id=requirements.objective
				LEFT OUTER JOIN
				(
					SELECT id,quantity FROM objectives
				) AS objectives2
					ON requirements.alternative==objectives2.id
			WHERE requirements.quantity<=objectives2.quantity
				OR requirements.quantity IS NULL
			GROUP BY objective_id
			ORDER BY expiration,COUNT(*)DESC,objectives.quantity
			''')


	def ObjectivesNoSatisfacted(self):
		return self.connection.execute('''
			SELECT objectives.id AS objective_id,name,objectives.quantity,expiration
			FROM objectives
				LEFT OUTER JOIN requirements
					ON objectives.id=requirements.objective
				LEFT OUTER JOIN
				(
					SELECT id,quantity FROM objectives
				) AS objectives2
					ON requirements.alternative==objectives2.id
			WHERE requirements.quantity>objectives2.quantity
			GROUP BY objective_id
			ORDER BY expiration,COUNT(*)DESC
			''')


