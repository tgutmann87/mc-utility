# mc-utility
Minecraft Server Management Utility

### ABOUT
I created this utility in an effort to simplify some of the management aspects of Minecraft servers down to single line commands with minimal input required from the user. This utility was created and tested on a Debian based distro and should work on similar. Redhat distros will be explored in the future and the utility will be updated to be more robust with those Linux distros.

### FUNCTIONS

##### General
The utility will always require at least one parameter which is the function to be executed. At the moment if no parameter is provided the utility will silently finish.
##### Install
**Command:** `python3 mc_utility.py install <pathway>` \
The install function requires a second parameter which will specify the pathway where the server JAR and all related files will be installed. The utility will create the pathway if it doesn't already exist and then save the pathway to `mc_utility.info` file locate in `/etc/`. It then retrieves the Minecraft server download page and scrapes it for the current link to download the `server.jar` file. Using that the JAR file is downloaded to the specified pathway. The utility then creates service file in `/etc/systemd/system` called `minecraft.service`. Additionally the start_minecraft_server.sh is created in the specified pathway to help start the server. Lastly, file permissions are modified as necessary and then the server is started.

##### Backup
**Command:** `python3 mc_utility.py backup` \
The backup feature takes all files and directories that are located in the install pathway that's recorded in the `mc_utility.info` file and compresses/archives them into a ZIP file. The resulting ZIP file is then transferred to the following pathway located at `/var/www/html`. This pathway is the default pathway that the Apache2 web server uses to serve web pages. This function will likely include an inital argument that includes the pathway of where the backup is to be stored which will then be stored in `mc_utility.info` for future backup calls.

##### Update
**Command:** `python3 mc_utility.py update` \

##### Remove
**Command:** `python3 mc_utility.py remove` \

##### DLBackup
**Command:** `python3 mc_utility.py dlbackup <pathway> <IP/DNS>` \

##### Unpack
**Command:** `python3 mc_utility.py unpack <pathway> <ZIP_File_Name>` \
