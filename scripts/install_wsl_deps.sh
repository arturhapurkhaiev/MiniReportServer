#!/bin/bash

echo ""
echo "Installing Ubuntu dependencies..."
echo ""

sudo apt update

sudo apt install -y \
git \
make \
docker.io \
python3 \
python3-pip \
freetds-dev \
freetds-bin \
dos2unix

echo ""
echo "Installing docker-compose..."
echo ""

sudo pip3 install docker-compose

echo ""
echo "Starting Docker..."
echo ""

sudo service docker start

echo ""
echo "Adding user to docker group..."
echo ""

sudo usermod -aG docker $USER

echo ""
echo "Fixing git safe directory..."
echo ""

git config --global --add safe.directory /opt/dwh

echo ""
echo "Ubuntu dependencies installed"
echo ""
