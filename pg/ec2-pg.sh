#!/bin/bash
datadir=/opt/ebs/pg95
logfile=/opt/ebs/pg95.log
pg_ctl=/usr/lib/postgresql/9.5/bin/pg_ctl
mkdir -p $datadir
sudo chown -R postgres:ubuntu $datadir
sudo chown postgres:ubuntu $logfile
sudo su - postgres -c "$pg_ctl -D $datadir initdb -U postgres -W"
sudo su - postgres -c "$pg_ctl -D $datadir -l $logfile start"
