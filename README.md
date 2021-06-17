# MC-Utility
Minecraft Server Management Utility

## ABOUT
I created this utility in an effort to simplify some of the management aspects of Minecraft servers down to single line commands with minimal input required from the user. This utility was created and tested on a Debian based distro and should work on similar. Redhat distros will be explored in the future and the utility will be updated to be more robust with those Linux distros.

## FUNCTIONS

### General
The utility will always require at least one parameter which is the function to be executed. At the moment if no parameter is provided the utility will silently finish.

### Install
**Command:** `python3 mc_utility.py install <pathway>` \
The install function requires a single parameter specifying the pathway where the server JAR and related files will be installed. If the directory doesn't exist the utility will create it and any required parents. The specified pathway will then be stored in `mc_utility.info` file locate in `/etc/`. Next, the utility will pull the HTML for the [Minecraft Server Download](https://www.minecraft.net/en-us/download/server) page scraping the most current link to download the Minecraft server. The server JAR file is then moved to the directory specified and `eula.txt` is created along with `start_minecraft_server.sh`. Once complete `minecraft.service` is created in `/etc/systemd/system` making the server a service that can run in the background

### Backup
**Command:** `python3 mc_utility.py backup` \
The backup feature requires no additional parameters and compresses all files/directories located in the install pathway specified in `mc_utility.info` into a ZIP file. The resulting ZIP file is transferred to the following pathway located at `/var/www/html`. This pathway is the default pathway that the Apache2 web server uses to serve web pages. 

NOTE: This function will likely be updated in the future to include an argument for specifying a custom path which will be stored in `mc_utility.info`

### Update
**Command:** `python3 mc_utility.py update` \
The update function requires no additional parameters and begins the process by shutting down the server. Once shutdown the utility will pull the HTML for the [Minecraft Server Download](https://www.minecraft.net/en-us/download/server) page scraping the most current link to download the Minecraft server. After the server is downloaded the server is restarted.

### Remove
**Command:** `python3 mc_utility.py remove` \
The remove function requires no additional parameters and simply removes the following files and directories:
* The all files/directories located in the server install pathway specified in `mc_utility.info`
* `/etc/systemd/system/minecraft.service`
* `/etc/mc_utility.info`
* `/etc/mcserver_backup.info`

### DLBackup
**Command:** `python3 mc_utility.py dlbackup <pathway> <IP/Domain>` \
The dlbackup function allows you to download server backups if they're web accessible and it requires two additional parameters. The first specifies the pathway where the server backup will be downloaded to. The second specifies the IP or domain where the servercan be downloaded. If possible the utility will attempt to download the file using a secure connection. 

NOTE: The utility appends a hardcoded file name to the domain provided. The format of the file name is the same that the back up function uses `minecraftServerYYYY-MM-DD.zip`
### Unpack
**Command:** `python3 mc_utility.py unpack <pathway> <ZIP_File_Name>` \

