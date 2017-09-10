#!/usr/bin/env bash
echo ">>> Installing Base Packages"

# Update
sudo apt-get update

# Install base packages
sudo apt-get install -qq curl build-essential zsh vim


# Install OhMyZsh
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

