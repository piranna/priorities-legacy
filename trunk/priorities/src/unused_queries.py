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
			SELECT name,quantity,expiration,COUNT(*) AS num_requeriments
				FROM objectives,requeriments
				WHERE objectives.id==requeriments.objective
				GROUP BY name
				ORDER BY num_requeriments
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


