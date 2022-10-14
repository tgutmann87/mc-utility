#Series of import statements
import sys
import MCUtil

utility = MCUtil.MCUtil()

#Checking the first variable to see what function to execute.
#FIRST ARGUMENT: Function to execute.
if sys.argv[1] == "install":
	utility.install()

elif sys.argv[1] == "setConfiguration":
	#SECOND ARGUMENT: Option within mc_utility.info to change.
	#THIRD ARGUMENT: The value for the option that you're trying to change.
	utility.setConfiguration(sys.argv[2], sys.argv[3])
	
elif sys.argv[1] == "listConfiguration":
	utility.listConfiguration()

elif sys.argv[1] == "backup":
	utility.backupServer()
	
elif sys.argv[1] == "update":
	utility.update()
	
elif sys.argv[1] == "remove":
	utility.remove()
	
#elif sys.argv[1] == "dlbackup":
	#SECOND ARGUMENT: Location to place ZIP backup.
	#THIRD ARGUMENT: IP/Domain of where the backup is located.

elif sys.argv[1] == "unpack":
	#SECOND ARGUMENT: Where to unpack the server files to
	#THIRD ARGUMENT: ZIP file to unpack into current environment
	utility.unpackServer(sys.argv[2], sys.argv[3])

elif sys.argv[1] == "listServerProperties":
	utility.listServerProperties()
		
elif sys.argv[1] == "changeServerProperties":
	#SECOND ARGUMENT: A property within the server.properties file.
	#THIRD ARGUMENT: The value which will be set for the specified property.
	utility.changeServerProperties()

#Writes any configuration changes to mc_utility.info prior to ending.
#configParser.write(open("/etc/mc_utility/mc_utility.info", "w"), space_around_delimiters=False)