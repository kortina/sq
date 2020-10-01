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
sudo apt-get install -y postgresql-client
sudo apt-get install -y python3 python3-pip
sudo pip3 install boto3 click ipython
sudo ln -s /usr/bin/python3 /usr/bin/python
# so you can:
# psql postgres://postgres:DaVinci@localhost:5432/ # on ec2

u=`whoami`
sudo usermod -aG docker "$u"

# ensure keyfile is linked to github:
test -e ~/.ssh || mkdir ~/.ssh
touch ~/.ssh/config
# for some reason git does not seem to respect this:
grep -q sq_github_deploy_key ~/.ssh/config || cat >> ~/.ssh/config <<-EOF
Host github.com
    HostName github.com
    IdentityFile ~/sq_github_deploy_key
    IdentitiesOnly yes
EOF
# so also just do this:
export_ssh_command="export GIT_SSH_COMMAND='ssh -i ~/sq_github_deploy_key'"
grep -q GIT_SSH_COMMAND ~/.bash_profile || echo "$export_ssh_command" >> ~/.bash_profile
eval "$export_ssh_command"

git clone git@github.com:kortina/sq.git
cd sq