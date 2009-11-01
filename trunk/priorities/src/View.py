APP="priorities"

import gettext
gettext.textdomain(APP)
_ = gettext.gettext


class View:
	controller = None
	config = None

