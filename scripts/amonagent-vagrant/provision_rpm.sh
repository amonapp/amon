#!/usr/bin/env bash
echo ">>> Installing Base Packages on RPM"


# Install base packages
sudo yum install -y curl gcc git gcc-c++ make vim epel-release zsh


# Install OhMyZsh
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"


sudo yum install -y gcc-c++ make openssl-devel zsh ruby ruby-devel
sudo gem install sensu-plugins-http sensu-plugins-filesystem-checks sensu-plugins-network-checks sensu-plugins-process-checks sensu-plugins-entropy-checks sensu-plugins-disk-checks sensu-plugins-dns --no-ri --no-rdoc
