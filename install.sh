#!/bin/bash
# The one-line installer for AmonOne
# Author: Martin Rusev <martin@amon.cx>
set -e
command_exists() {
	type "$1" &> /dev/null ;
}

file_exists() {
	[ -f "$1" ]
}

ARCH=
DISTRO=
UBUNTU=0
PYTHON=python
VERBOSE=0
INSTALL_AMON=0 


# Debian based distros - Tested and supported on : Debian, Ubuntu
if file_exists /etc/debian_version ; then
	DISTRO='debian'
# RPM based distros - Tested and supported on : Fedora, CentOS, Amazon Linux AMI
elif file_exists /etc/redhat-release ; then
	DISTRO='rpm'
elif file_exists /etc/system-release ; then
	DISTRO='rpm'
else 
	echo "Your operating system is not supported at the moment"
	exit
fi

if file_exists  "/etc/lsb-release"; then
	if cat /etc/lsb-release | grep 'buntu' >> /dev/null; then
		UBUNTU=1
	fi
fi 

# Check if it is 32 or 64 bit machine
MACHINE_TYPE=`uname -m`
if [ "$MACHINE_TYPE" == 'i686' ]; then
	# 32-bit
	ARCH='32bit'
else
	# 64-bit
	ARCH='64bit'
fi


# Set variables for the installation
mongo_check=$(ps aux | grep -c mongo) # Check if mongo is running
amon_log_dir="/var/log/amonone/"

install_amon() {
	INSTALL_AMON=1

	# Install easy_install if necessary
	if ! command_exists easy_install ; then
		wget "http://peak.telecommunity.com/dist/ez_setup.py" 
		sudo python ez_setup.py
		rm -f ez_setup.py
	fi

	# Install depencies
	if [ "$DISTRO" == 'debian' ]; then
		if dpkg-query -s gcc python-dev sysstat >> /dev/null ; then
			echo "*** AmonOne requirements already installed"
		else
			echo "** Installing AmonOne requirements"
			sudo apt-get -y install gcc python-dev sysstat
		fi

		if dpkg-query -W gcc python-dev sysstat ; then 
			echo "** AmonOne requirements successfuly installed!"
		fi
	fi

	if [ "$DISTRO" == 'rpm' ]; then 
		if rpm --quiet -q gcc python-devel sysstat ; then
			echo "*** AmonOne requirements already installed"
		else 
			echo "** Installing AmonOne requirements"
			sudo yum -t -y install gcc python-devel sysstat
		fi

		if rpm --quiet -q gcc python-devel sysstat; then 
			echo "** AmonOne requirements successfuly installed!"
		fi
	fi


echo "\033[0;34mCloning AmonOne...\033[0m"
hash git >/dev/null && /usr/bin/env git clone https://github.com/martinrusev/amonone.git ~/amonone || {
  echo "git not installed"
  exit
}
	cd ~/amonone

	sudo python setup.py install # Install Amon and all the dependecies
	python generate_config.py # Generate the configuration file

	# Copy the generated configuration file from the current directory
	sudo cp amonone.conf /etc/amonone.conf

	# Copy the daemon
	sudo cp contrib/amonone /etc/init.d/amonone
	
	# Copy the collector daemon
	sudo cp contrib/amonone-collector /etc/init.d/amonone-collector

	# make the web app daemon executable
	sudo chmod +x /etc/init.d/amonone
	
	# make the collector daemon executable
	sudo chmod +x /etc/init.d/amonone-collector

	# Add the daemons to the startup list
	if [ "$DISTRO" == 'debian' ]; then
		sudo update-rc.d amonone defaults > /dev/null
		sudo update-rc.d amonone-collector defaults > /dev/null
	elif [ "$DISTRO" == 'rpm' ]; then
		sudo chkconfig --add amonone > /dev/null
		sudo chkconfig --add amonone-collector > /dev/null
	fi

	# Create a directory for the log files
	sudo mkdir -p "$amon_log_dir"
	sudo touch "$amon_log_dir/amonone-mailer.log"
	
}
 
 

# Install MongoDB
install_mongodb() {

   if [ "$DISTRO" == 'debian' ]; then
		sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
   
			if ! file_exists "/etc/apt/sources.list.d/10gen.list"; then

				if [ "$UBUNTU" == 1 ]; then

cat <<EOL > 10gen.list
deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen
EOL
				else # debian

cat <<EOL > 10gen.list
deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen
EOL
				fi # is_ubuntu END 

				sudo cp 10gen.list /etc/apt/sources.list.d/10gen.list
				sudo apt-get update

			fi # file exists

			sudo apt-get install mongodb-10gen
		
   fi # DISTRO = debian


   if [ "$DISTRO" == 'rpm' ]; then

		if ! file_exists "/etc/yum.repos.d/10gen.repo"; then

			if [ "$ARCH" == '64bit' ]; then
cat <<EOL > 10gen.repo
[10gen]
name=10gen Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64
gpgcheck=0
enabled=1
EOL
			# 32 bit
			else 
cat <<EOL > 10gen.repo
[10gen]
name=10gen Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/i686
gpgcheck=0
enabled=1
EOL
			fi # ARCH END

			sudo cp 10gen.repo /etc/yum.repos.d/10gen.repo

		fi # file exists 

		yum install mongo-10gen mongo-10gen-server -y
		chkconfig mongod on

   fi # DISTRO = rpm

}


#Start Mongo
start_mongodb()
{

	if [ "$DISTRO" == 'rpm' ]; then
	   sudo service mongod start
	else 
		sudo /etc/init.d/mongodb start
	fi 

	sleep 5 # Wait for Mongo to write the journal files
}

echo ""

# Install MongoDB if it is not installed on the system
if ! command_exists mongo ; then
	# Check one more time, the value should be 1
	if [ $mongo_check = '1' ]; then	 
		install_mongodb
		start_mongodb
	fi
fi


# Show a message about where to go for help.
print_troubleshooting_instructions() {
	echo
	echo "For troubleshooting instructions, please see the AmonOne User Guide:"
	echo "https://github.com/martinrusev/amonone/wiki"
}

restart_amonone() {

  # All done!
  if  pgrep -x amon > /dev/null; then
	  echo "*** AmonOne succesfully updated"
	  sudo /etc/init.d/amonone restart
	  sudo /etc/init.d/amonone-collector restart
  else
	  echo "*** AmonOne succesfully installed"
	  sudo /etc/init.d/amonone start
	  sudo /etc/init.d/amonone-collector start
	  echo "*** Starting AmonOne "
  fi

}

install_amon
if [ "$INSTALL_AMON" == 1 ]; then
	install_mongodb
	restart_amonone
	print_troubleshooting_instructions
fi
