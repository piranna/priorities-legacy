def Load():
	config_dir = "$HOME/.priorities"

#	preferences = []

#	# Default preferences
#	preferences.append(map('defaultDB', "~/.priorities/personal.sqlite"))
#	preferences['useDefaultDB'] = True

#	preferences['color_unavailable'] = "#FF0000"
#	preferences['color_inprocess'] = "#777700"
#	preferences['color_available'] = "#00FF00"
#	preferences['color_satisfacted'] = "#0000FF"

	# Load preferences from file
	# Create configuration dir
	try:
		import os

		os.makedirs(config_dir)

		try:
			file = open(config_dir+"/config", "r")
			for line in file.readlines():
				line = line.split('#')[0].split('=')
				line[0] = line[0].strip()
				line[1] = line[1].strip()

				if line[0]=="default_db":
					preferences['defaultDB'] = line[1]
				elif line[0]=="use_default_db":
					preferences['useDefaultDB'] = line[1]

				elif line[0]=="color_unavailable":
					preferences['color_unavailable'] = line[1]
				elif line[0]=="color_inprocess":
					preferences['color_inprocess'] = line[1]
				elif line[0]=="color_available":
					preferences['color_available'] = line[1]
				elif line[0]=="color_satisfacted":
					preferences['color_satisfacted'] = line[1]

		except:
			print "no file"

		finally:
			file.close()

	except Exception, e:
		print "Exception on 'Preferences.py':", e.args[0]

#	return preferences