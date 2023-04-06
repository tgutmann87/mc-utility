import os
import html
import json
import shutil
import urllib
import logging
import zipfile
import datetime
import requests
import subprocess
import configparser

class MCUtil:
	def __init__(self):
		#Initialize Logging
		logging.basicConfig(filename="/var/log/mc-utility.log", filemode="a", level=logging.DEBUG)
		
		print("==========Welcome to the Minecraft Server Utility!==========")
		logging.info("==========Welcome to the Minecraft Server Utility!==========")
		#Checking for and creating configuration file if it doesn't exist
		self.initializeConfigurationFile()
		
	def backupServer(self):
		logging.info("==========Beginning Backup of Server==========")
		logging.info("Stopping Minecraft Server.")
		print("Stopping Minecraft Server.")
		subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()

		logging.info("Zipping necessary files.")
		print("Zipping necessary files.")
		os.chdir(self.serverPathway)
		shutil.copy("/etc/systemd/system/minecraft.service", self.serverPathway)
		shutil.make_archive(self.configParser.get("mc-utility", "backup_Location") + "/minecraftServer" + str(datetime.datetime.now().date()), "zip")

		logging.info("Files have been zipped and sent to web server for download. Restarting the Minecraft server.")
		print("Files have been zipped and sent to web server for download. Restarting the Minecraft server.")
		subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

		logging.info("Minecraft server has been successfully restarted.")
		print("Minecraft server has been successfully restarted.")
		
	def changeServerProperties(self, property, value):
		logging.info("==========Beginning Modification of server.properties==========")
		print("==========Beginning Modification of server.properties==========")
		
		#Specifying the section for ConfigParser in addition to setting all arguments to a lower case 
		section = "Minecraft Properties"

		#Declares four different lists for the different data types. The respective properties for those data types are contained within those lists.
		boolList = ["allow-flight", "allow-nether", "broadcast-console-to-ops", "broadcast-rcon-to-ops", "enable-command-block", "enable-jmx-monitoring", "enable-rcon", "sync-chunk-writes", 
		"enable-status", "enable-query", "force-gamemode", "generate-structures", "hardcore", "online-mode", "prevent-proxy-connections", "pvp", "require-resource-pack", "snooper-enabled", 
		"spawn-animals", "spawn-monsters", "spawn-npcs", "use-native-transport", "white-list", "enforce-whitelist"]
		
		selectionList = ["", "difficulty", "gamemode", "level-type"]
		
		integerList = ["entity-broadcast-range-percentage", "function-permission-level", "op-permission-level", "max-build-height", "max-players", "player-idle-timeout", "spawn-protection", 
		"max-tick-time", "max-world-size", "rate-limit", "network-compression-threshold", "query.port", "rcon.port", "server-port", "view-distance"]
		
		stringList = ["generator-settings", "level-name", "level-seed", "motd", "rcon.password", "resource-pack", "resource-pack-sha1", "server-ip"]
		
		#Sets other arguments to lowercase as long as they're strings.
		option = property.lower()
		self.value = value
		if(isinstance(value, str)):
			self.value = self.value.lower()
		
		#Parses the server.properties file to add the Section Header so that ConfigParser can be used.
		logging.debug("Adding section header to server.properties for proper parsing.")
		file = open(serverPathway + "/server.properties", "r")
		temp = file.readlines()
		file.close()
		
		if not temp[0].startswith("[Minecraft Properties]"):
			temp.insert(0, "[Minecraft Properties]\n")
		
		###Commenting out to test for 
		#Writes the changes back to the server.properties file.
		#file = open(serverPathway + "/server.properties", "w")
		#for line in temp:
		#	file.write(line)
		#file.close()
		
		#Initializing the Parser.
		propertiesParser = configparser.ConfigParser()
		#propertiesParser.read(serverPathway + "/server.properties")
		propertiesParser.read_string(temp)
		
		#Checks if the option provided matches one of the above groupings (Integer, String, Boolean, Selection).
		if boolList.count(option):
			if self.value == "true" or self.value == "false":
				#Writes the new boolean self.value to the Config Parser assuming that self.value is equal to true or false.
				propertiesParser.set(section, option, self.value)
			else:
				#Error logging in the event that the conditions for the self.value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a boolean value. Value provided was: " + self.value)
				print("The value specified for the option \"" + option + "\" isn't a boolean value. Value provided was: " + self.value)
				
		elif selectionList.count(option):
			selectionself.values = [[""], ["", "peaceful", "easy", "normal", "hard"], ["", "survival", "creative", "adventure", "spectator"], ["", "default", "flat", "largeBiomes", "amplified"]]
			if selectionself.values[selectionList.index(option)].count(self.value):
				#Writes the new selection to the Config Parser assuming that self.value provided exists within the expected set of self.values for that option.
				propertiesParser.set(section, option, self.value)
			else:
				#Error logging in the event that the conditions for the self.value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a proper selection. Value provided was: " + self.value)
				print("The value specified for the option \"" + option + "\" isn't a proper selection. Value provided was: " + self.value)
				print("The option \"" + option + "\ has the following selections: " + str(selectionself.values[selectionList.index(option)]))
				
		elif integerList.count(option):
			if self.value.isnumeric() and not isinstance(int(self.value), float):
				if int(self.value) <= 29999984 and int(self.value) >= 1:
					#Writes the new Integer self.value to the Config Parser assuming that the self.value provided is an integer and not float.
					#In addition the self.value must also be between 1 and 29,999,984.
					propertiesParser.set(section, option, self.value)
				else:
					#Error logging in the event that the conditions for the self.value aren't met.
					logging.warning("The value specified for the option \"" + option + "\" isn't an integer between 1 and 29999984. Value provided was: " + self.value)
					print("The value specified for the option \"" + option + "\" isn't an integer between 1 and 29999984. Value provided was: " + self.value)
			else:
				#Error logging in the event that the conditions for the self.value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" either isn't a number or is a decimal. Value provided was: " + self.value)
				print("The value specified for the option \"" + option + "\" either isn't a number or is a decimal. Value provided was: " + self.value)
		
		elif stringList.count(option):
			if len(self.value) <= 512:
				#Writes the new String self.value to the Config Parser assuming that it's no larger that 512 characters
				propertiesParser.set(section, option, value)
			else:
				#Error logging in the event that the conditions for the self.value aren't met.
				logging.warning("The value specified for the option \"" + option + "\" isn't a string that's less than 512 characters. Value provided was: " + self.value)
				print("The value specified for the option \"" + option + "\" isn't a string that's less than 512 characters. Value provided was: " + self.value)
		else:
			#Error logging in the event that the conditions for the self.value aren't met.	
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
		
	def createService(self, minRAM, maxRAM):
		file = open("/etc/systemd/system/minecraft.service", "x")
		file.write("[Unit]\n")
		file.write("Description=Minecraft Server\n")
		file.write("After=network.target\n")
		file.write("[Service]\n")
		file.write("Type=simple\n")
		file.write("ExecStart=/bin/sh -c \"cd " + self.serverPathway + "; exec java -Xmx" + maxRAM + "G -Xms" + minRAM + "G -jar mcserver.jar nogui;\"")
		file.write("TimeoutStartSec=0\n")
		file.write("SuccessExitStatus=143")
		file.write("[Install]\n")
		file.write("WantedBy=default.target\n")
		file.close()
		
		#Modifying file permissions
		logging.info("Setting permissions for minecraft.service.")
		print("Setting permissions for minecraft.service.")
		os.chmod("/etc/systemd/system/minecraft.service", 0o600) #The '0o' (Zero - Oh) signifies octal numbers proceeding
		
	def downloadBackup(self):
		temp = 0
		
	def getDownloadLink(self):
		#Using Mojang Minecraft API to get latest server download link
		logging.debug("Using Minecraft API to pull most recent server.jar download link.")
		temp = json.loads(requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").text)
		for version in temp["versions"]:
			if version["type"] == "release":
				temp = json.loads(requests.get(version["url"]).text)
				break
		##url = temp["downloads"]["server"]["url"]
		temp = temp["downloads"]["server"]["url"]
		logging.debug("Download URL Acquired. Location: " + temp)
		return temp
		
	def getConfigurationOption(self, option):
		return self.configParser.get("mc-utility", option)
		
	def initializeConfigurationFile(self):
		#Initializing ConfigParser
		self.configParser = configparser.ConfigParser()
		if os.path.isfile("/etc/mc-utility/mc-utility.info"):
			logging.debug("File exists! Transferring contents to appropriate variables.")
			self.configParser.read_file(open("/etc/mc-utility/mc-utility.info", "r"))	
		else:
			logging.debug("File doesn't exist! Creating /etc/mc-utility/mc-utility.info.")
			self.configParser.add_section("mc-utility")
			self.configParser.set("mc-utility", "Server_Location", "/usr/games/minecraft")
			self.configParser.set("mc-utility", "Backup_File_Location", "/var/www/html")
			self.configParser.set("mc-utility", "Archive_Site", "")
			self.configParser.set("mc-utility", "Logging_Level", "DEBUG")
			self.configParser.set("mc-utility", "Certificate_Path", "/etc/mc-utility/MC-Self-Signed.crt")
			self.configParser.set("mc-utility", "Private_Key_Path", "/etc/mc-utility/MC-Self-Signed.key")
			
			try:
				self.configParser.write(open("/etc/mc-utility/mc-utility.info", 'w'), space_around_delimiters=False)
			except FileNotFoundError:
				logging.debug("Creating /etc/mc-utility")
				os.mkdir("/etc/mc-utility")
			
		#Setting Class Variables 
		self.serverPathway = self.configParser.get("mc-utility", "Server_Location")
		self.backupFilePathway = self.configParser.get("mc-utility", "Backup_File_Location")
		self.archiveSite = self.configParser.get("mc-utility", "Archive_Site")
		self.logLevel = self.configParser.get("mc-utility", "Logging_Level")
		self.certPathway = self.configParser.get("mc-utility", "Certificate_Path")
		self.privateKeyPathway = self.configParser.get("mc-utility", "Private_Key_Path")
			
	def install(self):
		logging.info("==========Beginning Installation and Configuration of Server==========")
		logging.info("Core server files will be installed at the following location:  " + self.serverPathway)
		logging.info("Checking to see if the directory exists.")
		print("==========Beginning Installation and Configuration of Server==========")
		print("Core server files will be installed at the following location:  " + self.serverPathway)
		print("Checking to see if the directory exists.")
		
		url = self.getDownloadLink()

		#Creating the directories for the server as well as associated utility files.
		logging.debug("Creating necessary directory structures.")
		if not os.path.isdir(self.serverPathway):
			logging.debug("Creating " + self.serverPathway)
			os.makedirs(self.serverPathway)

		#Switching over to the directory where the server JAR will be installed.
		logging.debug("Moving MC Utility to directory.")
		os.replace("mc-utility.py", "/etc/mc-utility/mc-utility.py")
		os.replace("MCUtil.py", "/etc/mc-utility/MCUtil.py")
		logging.debug("Switching to the directory where the ser JAR file will be installed.")
		os.chdir(self.serverPathway)
		
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
			self.createService("1", "2")
		
		#Creating eula.txt
		logging.debug("Creating eula.txt")
		file = open("eula.txt", "w")
		file.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n")
		file.write("eula=true\n")
		file.close()
		
		#Writing server location to the configuration file
		self.configParser.set("mc-utility", "server_Location", self.serverPathway)

		logging.info("Starting the server.")
		print("Starting the server.")
		subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
		logging.info("Server has been successfully started. Have Fun!!!")
		print("Server has been successfully started. Have Fun!!!")
		
		self.configParser.write(open("/etc/mc-utility/mc-utility.info", "w"), space_around_delimiters=False)
		
	def listConfiguration(self):
		print(open("/etc/mc-utility/mc-utility.info", "r").read())
		
	def listServerProperties(self):	
		file = open(serverPathway + "/server.properties", "r")
		for line in file.readlines():
			print(line)
		file.close()
		
	def remove(self):
		logging.info("==========Beginning Removal of Server and All Related Files==========")
	
		#Removes the minecraft.service file if it exists.
		if os.path.isfile("/etc/systemd/system/minecraft.service"):
			logging.info("Removing minecraft.service")
			print("Removing minecraft.service")
			os.remove("/etc/systemd/system/minecraft.service")
		
		#Removes the server pathway, specified in the mc-utility.info file, if it exists.
		if os.path.isdir(self.serverPathway):
			logging.info("Removing " + self.serverPathway)
			print("Removing " + self.serverPathway)
			shutil.rmtree(self.serverPathway)

		#Removes the mc-utility.info file if it exists.
		if os.path.isfile("/etc/mc-utility/mc-utility.info"):
			logging.info("Removing /etc/mc-utility/mc-utility.info")
			print("Removing /etc/mc-utility/mc-utility.info")
			os.remove("/etc/mc-utility/mc-utility.info")

		logging.info("Server Removal Complete!")
		print("Server Removal Complete!")
		
	def setConfiguration(self, option, value): 
		self.configParser.set("mc-utility", option, value)
		configParser.write(open("/etc/mc-utility/mc-utility.info", "w"), space_around_delimiters=False)
		
	def unpackServer(self, pathway, filename):
		logging.info("==========Beginning Unpack of Server Backup==========")
		print("==========Beginning Unpack of Server Backup==========")
		
		#Checks to see if the server file exists and attempts a shutdown of the process if it does exist.
		if os.path.isfile("/etc/systemd/system/minecraft.server"):
			logging.info("Shutting down minecraft server.")
			print("Shutting down minecraft server.")
			subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
		
		#Removes the specified directory if it exists for safety.
		if os.path.isdir(pathway):
			logging.debug("Removing the old directory and all of it's contents.")
			shutil.rmtree(pathway)
		
		#Unpacking the ZIP file to the specified directory.
		logging.info("Unpacking The ZIP File to " + pathway)
		print("Unpacking The ZIP File to " + pathway)
		os.makedirs(pathway)
		shutil.unpack_archive(filename, pathway, "zip")
		
		#Restarts the server
		logging.info("Starting The Server.")
		print("Starting The Server.")
		subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

		logging.info("Server Sucessfully Started.")
		print("Server Sucessfully Started.")
		
	def updateServer(self):
		logging.info("==========Beginning Update of Server==========")
		logging.info("Stopping Minecraft Server.")
		print("==========Beginning Update of Server==========")
		print("Stopping the Minecraft Server.")
		
		url = self.getDownloadLink()
		
		subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
		
		#Removing the old server JAR file. Then downloading and writing to disk the new one.
		logging.info("Downloading the updated JAR file from https://minecraft.net")
		print("Downloading the updated JAR file from https://minecraft.net")
		os.chdir(self.serverPathway)
		os.remove("mcserver.jar")
		logging.debug("Writing binary data to mcserver.jar")
		jar = urllib.request.urlopen(url).read()
		file = open("mcserver.jar", "wb")
		file.write(jar)
		file.close()

		logging.info("Restarting the server.")
		print("Restarting the server.")
		subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
		