#!/bin/bash
# Create the file repository configuration:
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import the repository signing key:
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update the package lists:
sudo apt-get update

# Install the latest version of PostgreSQL.
# If you want a specific version, use 'postgresql-12' or similar instead of 'postgresql':
sudo apt-get -y install postgresql-9.5 postgresql-contrib-9.5

mkdir -p $PGDATA
mkdir -p $PGLOG
sudo chown -R postgres:ubuntu $PGDATA
sudo chown postgres:ubuntu $PGLOG
sudo su - postgres -c "$PG_CTL -D $PGDATA initdb -U postgres -W"