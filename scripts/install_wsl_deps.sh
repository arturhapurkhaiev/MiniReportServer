#!/bin/bash

echo "Installing Ubuntu dependencies..."

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

sudo service docker start

sudo usermod -aG docker $USER

echo ""
echo "Ubuntu dependencies installed"
echo ""
