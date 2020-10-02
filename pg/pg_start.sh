#!/bin/bash
datadir=/opt/ebs/pg95
logfile=/opt/ebs/pg95.log
pg_ctl=/usr/lib/postgresql/9.5/bin/pg_ctl
sudo su - postgres -c "$pg_ctl -D $datadir -l $logfile start"
