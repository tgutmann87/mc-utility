# MC_Utility
Minecraft Server Management Utility

## ABOUT
   I created this utility in an effort to simplify some of the management aspects of Minecraft servers down to single line commands with minimal input required from the user. This utility was created and tested on a Debian based distro and should work on similar. Redhat distros will be explored in the future and the utility will be updated to be more robust with those Linux distros.
  

## FUNCTIONS
**General**\
The utility will always require at least one parameter which is the function to be executed. At the moment if no parameter is provided the utility will silently finish.

---

**Install**\
Command: `python3 mc_utility.py install <pathway>` 

The install function requires a single parameter specifying the pathway where the server JAR and related files will be installed. If the directory doesn't exist the utility will create it and any required parents. The specified pathway will then be stored in `mc_utility.info` file locate in `/etc/mc_utility`. Next, the utility will use the Minecraft API at [Minecraft API: Version Manifest](https://launchermeta.mojang.com/mc/game/version_manifest.json) to download the most recent server JAR that has been marked as official release. The server JAR file is then moved to the directory specified and `eula.txt` is created along with `start_minecraft_server.sh`. Once complete `minecraft.service` is created in `/etc/systemd/system` making the server a service that can run in the background.

---

**Set Configuration**\
Command: `setConfiguration <Property_to_Configure> <Property_Value>`

At this time the configuration command is rather simple and currently allows for easily manipulation of the properties within the `/etc/mc_utility/mc_utility.info` file. The property provided must appear exactly as it does in the `mc_utility.info` file. This command will be updated in future releases to support more functionality.

---

**List Configuration**\
Command: `listConfiguration`

This command simply lists the MC_Util configurations listed in the `/etc/mc_utility/mc_utility.info` file located on the server.

---

**Backup**\
Command: `backup` 

The backup feature requires no additional parameters and compresses all files/directories located in the install pathway specified in `mc_utility.info` into a ZIP file. The resulting ZIP file is transferred to the following pathway located at `/var/www/html`. This pathway is the default pathway that the Apache2 web server uses to serve web pages. 

NOTE: This function will likely be updated in the future to include an argument for specifying a custom path which will be stored in `mc_utility.info`

---

**Update**\
Command: `update` 

The update function requires no additional parameters and begins the process by shutting down the server. Once shutdown the utility will access the Minecraft API at [Minecraft API: Version Manifest](https://launchermeta.mojang.com/mc/game/version_manifest.json) and parse through it to find the most recent server release. Once found the download link is obtained, saved locally and then used to pull the new server JAR. Once the update process is complete the Minecraft server is restarted.

---

**Remove**\
Command: `remove` 

The remove function requires no additional parameters and simply removes the following files and directories:
* The all files/directories located in the server install pathway specified in `mc_utility.info`
* `/etc/systemd/system/minecraft.service`
* `/etc/mc_utility/mc_utility.info`

---

**DLBackup (Currently Deprecated)**\
Command: `dlbackup <pathway> <IP/Domain>` 

The dlbackup function allows you to download server backups if they're web accessible and it requires two additional parameters. The first specifies the pathway where the server backup will be downloaded to. The second specifies the IP or domain where the servercan be downloaded. If possible the utility will attempt to download the file using a secure connection. 

NOTE: The utility appends a hardcoded file name to the domain provided. The format of the file name is the same that the back up function uses `minecraftServerYYYY-MM-DD.zip`

---

**Unpack**\
Command: `unpack <pathway> <ZIP_File_Name>` 

The unpack function allows you to unpack a server backup and requires two additional commands. The first parameter is the pathway where the server backup should be unpacked to. If the directory doesn't exist the uitility will create it and any required parents. The pathway will also be stored in the `/etc/mc_utility/mc_utility.info`. Additionally, if the directory does exist it will be deleted and re-created with the assumption there was a working version of the server already in that directory. The second parameter is simply the ZIP backup that you'd like to unpack.

---

**List Server Properties**\
Command: `listServerProperties`

Displayes the Minecraft `server.properties` configuration file.

---

**Change Server Properties**\
Command: `changeServerProperties <property_to_change> <property_value>`

Allows the changing of properties in the `server.properties` configuration file.

You will have to specify the property from `server.properties` exactly as it appears in the file. In addition please be aware of the following value restrictions for each type of property:
* Integer values are restricted to values between 1 and 29,999,984.
* String values are restricted to 512 characters. Please note any string with spaces will require `""`.
* Boolean values are restricted to strings `true` or `false`.
* Values with limited selections (i.e. difficulty) have buit in checks that verrify the value provided matches one within it's set.

---
