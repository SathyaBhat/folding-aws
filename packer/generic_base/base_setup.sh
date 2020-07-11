#!/bin/bash

set -e

echo "Update packages"
sudo apt update 

echo "Removing old Docker stuff"
sudo apt remove docker docker-engine docker.io containerd runc

echo "Install deps"
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    git \
    vim \
    htop \
    zsh


echo "Setup Docker repos"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

echo "Install Docker"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

echo "Install Compose"
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

