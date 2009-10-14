import os


def Load():
	print "\nLoad"
	config_dir = os.path.expanduser("~/.priorities")

	config = {}

	# Default config
	config['useDefaultDB']				= True
	config['database']					= config_dir+"/personal.sqlite"

	config['showSharp']					= False
	config['showArrowHeads']			= True

	config['showExceededDependencies']	= 1
	config['expirationWarning']			= 1
	config['removeOrphanRequeriments']	= True
	config['deleteCascade']				= True
	config['confirmDeleteCascade']		= True

	config['color_unabordable']			= "#FF7777"
	config['color_inprocess']			= "#FFFF77"
	config['color_available']			= "#77FF77"
	config['color_satisfacted']			= "#7777FF"

	# Load config from file
	# Create configuration dir
	try:
		os.makedirs(config_dir)

	except os.error, e:
		pass
		#print "Exception on 'config.py':", os.strerror(e.args[0])

	try:
		file = open(config_dir+"/config", "r")

		for line in file.readlines():
			line = line.split('//')[0].split('=')
			config[line[0].strip()] = line[1].strip()
			print line[0].strip(),line[1].strip()

		file.close()

		# Re-define boolean config
		config['useDefaultDB']				= (config['useDefaultDB']=="True")
		config['showSharp']					= (config['showSharp']=="True")
		config['showArrowHeads']			= (config['showArrowHeads']=="True")
		config['removeOrphanRequeriments']	= (config['removeOrphanRequeriments']=="True")
		config['deleteCascade']				= (config['deleteCascade']=="True")
		config['confirmDeleteCascade']		= (config['confirmDeleteCascade']=="True")

		# Re-define integer config
		config['showExceededDependencies']	= int(config['showExceededDependencies'])
		config['expirationWarning']			= int(config['expirationWarning'])

	except:
		pass
		#print "no file to load"

	return config


def Store(config):
	print "\nStore"
	config_dir = os.path.expanduser("~/.priorities")

	try:
		file = open(config_dir+"/config", "w")

		for key,value in config.iteritems():
			print key,value
			file.write(key+"="+str(value)+"\n")

		file.close()

	except:
		print "Exception storing config"