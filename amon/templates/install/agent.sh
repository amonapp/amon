#!/bin/bash
# Amon Agent install script.
set -e
logfile="amonagent-install.log"

# Set up a named pipe for logging
npipe=/tmp/$$.tmp
mknod $npipe p

# Log all output to a log for error checking
tee <$npipe $logfile &
exec 1>&-
exec 1>$npipe 2>&1
trap "rm -f $npipe" EXIT

function file_exists() {
    [ -f "$1" ]
}

# Basic distro detection
DISTRO='debian' 
if file_exists /etc/debian_version ; then
    DISTRO='debian'
elif file_exists /etc/system-release; then
    DISTRO='rpm'
fi

# Proper distro detection - for Ansible
DISTRO_ID=$(
python - <<EOF
import platform ; print platform.dist()[0].lower()
EOF
)

DISTRO_VERSION=$(
python - <<EOF
import platform
distro = platform.dist()[1].replace(',','.')
distro_list = distro.split(".")
if len(distro_list) > 0 and len(distro) > 0:
    print int(distro_list[0])
EOF
)

function on_error() {
    printf "\033[31m
It looks like you hit an issue when trying to install the Agent.

Troubleshooting and basic usage information for the Agent are available at:

   https://amon.cx/docs#monitoring

If you're still having problems, please send an email to martin@amon.cx
with the contents of amonagent-install.log and we'll do our very best to help you
solve your problem.\n\033[0m\n"
}
trap on_error ERR


if [ -n "$API_KEY" ]; then
    api_key=$API_KEY
fi

if [ ! $api_key ]; then
    printf "\033[31mAPI key not available in API_KEY environment variable.\033[0m\n"
    exit 1;
fi


# Root user detection
if [ $(echo "$UID") = "0" ]; then
    sudo_cmd=''
else
    sudo_cmd='sudo'
fi

function add_repos(){

    printf "\033[92m\n* Adding Repositories ...\n\033[0m\n"

    if [ "$DISTRO" == 'debian' ]; then

        $sudo_cmd sh -c "echo 'deb http://packages.amon.cx/repo amon contrib' > /etc/apt/sources.list.d/amonagent.list"
        $sudo_cmd apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv AD53961F

        # Update once
        $sudo_cmd apt-get update

    elif [ "$DISTRO" == 'rpm' ]; then
        $sudo_cmd sh -c "echo -e '[amon]\nname = Amon.\nbaseurl = http://packages.amon.cx/rpm/\nenabled=1\ngpgcheck=0\npriority=1' > /etc/yum.repos.d/amon.repo"
        $sudo_cmd yum install -y epel-release

    fi


}


function install_agent() {

    # Install the necessary package sources
    if [ "$DISTRO" == 'rpm' ]; then
        printf "\033[92m* Installing the Amon Agent package for RPM distros\n\033[0m\n"

        $sudo_cmd yum -y install amonagent

    elif [ "$DISTRO" == 'debian' ] && ([ "$ARCHITECTURE" == "x86_64" ] || [ "$ARCHITECTURE" == "i686" ]); then
        printf "\033[92m\n* Installing the Amon Agent package for Debian distros\n\033[0m\n"

        $sudo_cmd apt-get install -y --force-yes amonagent

        #Added in reply to https://github.com/amonapp/amon/issues/170
        ARCHITECTURE=`uname -m`
        if [ "$ARCHITECTURE" == "i686" ] ; then
            sed -i "s/\/usr\/bin\/amonagent/\/usr\/bin\/amonagent32/" /etc/systemd/system/amonagent.service
        fi
        
    else
        printf "\033[31mYour OS or distribution are not supported by this install script.
            Please follow the instructions on the Agent setup page:

        https://amon.cx/docs#monitoring\033[0m\n"
        exit;
    fi

    if [ ! -f /etc/opt/amonagent/amonagent.conf ]; then
        printf "\033[92m\n* Adding your API key to the Agent configuration: /etc/opt/amonagent/amonagent.conf\n\033[0m\n"
        $sudo_cmd mkdir -p /etc/opt/amonagent
        $sudo_cmd sh -c "echo  '{\"api_key\": \"$api_key\" , \"amon_instance\": \"{{domain_url}}\"}' > /etc/opt/amonagent/amonagent.conf"
    fi




}


# Show a message about where to go for help.
function print_troubleshooting_instructions() {


printf "\033[32m All done.
   ----------------------------------

   The configuration file for the agent is located in /etc/opt/amonagent/amonagent.conf

   ----------------------------------

   To restart the agent:

   service amonagent restart  (or) systemctl restart amonagent


   ----------------------------------

   The binary for the agent is located in /usr/local/bin/amonagent or /usr/bin/amonagent

   Run:

   amonagent -test

   to collect all available metrics and print the result in the terminal


   ----------------------------------

   You can check for errors in

   /var/log/amonagent/amonagent.log


   For more troubleshooting instructions, please see the Documentation:

        https://amon.cx/docs

\033[0m"


}

add_repos
install_agent
print_troubleshooting_instructions
