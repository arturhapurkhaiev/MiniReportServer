#!/bin/bash

echo ""
echo "Installing Ubuntu dependencies..."
echo ""

sudo apt update

sudo apt install -y \
git \
make \
docker.io \
docker-compose-plugin \
python3 \
python3-pip \
freetds-dev \
freetds-bin \
dos2unix

echo ""
echo "Starting Docker..."
echo ""

sudo service docker start

echo ""
echo "Adding user to docker group..."
echo ""

sudo usermod -aG docker $USER

echo ""
echo "Ubuntu dependencies installed"
echo ""
