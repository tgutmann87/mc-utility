import os
import sys
import html
import shutil
import urllib #For making HTTP requests https://docs.python.org/3/library/urllib.request.html#module-urllib.request
import zipfile
import datetime
import requests
import subprocess

from html.parser import HTMLParser

class MCHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == "a" and attrs[0][1].startswith("https://launcher.mojang.com/v1/objects/"):
			attr = attrs[0][1]
			file = open("mc_temp.info", "a")
			file.write(attr)
			file.close()

print("==========Welcome to the Minecraft Server Utility!==========")

if os.path.isfile("/etc/mc_utility.info"):
	file = open("/etc/mc_utility.info", "r")
	pathway = file.readline()
	file.close()	

parser = MCHTMLParser()
html = str(urllib.request.urlopen("https://www.minecraft.net/en-us/download/server").read())
parser.feed(html)
file = open("mc_temp.info", "r")
url = file.readline()
file.close()
os.remove("mc_temp.info")

#Checking the first variable to see what function to execute
#FIRST ARGUMENT: Function to execute
if sys.argv[1] == "install":
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Beginning Installation and Configuration of Server."], stdout = subprocess.PIPE).communicate()
	print("***Beginning the Installation of the Minecraft Server***")
	print("Core Server Files will be installed at the following location:  ", sys.argv[2])
	print("Checking to see if the directory exists.")
	if os.path.isdir(sys.argv[2]) == False:
		print("The Utility was nable to ind the directories. Creating necessary directory structure.")
		os.makedirs(sys.argv[2])
		print("Directory Created!")
	print("Moving MC Utility to directory.")
	os.replace("mc_utility.py", sys.argv[2] + "/mc_utility.py")
	print("Switching to the directory.")
	os.chdir(sys.argv[2])
	
	print("Downloading JAR file from https://minecraft.net")
	jar = urllib.request.urlopen(url).read()
	file = open("mcserver.jar", "wb")
	file.write(jar)
	file.close()
	
	print("JAR file successfully downloaded. Creating service related files.")
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

	print("Successfully reated minecraft.service. Creating start_minecraft_server.sh")
	#The functionality in the following file can eventually be integrated into this application and the ExecStart line changed in minecraft.service
	file = open("start_minecraft_server.sh", "w")
	file.write("#!/bin/bash\n")
	file.write("#Standard Minecraft\n")
	file.write("cd " + sys.argv[2] + "\n")
	file.write("exec java -Xmx2G -Xms1G -jar mcserver.jar nogui\n")
	file.close()
	
	print("Successfully created start_minecraft_server.sh. Creating eula.txt.")
	if os.path.isfile("eula.txt"):
		os.remove("eula.txt")
	file = open("eula.txt", "w")
	file.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n")
	file.write("eula=true\n")
	file.close()
	
	print("Successfully created eula.txt. Creating mc_utility.info.")
	file = open("/etc/mc_utility.info", "w")
	file.write(sys.argv[2])
	file.close()
	
	print("Setting proper permissions for files created.")
	os.chmod("/etc/systemd/system/minecraft.service", 0o600) #The '0o' (Zero - Oh) signifies octal numbers proceeding
	os.chmod("start_minecraft_server.sh", 0o770)
	
	print("Permissions have been successfully changed. Writing cronjobs.")
	#Code to implement cronjob for server backup
	#Will be added at a later date	
	
	print("Successfully created cronjobs. Starting the server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	print("Server has been successfully started. Have Fun!!!")

elif sys.argv[1] == "backup":
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Minecraft Server being stopped for backup."]).communicate()
	print("Stopping Minecraft Server.")
	subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
	
	print("Minecraft server stopped. Zipping necessary files.")
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Minecraft server stopped. Zipping necessary files."]).communicate()
	os.chdir(pathway)
	shutil.copy("/etc/systemd/system/minecraft.service", pathway)
	shutil.make_archive("/var/www/html/" + "minecraftServer" + str(datetime.datetime.now().date()), "zip")

	print("Files have been zipped and sent to web server for download. Restarting the Minecraft server.")
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Files have been zipped and sent to web server for download. Restarting the Minecraft server."]).communicate()
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	
	print("Minecraft server has been successfully restarted...")
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Minecraft server has been successfully restarted."]).communicate()

elif sys.argv[1] == "update":
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Starting update to the Minecraft server."]).communicate()
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Stopping the server."]).communicate()
	subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
	
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Successfully stopped the server. Downloading the updated JAR file from https://minecraft.net"]).communicate()
	os.chdir(pathway)
	os.remove("mcserver.jar")
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Old JAR file removed."]).communicate()
	#jar = urllib.request.urlopen(sys.argv[2]).read()
	jar = urllib.request.urlopen(url).read()
	file = open("mcserver.jar", "wb")
	file.write(jar)
	file.close()
	
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] JAR file has been successfully updated. Restarting the server."]).communicate()
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	subprocess.Popen(["logger", "-i", "-p", "user.info", "[ MINECRAFT ] Server has been successfully restarted. Update process complete!"]).communicate()
	
elif sys.argv[1] == "remove":
	print("Removing minecraft.service")
	os.remove("/etc/systemd/system/minecraft.service")

	print("Removing " + pathway)
	shutil.rmtree(pathway)
	
	if os.path.isfile("/etc/mc_utility.info"):
		print("Removing /etc/mc_utility.info")
		os.remove("/etc/mc_utility.info")
		
	if os.path.isfile("/etc/mcserver_backup.info"):
		print("Removing /etc/mcserver_backup.info")
		os.remove("/etc/mcserver_backup.info")
		
	print("Server Removal Complete!")
	
elif sys.argv[1] == "dlbackup":
	#SECOND ARGUMENT: Location to place ZIP backup
	#THIRD ARGUMENT: IP/Domain of where the backup is located
	if not os.path.isdir(sys.argv[2]):
		print("Unable to find backup directory. Creating directory structure.")
		os.makedirs(sys.argv[2])
		print("Directory created.")
		
	print("Downloading the backup now.")
	os.chdir(sys.argv[2])
	if sys.argv[3].rfind("https://") == 0:
		zip = urllib.request.urlopen(sys.argv[3] + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
	elif sys.argv[3].rfind("http://") == 0:
		temp = sys.argv[3].replace("http://", "https://")
		zip = urllib.request.urlopen(temp + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
	else:
		zip = urllib.request.urlopen("https://" + sys.argv[3] + "/minecraftServer" + str(datetime.datetime.now().date()) + ".zip").read()
	
	file = open("minecraftServer" + str(datetime.datetime.now().date()) + ".zip", "wb")
	file.write(zip)
	file.close()
	
	print("Backup Successfully Downloaded. Creating /etc/mcserver_backup.info")
	file = open("/etc/mcserver_backup.info", "w")
	file.write(sys.argv[2])
	file.close()
	
elif sys.argv[1] == "unpack":
	#SECOND ARGUMENT: Where to unpack the server files to
	#THIRD ARGUMENT: ZIP file to unpack into current environment
	if os.path.isfile("/etc/systemd/system/minecraft.server"):
		print("Shutting down minecraft server.")
		subprocess.Popen(["systemctl", "stop", "minecraft.service"]).communicate()
	
	print("Reading mcserver_backup.info For Backup Directory.")
	file = open("/etc/mcserver_backup.info", "r")
	os.chdir(file.readline())
	file.close()
	
	if os.path.isdir(sys.argv[2]):
		print("Removing Old Directory and All It's Contents")
		shutil.rmtree(sys.argv[2])
	
	print("Unpacking The ZIP File.")
	os.makedirs(sys.argv[2])
	shutil.unpack_archive(sys.argv[3], sys.argv[2], "zip")
	
	print("Files Unpacked. Starting The Server.")
	subprocess.Popen(["systemctl", "start", "minecraft.service"]).communicate()
	
	print("Server Sucessfully Started.")
	print("Creating /etc/mc_utility.info")
	file = open("/etc/mc_utility.info", "w")
	file.write(sys.argv[2])
	file.close()
	