APP="priorities"

import gettext
gettext.textdomain(APP)
_ = gettext.gettext


class View:
	controller = None
	config = None

	def __init__(self, id):
		if not self.controller.Get_Connection():
			self.__AskDB()