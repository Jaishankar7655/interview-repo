#!/bin/bash
# -----------------------------------------
# Docker & Docker Compose Installation Script
# Works on Ubuntu/Debian-based systems
# -----------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

echo "-----------------------------------------"
echo "🚀 Starting Docker Installation"
echo "-----------------------------------------"

# Update existing packages
sudo apt update -y
sudo apt upgrade -y

# Install required dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker APT repository
sudo add-apt-repository \
   "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) stable"

# Update package index again
sudo apt update -y

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Check Docker installation
echo "✅ Docker installed successfully!"
docker --version

echo "-----------------------------------------"
echo "🐳 Installing Docker Compose"
echo "-----------------------------------------"

# Get latest docker-compose release version dynamically
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)

# Download Docker Compose binary
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Apply executable permissions
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
echo "✅ Docker Compose installed successfully!"
docker-compose --version

echo "-----------------------------------------"
echo "🎉 Docker & Docker Compose Installation Complete!"
echo "-----------------------------------------"

