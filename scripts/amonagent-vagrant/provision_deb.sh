#!/usr/bin/env bash
echo ">>> Installing Base Packages"

# Update
sudo apt-get update

# Install base packages
sudo apt-get install -qq curl unzip git-core ack-grep software-properties-common build-essential zsh  ruby ruby-dev vim

sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -qq ansible

# Install OhMyZsh
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

sudo gem install sensu-plugins-http sensu-plugins-filesystem-checks sensu-plugins-network-checks sensu-plugins-process-checks sensu-plugins-entropy-checks sensu-plugins-disk-checks sensu-plugins-dns --no-ri --no-rdoc


