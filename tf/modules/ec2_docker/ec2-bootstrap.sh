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

# Create the bash profile:
cat << EOF > ~/.bash_profile
alias dk='docker-compose' 
source ~/.aws
export GIT_SSH_COMMAND='ssh -i ~/sq_github_deploy_key'
export PGDATA=/opt/ebs/pg95
export PGLOGFILE=/opt/ebs/pg95.log
export PGCONF=/home/ubuntu/sq/pg/postgresql95.conf
export PG_CTL="/usr/lib/postgresql/9.5/bin/pg_ctl"
export PATH="\$PATH:/usr/lib/postgresql/9.5/bin:~/sq:~/sq/pg"
EOF

source ~/.bash_profile

git clone git@github.com:kortina/sq.git
cd sq