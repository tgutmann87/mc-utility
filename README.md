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

##### Update

##### Remove

##### DLBackup

##### Unpack
