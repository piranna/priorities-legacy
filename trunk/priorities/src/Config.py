import os


class Config:
	"Constructor & Destructor"
	def __init__(self, config_path):
		self.__config_path = os.path.expanduser(config_path)

		# Default config
		self.__Defaults()

		# Load file data
		self.__Load()

	def __del__(self):
		self.__Store()

	"Defaults"
	def __Defaults(self):
		self.config = {}

		self.config['useDefaultDB']				= True
		self.config['database']					= self.config_path+"/personal.sqlite"
	
		self.config['showSharp']				= False
		self.config['showArrowHeads']			= True
	
		self.config['showExceededDependencies']	= 1
		self.config['expirationWarning']		= 1
		self.config['removeOrphanRequeriments']	= True
		self.config['deleteCascade']			= True
		self.config['confirmDeleteCascade']		= True
	
		self.config['color_unabordable']		= "#FF7777"
		self.config['color_inprocess']			= "#FFFF77"
		self.config['color_available']			= "#77FF77"
		self.config['color_satisfacted']		= "#7777FF"


	"Get & Set"
	def Get(self, var):
		return self.config.get(var)

	def Set(self, var, value):
		if self.config.has_key(var):
			self.config[var] = value


	"Load & Store"
	def __Load(self):	
		# Load config from file
		# Create configuration dir
		try:
			os.makedirs(self.config_path)
	
		except os.error, e:
			pass
			#print "Exception on 'config.py':", os.strerror(e.args[0])
	
		try:
			file = open(self.config_path+"/config", "r")
	
			for line in file.readlines():
				line = line.split('//')[0].split('=')
				config[line[0].strip()] = line[1].strip()
#				print line[0].strip(),line[1].strip()
	
			file.close()
	
			# Re-define boolean config
			self.config['useDefaultDB']				= (self.config['useDefaultDB']=="True")
			self.config['showSharp']				= (self.config['showSharp']=="True")
			self.config['showArrowHeads']			= (self.config['showArrowHeads']=="True")
			self.config['removeOrphanRequeriments']	= (self.config['removeOrphanRequeriments']=="True")
			self.config['deleteCascade']			= (self.config['deleteCascade']=="True")
			self.config['confirmDeleteCascade']		= (self.config['confirmDeleteCascade']=="True")
	
			# Re-define integer config
			self.config['showExceededDependencies']	= int(self.config['showExceededDependencies'])
			self.config['expirationWarning']		= int(self.config['expirationWarning'])
	
		except:
			pass
			#print "no file to load"
	
		return self.config

	def __Store(self):
		try:
			file = open(self.config_path+"/config", "w")
	
			for key,value in self.config.iteritems():
#				print key,value
				file.write(key+"="+str(value)+"\n")

		except:
			print "Exception storing config"

		finally:
			file.close()