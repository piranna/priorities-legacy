import os


import gettext
gettext.textdomain("priorities")
_ = gettext.gettext


class Config:
	"Constructor"
	def __init__(self, config_path):
		self.__config_path = os.path.expanduser(config_path)

		# Default config
		self.__Defaults()

		# Create configuration dir
		self.__MakeConfigDir()

		# Load file data
		self.__Load()


	"Get & Set"
	def Get(self, var):
		return self.__config.get(var)

	def Set(self, var, value):
		if self.__config.has_key(var):
			self.__config[var] = value


	"Defaults & MakeConfigDir"
	def __Defaults(self):
		self.__config = {}

		self.__config['useDefaultDB']				= True
		self.__config['database']					= self.__config_path+"/personal.sqlite"

		self.__config['showSharp']					= False
		self.__config['showArrowHeads']				= True
		self.__config['showLayoutBorders']			= True

		self.__config['showExceededRequeriments']	= 1
		self.__config['expirationWarning']			= 1
		self.__config['removeOrphanRequeriments']	= True
		self.__config['deleteCascade']				= True
		self.__config['confirmDeleteCascade']		= True

		self.__config['color_unabordable']			= "#FF7777"
		self.__config['color_inprocess']			= "#FFFF77"
		self.__config['color_available']			= "#77FF77"
		self.__config['color_satisfacted']			= "#7777FF"

		self.__config['maximized']					= False

	def __MakeConfigDir(self):
		try:
			os.makedirs(self.__config_path)

		except os.error:
			pass


	"Load & Store"
	def __Load(self):
		"Load config from file"
		try:
			file = open(self.__config_path+"/config", "r")

			for line in file.readlines():
				line = line.split('//')[0].split('=')
				self.__config[line[0].strip()] = line[1].strip()

			# Re-define boolean config
			self.__config['useDefaultDB']				= (self.__config['useDefaultDB']=="True")
			self.__config['showSharp']					= (self.__config['showSharp']=="True")
			self.__config['showArrowHeads']				= (self.__config['showArrowHeads']=="True")
			self.__config['showLayoutBorders']			= (self.__config['showLayoutBorders']=="True")
			self.__config['removeOrphanRequeriments']	= (self.__config['removeOrphanRequeriments']=="True")
			self.__config['deleteCascade']				= (self.__config['deleteCascade']=="True")
			self.__config['confirmDeleteCascade']		= (self.__config['confirmDeleteCascade']=="True")
			self.__config['maximized']					= (self.__config['maximized']=="True")

			# Re-define integer config
			self.__config['showExceededRequeriments']	= int(self.__config['showExceededRequeriments'])
			self.__config['expirationWarning']			= int(self.__config['expirationWarning'])

			file.close()

		except:
			print _("Exception loading config")

	def Store(self):
		try:
			file = open(self.__config_path+"/config", "w")

			for key,value in self.__config.iteritems():
				file.write(key+"="+str(value)+"\n")

		except:
			print _("Exception storing config")

		finally:
			file.close()

