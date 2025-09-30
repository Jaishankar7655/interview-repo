#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Updating system packages ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== Installing prerequisites ==="
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "=== Adding Docker’s official GPG key ==="
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "=== Setting up the Docker repository ==="
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "=== Installing Docker Engine ==="
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "=== Installing Docker Compose (plugin) ==="
sudo apt-get install -y docker-compose-plugin

echo "=== Creating symlink for docker-compose ==="
sudo ln -s /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose || true

echo "=== Adding current user to docker group ==="
sudo usermod -aG docker $USER

echo "=== Verifying installation ==="
docker --version
docker-compose --version

echo "=== Installation complete! Please log out and log back in for group changes to take effect. ==="
