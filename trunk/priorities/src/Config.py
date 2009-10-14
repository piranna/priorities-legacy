import os


class Config:
	"Constructor & Destructor"
	def __init__(self, config_path):
		self.__config_path = os.path.expanduser(config_path)

		# Default config
		self.__Defaults()

		# Create configuration dir
		self.__MakeConfigDir()

		# Load file data
		self.__Load()

	def __del__(self):
		self.__Store()


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
	
		self.__config['showExceededDependencies']	= 1
		self.__config['expirationWarning']			= 1
		self.__config['removeOrphanRequeriments']	= True
		self.__config['deleteCascade']				= True
		self.__config['confirmDeleteCascade']		= True
	
		self.__config['color_unabordable']			= "#FF7777"
		self.__config['color_inprocess']			= "#FFFF77"
		self.__config['color_available']			= "#77FF77"
		self.__config['color_satisfacted']			= "#7777FF"

	def __MakeConfigDir(self):
		try:
			os.makedirs(self.__config_path)
	
		except os.error, e:
			pass


	"Load & Store"
	def __Load(self):	
		"Load config from file"
		try:
			file = open(self.__config_path+"/config", "r")
	
			for line in file.readlines():
				line = line.split('//')[0].split('=')
				self.__config[line[0].strip()] = line[1].strip()
#				print line[0].strip(),line[1].strip()

			# Re-define boolean config
			self.__config['useDefaultDB']				= (self.__config['useDefaultDB']=="True")
			self.__config['showSharp']					= (self.__config['showSharp']=="True")
			self.__config['showArrowHeads']				= (self.__config['showArrowHeads']=="True")
			self.__config['removeOrphanRequeriments']	= (self.__config['removeOrphanRequeriments']=="True")
			self.__config['deleteCascade']				= (self.__config['deleteCascade']=="True")
			self.__config['confirmDeleteCascade']		= (self.__config['confirmDeleteCascade']=="True")
	
			# Re-define integer config
			self.__config['showExceededDependencies']	= int(self.__config['showExceededDependencies'])
			self.__config['expirationWarning']			= int(self.__config['expirationWarning'])
	
		except:
			print "Exception loading config"

		finally:
			file.close()

	def __Store(self):
		try:
			file = open(self.__config_path+"/config", "w")
	
			for key,value in self.__config.iteritems():
#				print key,value
				file.write(key+"="+str(value)+"\n")

		except:
			print "Exception storing config"

		finally:
			file.close()