import os


def Load():
	print "\nLoad"
	config_dir = os.path.expanduser("~/.priorities")

	preferences = {}

	# Default preferences
	preferences['useDefaultDB']				= True
	preferences['database']					= config_dir+"/personal.sqlite"

	preferences['showSharp']				= False
	preferences['showArrowHeads']			= True

	preferences['showExceededDependencies']	= 1
	preferences['expirationWarning']		= 1
	preferences['deleteCascade']			= True

	preferences['color_unabordable']		= "#FF7777"
	preferences['color_inprocess']			= "#FFFF77"
	preferences['color_available']			= "#77FF77"
	preferences['color_satisfacted']		= "#7777FF"

	# Load preferences from file
	# Create configuration dir
	try:
		os.makedirs(config_dir)

	except os.error, e:
		pass
		#print "Exception on 'Preferences.py':", os.strerror(e.args[0])

	try:
		file = open(config_dir+"/config", "r")

		for line in file.readlines():
			line = line.split('//')[0].split('=')
			preferences[line[0].strip()] = line[1].strip()
			print line[0].strip(),line[1].strip()

		file.close()

		# Re-define boolean preferences
		preferences['useDefaultDB']		= (preferences['useDefaultDB']=="True")
		preferences['showSharp']		= (preferences['showSharp']=="True")
		preferences['showArrowHeads']	= (preferences['showArrowHeads']=="True")
		preferences['deleteCascade']	= (preferences['deleteCascade']=="True")

		# Re-define integer preferences
		preferences['showExceededDependencies']	= int(preferences['showExceededDependencies'])
		preferences['expirationWarning']		= int(preferences['expirationWarning'])

	except:
		pass
		#print "no file to load"

	return preferences


def Store(preferences):
	print "\nStore"
	config_dir = os.path.expanduser("~/.priorities")

	try:
		file = open(config_dir+"/config", "w")

		for key,value in preferences.iteritems():
			print key,value
			file.write(key+"="+str(value)+"\n")

		file.close()

	except:
		print "Exception storing preferences"

