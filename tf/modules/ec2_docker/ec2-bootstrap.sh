#!/bin/bash
# bootstrap deps on ec2
sudo apt-get -y update
sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get -y update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io
sudo apt-get install -y docker-compose
sudo apt-get install -y postgresql postgresql-contrib
# so you can:
# psql postgres://postgres:DaVinci@localhost:5432/ # on ec2


u=`whoami`
sudo usermod -aG docker "$u"

eval `ssh-agent`
ssh-add sq_github_deploy_key
git clone git@github.com:kortina/sq.git
cd sq
# docker-compose up -d