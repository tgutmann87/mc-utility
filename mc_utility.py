#Series of import statements
import os
import sys
import html
import shutil
import urllib #For making HTTP requests https://docs.python.org/3/library/urllib.request.html#module-urllib.request
import logging
import zipfile
import datetime
import requests
import subprocess
from html.parser import HTMLParser

#Custom classes used in the utility
class MCHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == "a" and attrs[0][1].startswith("https://launcher.mojang.com/v1/objects/"):
			attr = attrs[0][1]
			file = open("mc_temp.info", "a")
			file.write(attr)
			file.close()		

#Utility Begins
print("==========Welcome to the Minecraft Server Utility!==========")

#Logging is initialized
logging.basicConfig(filename="/var/log/mc_utility.log", filemode="a", level=logging.DEBUG)

#Checking if info file exists. If the file does data is extracted and proper variables are set.
logging.debug("Checking to see if mc_utility.info exists.")
if os.path.isfile("/etc/mc_utility/mc_utility.info"):
	logging.debug("File exists! Transferring contents to appropriate variables.")
	file = open("/etc/mc_utility/mc_utility.info", "r")
	pathway = file.readline()
	file.close()
else:
	pathway = "/usr/games/minecraft"

#Creates an HTML parser then feeds the https://www.minecraft.net/en-us/download/server webpage to it for the download link to be obtained.
#Can likely be turned into a function later on.
logging.debug("Parsing Minecraft download page for link to the most recent release.")
parser = MCHTMLParser()
html = str(urllib.request.urlopen("https://www.minecraft.net/en-us/download/server").read())
parser.feed(html)

if os.path.isfile("mc_temp.info"):
	logging.debug("Download link for JAR file found.")
	file = open("mc_temp.info", "r")
	url = file.readline()
	file.close()
	os.remove("mc_temp.info")
else: 
	logging.warning("Download link for JAR couldn't be found.")

#Checking the first variable to see what function to execute
#FIRST ARGUMENT: Function to execute
if sys.argv[1] == "install":
#SECOND ARGUMENT: Directory to install the server into
	logging.info("==========Beginning Installation and Configuration of Server==========")
	logging.info("Core server files will be installed at the following location:  " + sys.argv[2])
	logging.info("Checking to see if the directory exists.")
	print("==========Beginning Installation and Configuration of Server==========")
	print("Core server files will be installed at the following location:  " + sys.argv[2])
	print("Checking to see if the directory exists.")

	logging.debug("Creating necessary directory structures.")
	if not os.path.isdir(sys.argv[2]):
		logging.debug("Creating " + sys.argv[2])
		os.makedirs(sys.argv[2])

	if not os.path.isdir("/etc/mc_utility"):
		logging.debug("Creating /etc/mc_utility")
		os.mkdir("/etc/mc_utility")

	logging.debug("Moving MC Utility to directory.")
	os.replace("mc_utility.py", "/etc/mc_utility/mc_utility.py")
	logging.debug("Switching to the directory.")
	os.chdir(sys.argv[2])
	
	logging.info("Downloading JAR file from https://minecraft.net")
	print("Downloading JAR file from https://minecraft.net")
	jar = urllib.request.urlopen(url).read()
	file = open("mcserver.jar", "wb")
	file.write(jar)
	file.close()
	
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
		file.write("ExecStart=" + sys.argv[2] + "/start_minecraft_server.sh\n")
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
	file.write("cd " + sys.argv[2] + "\n")
	file.write("exec java -Xmx2G -Xms1G -jar mcserver.jar nogui\n")
	file.close()

	logging.debug("Creating eula.txt")
	file = open("eula.txt", "w")
	file.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n")
	file.write("eula=true\n")
	file.close()

	logging.debug("Creating mc_utility.info")
	file = open("/etc/mc_utility/mc_utility.info", "w")
	file.write(sys.argv[2])
	file.close()

	logging.info("Setting permissions for files.")
	print("Setting permissions for files.")
	os.chmod("/etc/systemd/system/minecraft.service", 0o600) #The '0o' (Zero - Oh) signifies octal numbers proceeding
	os.chmod("start_minecraft_server.sh", 0o770)

	logging.info("Writing cronjobs.")
	print("Writing cronjobs.")
	#Code to implement cronjob for server backup
	#Will be added at a later date	

	logging.info("Starting the server.")
	print("Starting the server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	logging.info("Server has been successfully started. Have Fun!!!")
	print("Server has been successfully started. Have Fun!!!")

elif sys.argv[1] == "backup":
	logging.info("==========Beginning Backup of Server==========")
	logging.info("Stopping Minecraft Server.")
	print("Stopping Minecraft Server.")
	subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()

	logging.info("Zipping necessary files.")
	print("Zipping necessary files.")
	os.chdir(pathway)
	shutil.copy("/etc/systemd/system/minecraft.service", pathway)
	shutil.make_archive("/var/www/html/" + "minecraftServer" + str(datetime.datetime.now().date()), "zip")

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

	logging.info("Downloading the updated JAR file from https://minecraft.net")
	print("Downloading the updated JAR file from https://minecraft.net")
	os.chdir(pathway)
	os.remove("mcserver.jar")
	if os.path.isfile("mcserver.jar"):
		logging.warning("mcserver.jar has not been deleted!")
	else:
		logging.debug("Writing binary data to mcserver.jar")
		jar = urllib.request.urlopen(url).read()
		file = open("mcserver.jar", "wb")
		file.write(jar)
		file.close()

	logging.info("Restarting the server.")
	print("Restarting the server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	logging.info("Server has been successfully restarted. Update process complete!")

elif sys.argv[1] == "remove":
	logging.info("==========Beginning Removal of Server and All Related Files==========")
	
	if os.path.isfile("/etc/systemd/system/minecraft.service"):
		logging.info("Removing minecraft.service")
		print("Removing minecraft.service")
		os.remove("/etc/systemd/system/minecraft.service")
	
	if os.path.isdir(pathway):
		logging.info("Removing " + pathway)
		print("Removing " + pathway)
		shutil.rmtree(pathway)

	if os.path.isfile("/etc/mc_utility/mc_utility.info"):
		logging.info("Removing /etc/mc_utility/mc_utility.info")
		print("Removing /etc/mc_utility/mc_utility.info")
		os.remove("/etc/mc_utility/mc_utility.info")

	if os.path.isfile("/etc/mcserver_backup.info"):
		logging.info("Removing /etc/mcserver_backup.info")
		print("Removing /etc/mcserver_backup.info")
		os.remove("/etc/mcserver_backup.info")

	logging.info("Server Removal Complete!")
	print("Server Removal Complete!")

elif sys.argv[1] == "dlbackup":
	#SECOND ARGUMENT: Location to place ZIP backup
	#THIRD ARGUMENT: IP/Domain of where the backup is located
	logging.info("==========Beginning Download of the Server Backup==========")

	if not os.path.isdir(sys.argv[2]):
		logging.info("Unable to find backup directory. Creating directory and necessary parents.")
		print("Unable to find backup directory. Creating directory and necessary parents.")
		os.makedirs(sys.argv[2])
		logging.debug("Directory created.")

	logging.info("Downloading backup from https://" + sys.argv[3])
	print("Downloading backup from https://" + sys.argv[3])
	os.chdir(sys.argv[2])

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

	logging.debug("Writing binary data to minecraftServer" + str(datetime.datetime.now().date()) + ".zip")
	file = open("minecraftServer" + str(datetime.datetime.now().date()) + ".zip", "wb")
	file.write(zip)
	file.close()

	logging.info("Creating /etc/mc_utility/mcserver_backup.info")
	print("Creating /etc/mc_utility/mcserver_backup.info")
	file = open("/etc/mc_utility/mcserver_backup.info", "w")
	file.write(sys.argv[2])
	file.close()

elif sys.argv[1] == "unpack":
	#SECOND ARGUMENT: Where to unpack the server files to
	#THIRD ARGUMENT: ZIP file to unpack into current environment
	logging.info("==========Beginning Unpack of Server Backup==========")

	if os.path.isfile("/etc/systemd/system/minecraft.server"):
		logging.info("Shutting down minecraft server.")
		print("Shutting down minecraft server.")
		subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()

###Will fix for next update###	
#	if os.path.isfile("/etc/mcserver_backup.info"):
#		logging.info("Reading mcserver_backup.info For Backup Directory.")
#		print("Reading mcserver_backup.info For Backup Directory.")
#		file = open("/etc/mcserver_backup.info", "r")
#		os.chdir(file.readline())
#		file.close()

	if os.path.isdir(sys.argv[2]):
		logging.debug("Removing the old directory and all of it's contents.")
		shutil.rmtree(sys.argv[2])

	logging.info("Unpacking The ZIP File to " + sys.argv[2])
	print("Unpacking The ZIP File to " + sys.argv[2])
	os.makedirs(sys.argv[2])
	shutil.unpack_archive(sys.argv[3], sys.argv[2], "zip")

	logging.info("Starting The Server.")
	print("Starting The Server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()

	logging.info("Server Sucessfully Started.")
	print("Server Sucessfully Started.")
	print("Creating /etc/mc_utility/mc_utility.info")
	file = open("/etc/mc_utility/mc_utility.info", "w")
	file.write(sys.argv[2])
	file.close()