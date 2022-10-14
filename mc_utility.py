#Series of import statements
import os
import sys
import html
import json
import shutil
import urllib #For making HTTP requests https://docs.python.org/3/library/urllib.request.html#module-urllib.request
import logging
import zipfile
import datetime
import requests
import subprocess
import configparser

logging.basicConfig(filename="/var/log/mc_utility.log", filemode="a", level=logging.DEBUG)

#Utility Begins
print("==========Welcome to the Minecraft Server Utility!==========")
logging.info("==========Welcome to the Minecraft Server Utility!==========")

#Checking to see if mc_utility.info exists. If it does the values are parsed and if it doesn't the file is created with default values.
configParser = configparser.ConfigParser()
if os.path.isfile("/etc/mc_utility/mc_utility.info"):
	logging.debug("File exists! Transferring contents to appropriate variables.")
	configParser.read_file(open("/etc/mc_utility/mc_utility.info", "r"))	
else:
	configParser.add_section("MC_Utility")
	configParser.set("MC_Utility", "server_Location", "/usr/games/minecraft")
	configParser.set("MC_Utility", "backup_Location", "/var/www/html")
	configParser.set("MC_Utility", "archive_Location", "")
	configParser.set("MC_Utility", "logging_level", "DEBUG")

serverPathway = configParser.get("MC_Utility", "server_Location")

#Logging is initialized
#logging.basicConfig(filename="/var/log/mc_utility.log", filemode="a", level=configParser.get("MC_Utility", "logging_level"))

#Using the Minecraft API to pull the server JAR.
logging.debug("Using Minecraft API to pull most recent server.jar download link.")
temp = json.loads(requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").text)
for version in temp["versions"]:
	if version["type"] == "release":
		temp = json.loads(requests.get(version["url"]).text)
		break
url = temp["downloads"]["server"]["url"]
logging.debug("Download URL Acquired. Location: " + url)
temp = None 

#Checking the first variable to see what function to execute.
#FIRST ARGUMENT: Function to execute.
if sys.argv[1] == "install":
	logging.info("==========Beginning Installation and Configuration of Server==========")
	logging.info("Core server files will be installed at the following location:  " + serverPathway)
	logging.info("Checking to see if the directory exists.")
	print("==========Beginning Installation and Configuration of Server==========")
	print("Core server files will be installed at the following location:  " + serverPathway)
	print("Checking to see if the directory exists.")

	#Creating the directories for the server as well as associated utility files.
	logging.debug("Creating necessary directory structures.")
	if not os.path.isdir(serverPathway):
		logging.debug("Creating " + serverPathway)
		os.makedirs(serverPathway)

	if not os.path.isdir("/etc/mc_utility"):
		logging.debug("Creating /etc/mc_utility")
		os.mkdir("/etc/mc_utility")

	#Switching over to the directory where the server JAR will be installed.
	logging.debug("Moving MC Utility to directory.")
	os.replace("mc_utility.py", "/etc/mc_utility/mc_utility.py")
	logging.debug("Switching to the directory where the ser JAR file will be installed.")
	os.chdir(serverPathway)
	
	#Downloading the actual JAR file.
	logging.info("Downloading JAR file from https://minecraft.net.")
	print("Downloading JAR file from https://minecraft.net.")
	file = open("mcserver.jar", "wb")
	file.write(urllib.request.urlopen(url).read())
	file.close()
	
	#Creating the minecraft.service file in /etc/systemd/system/
	logging.info("Creating service related files.")
	print("Creating service related files.")
	logging.debug("Creating /etc/systemd/system/minecraft.service")
	if not os.path.isfile("/etc/systemd/system/minecraft.service"):
		file = open("/etc/systemd/system/minecraft.service", "x")
		file.write("[Unit]\n")
		file.write("Description=Start Minecraft\n")
		file.write("After=network.target\n")
		file.write("[Service]\n")
		file.write("Type=simple\n")
		file.write("ExecStart=" + serverPathway + "/start_minecraft_server.sh\n")
		file.write("TimeoutStartSec=0\n")
		file.write("SuccessExitStatus=143")
		file.write("[Install]\n")
		file.write("WantedBy=default.target\n")
		file.close()

	logging.debug("Creating start_minecraft_server.sh")
	#The functionality in the following file can eventually be integrated into this application and the ExecStart line changed in minecraft.service
	file = open("start_minecraft_server.sh", "w")
	file.write("#!/bin/bash\n")
	file.write("#Standard Minecraft\n")
	file.write("cd " + serverPathway + "\n")
	file.write("exec java -Xmx2G -Xms1G -jar mcserver.jar nogui\n")
	file.close()
	
	#Creating eula.txt
	logging.debug("Creating eula.txt")
	file = open("eula.txt", "w")
	file.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n")
	file.write("eula=true\n")
	file.close()
	
	#Writing server location to the configuration file
	configParser.set("MC_Utility", "server_Location", serverPathway)
	
	#Modifying file permissions
	logging.info("Setting permissions for files.")
	print("Setting permissions for files.")
	os.chmod("/etc/systemd/system/minecraft.service", 0o600) #The '0o' (Zero - Oh) signifies octal numbers proceeding
	os.chmod("start_minecraft_server.sh", 0o770)

	#logging.info("Writing cronjobs.")
	#print("Writing cronjobs.")
	#Code to implement cronjob for server backup
	#Will be added at a later date	

	logging.info("Starting the server.")
	print("Starting the server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	logging.info("Server has been successfully started. Have Fun!!!")
	print("Server has been successfully started. Have Fun!!!")

elif sys.argv[1] == "configure":
	#SECOND ARGUMENT: Option within mc_utility.info to change.
	#THIRD ARGUMENT: The value for the option that you're trying to change.
	if sys.argv[2] == "list":
		print(open("/etc/mc_utility/mc_utility.info", "r").read())
	else:
		configParser.set("MC_Utility", sys.argv[2], sys.argv[3])

elif sys.argv[1] == "backup":
	logging.info("==========Beginning Backup of Server==========")
	logging.info("Stopping Minecraft Server.")
	print("Stopping Minecraft Server.")
	subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()

	logging.info("Zipping necessary files.")
	print("Zipping necessary files.")
	os.chdir(serverPathway)
	shutil.copy("/etc/systemd/system/minecraft.service", serverPathway)
	shutil.make_archive(configParser.get("MC_Utility", "backup_Location") + "/minecraftServer" + str(datetime.datetime.now().date()), "zip")

	logging.info("Files have been zipped and sent to web server for download. Restarting the Minecraft server.")
	print("Files have been zipped and sent to web server for download. Restarting the Minecraft server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

	logging.info("Minecraft server has been successfully restarted.")
	print("Minecraft server has been successfully restarted.")

elif sys.argv[1] == "update":
	logging.info("==========Beginning Update of Server==========")
	logging.info("Stopping Minecraft Server.")
	print("==========Beginning Update of Server==========")
	print("Stopping the Minecraft Server.")
	subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
	
	#Removing the old server JAR file. Then downloading and writing to disk the new one.
	logging.info("Downloading the updated JAR file from https://minecraft.net")
	print("Downloading the updated JAR file from https://minecraft.net")
	os.chdir(serverPathway)
	os.remove("mcserver.jar")
	logging.debug("Writing binary data to mcserver.jar")
	jar = urllib.request.urlopen(url).read()
	file = open("mcserver.jar", "wb")
	file.write(jar)
	file.close()

	logging.info("Restarting the server.")
	print("Restarting the server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

elif sys.argv[1] == "remove":
	logging.info("==========Beginning Removal of Server and All Related Files==========")
	
	#Removes the minecraft.service file if it exists.
	if os.path.isfile("/etc/systemd/system/minecraft.service"):
		logging.info("Removing minecraft.service")
		print("Removing minecraft.service")
		os.remove("/etc/systemd/system/minecraft.service")
	
	#Removes the server pathway, specified in the mc_utility.info file, if it exists.
	if os.path.isdir(serverPathway):
		logging.info("Removing " + serverPathway)
		print("Removing " + serverPathway)
		shutil.rmtree(serverPathway)

	#Removes the mc_utility.info file if it exists.
	if os.path.isfile("/etc/mc_utility/mc_utility.info"):
		logging.info("Removing /etc/mc_utility/mc_utility.info")
		print("Removing /etc/mc_utility/mc_utility.info")
		os.remove("/etc/mc_utility/mc_utility.info")

	logging.info("Server Removal Complete!")
	print("Server Removal Complete!")

elif sys.argv[1] == "dlbackup":
	#SECOND ARGUMENT: Location to place ZIP backup.
	#THIRD ARGUMENT: IP/Domain of where the backup is located.
	logging.info("==========Beginning Download of the Server Backup==========")

	#Creates the specified backup directory if it doesn't already exist.
	if not os.path.isdir(sys.argv[2]):
		logging.info("Unable to find backup directory. Creating directory and necessary parents.")
		print("Unable to find backup directory. Creating directory and necessary parents.")
		os.makedirs(sys.argv[2])
		logging.debug("Directory created.")
	
	#Downloads the backup file from the specified web address.
	logging.info("Downloading backup from https://" + sys.argv[3])
	print("Downloading backup from https://" + sys.argv[3])
	os.chdir(sys.argv[2])

	#Checks to see if the given web address is using a secure connection.
	#This block of code needs to be revisited to determine if it is necessary.
	if sys.argv[3].rfind("https://") == 0:
		zip = urllib.request.urlopen(sys.argv[3] + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
		logging.debug("HTTPS already present. Secure connection already present.")
	elif sys.argv[3].rfind("http://") == 0:
		temp = sys.argv[3].replace("http://", "https://")
		zip = urllib.request.urlopen(temp + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
		logging.debug("Domain/IP given with HTTP converting to secure connection.")
	else:
		print("https://" + sys.argv[3] + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip")
		zip = urllib.request.urlopen("https://" + sys.argv[3] + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
		logging.debug("Secure connection specified.")

	#Writes the binary data retrieved from the specified web address to a ZIP file.
	logging.debug("Writing binary data to minecraftServer" + str(datetime.datetime.now().date()) + ".zip")
	file = open("minecraftServer" + str(datetime.datetime.now().date()) + ".zip", "wb")
	file.write(zip)
	file.close()
	
	#Writes the given backup directory to the mc_utility configuration file.
	logging.info("Creating /etc/mc_utility/mcserver_backup.info")
	print("Creating /etc/mc_utility/mcserver_backup.info")
	configParser.set("MC_Utility", "archive_Location", sys.argv[2])

elif sys.argv[1] == "unpack":
	#SECOND ARGUMENT: Where to unpack the server files to
	#THIRD ARGUMENT: ZIP file to unpack into current environment
	logging.info("==========Beginning Unpack of Server Backup==========")
	print("==========Beginning Unpack of Server Backup==========")
	
	#Checks to see if the server file exists and attempts a shutdown of the process if it does exist.
	if os.path.isfile("/etc/systemd/system/minecraft.server"):
		logging.info("Shutting down minecraft server.")
		print("Shutting down minecraft server.")
		subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
	
	#Removes the specified directory if it exists for safety.
	if os.path.isdir(sys.argv[2]):
		logging.debug("Removing the old directory and all of it's contents.")
		shutil.rmtree(sys.argv[2])
	
	#Unpacking the ZIP file to the specified directory.
	logging.info("Unpacking The ZIP File to " + sys.argv[2])
	print("Unpacking The ZIP File to " + sys.argv[2])
	os.makedirs(sys.argv[2])
	shutil.unpack_archive(sys.argv[3], sys.argv[2], "zip")
	
	#Restarts the server
	logging.info("Starting The Server.")
	print("Starting The Server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

	logging.info("Server Sucessfully Started.")
	print("Server Sucessfully Started.")
	print("Creating /etc/mc_utility/mc_utility.info")
		
elif sys.argv[1] == "properties":
	#SECOND ARGUMENT: Which sub function to execute
	#THIRD ARGUMENT: A property within the server.properties file.
	#FOURTH ARGUMENT: The value which will be set for the specified property.
	logging.info("==========Beginning Modification of server.properties==========")
	print("==========Beginning Modification of server.properties==========")
	
	#Specifying the section for ConfigParser in addition to setting all arguments to a lower case 
	section = "Minecraft Properties"
	action = sys.argv[2].lower()
	
	#If the provided sub-function is list the the entirety of the server.properties file will be displayed.
	if action == "list":
		file = open(serverPathway + "/server.properties", "r")
		for line in file.readlines():
			print(line)
		file.close()
	
	elif action == "change":
		#Declares four different lists for the different data types. The respective properties for those data types are contained within those lists.
		boolList = ["allow-flight", "allow-nether", "broadcast-console-to-ops", "broadcast-rcon-to-ops", "enable-command-block", "enable-jmx-monitoring", "enable-rcon", "sync-chunk-writes", 
		"enable-status", "enable-query", "force-gamemode", "generate-structures", "hardcore", "online-mode", "prevent-proxy-connections", "pvp", "require-resource-pack", "snooper-enabled", 
		"spawn-animals", "spawn-monsters", "spawn-npcs", "use-native-transport", "white-list", "enforce-whitelist"]
		
		selectionList = ["", "difficulty", "gamemode", "level-type"]
		
		integerList = ["entity-broadcast-range-percentage", "function-permission-level", "op-permission-level", "max-build-height", "max-players", "player-idle-timeout", "spawn-protection", 
		"max-tick-time", "max-world-size", "rate-limit", "network-compression-threshold", "query.port", "rcon.port", "server-port", "view-distance"]
		
		stringList = ["generator-settings", "level-name", "level-seed", "motd", "rcon.password", "resource-pack", "resource-pack-sha1", "server-ip"]
		
		#Sets other arguments to lowercase as long as they're strings.
		option = sys.argv[3].lower()
		value = sys.argv[4]
		if(isinstance(sys.argv[4], str)):
			value = value.lower()
		
		#Parses the server.properties file to add the Section Header so that ConfigParser can be used.
		logging.debug("Adding section header to server.properties for proper parsing.")
		file = open(serverPathway + "/server.properties", "r")
		temp = file.readlines()
		if not temp[0].startswith("[Minecraft Properties]"):
			temp.insert(0, "[Minecraft Properties]\n")
		file.close()
		
		#Writes the changes back to the server.properties file.
		file = open(serverPathway + "/server.properties", "w")
		for line in temp:
			file.write(line)
		file.close()
		
		#Initializing the Parser.
		propertiesParser = configparser.ConfigParser()
		propertiesParser.read(serverPathway + "/server.properties")
		
		#Checks if the option provided matches one of the above groupings (Integer, String, Boolean, Selection).
		if boolList.count(option):
			if value == "true" or value == "false":
				#Writes the new boolean value to the Config Parser assuming that value is equal to true or false.
				propertiesParser.set(section, option, value)
			else:
				#Error logging in the event that the conditions for the value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a boolean value. Value provided was: " + value)
				print("The value specified for the option \"" + option + "\" isn't a boolean value. Value provided was: " + value)
				
		elif selectionList.count(option):
			selectionValues = [[""], ["", "peaceful", "easy", "normal", "hard"], ["", "survival", "creative", "adventure", "spectator"], ["", "default", "flat", "largeBiomes", "amplified"]]
			if selectionValues[selectionList.index(option)].count(value):
				#Writes the new selection to the Config Parser assuming that value provided exists within the expected set of values for that option.
				propertiesParser.set(section, option, value)
			else:
				#Error logging in the event that the conditions for the value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a proper selection. Value provided was: " + value)
				print("The value specified for the option \"" + option + "\" isn't a proper selection. Value provided was: " + value)
				print("The option \"" + option + "\ has the following selections: " + str(selectionValues[selectionList.index(option)]))
				
		elif integerList.count(option):
			if value.isnumeric() and not isinstance(int(value), float):
				if int(value) <= 29999984 and int(value) >= 1:
					#Writes the new Integer value to the Config Parser assuming that the value provided is an integer and not float.
					#In addition the value must also be between 1 and 29,999,984.
					propertiesParser.set(section, option, value)
				else:
					#Error logging in the event that the conditions for the value aren't met.
					logging.warning("The value specified for the option \"" + option + "\" isn't an integer between 1 and 29999984. Value provided was: " + value)
					print("The value specified for the option \"" + option + "\" isn't an integer between 1 and 29999984. Value provided was: " + value)
			else:
				#Error logging in the event that the conditions for the value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" either isn't a number or is a decimal. Value provided was: " + value)
				print("The value specified for the option \"" + option + "\" either isn't a number or is a decimal. Value provided was: " + value)
		
		elif stringList.count(option):
			if len(value) <= 512:
				#Writes the new String value to the Config Parser assuming that it's no larger that 512 characters
				propertiesParser.set(section, option, sys.argv[4])
			else:
				#Error logging in the event that the conditions for the value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a string that's less than 512 characters. Value provided was: " + value)
				print("The value specified for the option \"" + option + "\" isn't a string that's less than 512 characters. Value provided was: " + value)
		else:
			#Error logging in the event that the conditions for the value aren't met.	
			logging.warning("The option provided doesn't exist. Please check your selection and try again.")
			print("The option provided doesn't exist. Please check your selection and try again.")
		
		#Writes the changes made to the Config Parser to the server.properties file.
		propertiesParser.write(open(serverPathway + "/server.properties", "w"), space_around_delimiters=False)
		
		#Reads the server.properties file to a variable to remove the section header.
		file = open(serverPathway + "/server.properties", "r")
		temp = file.readlines()
		file.close()
		
		#Removing the section header and writing the everything back to server.properties.
		file = open(serverPathway + "/server.properties", "w")
		temp.pop(0)
		for line in temp:
			file.write(line)
		file.close()
		
	else:
		#Error in the event that the subfunction provided doesn't exist.
		logging.warning("The action you specified is not one supported by the Properties function. Please check your input and try again. Action provided: " + action)
		print("The action you specified is not one supported by the Properties function. Please check your input and try again. Action provided: " + action)

#Writes any configuration changes to mc_utility.info prior to ending.
configParser.write(open("/etc/mc_utility/mc_utility.info", "w"), space_around_delimiters=False)