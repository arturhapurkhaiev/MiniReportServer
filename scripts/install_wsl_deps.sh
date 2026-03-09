#!/bin/bash

echo "Installing Ubuntu dependencies..."

sudo apt update

sudo apt install -y \
git \
make \
docker.io \
docker-compose \
python3 \
python3-pip \
freetds-dev \
freetds-bin

echo "WSL dependencies installed"
