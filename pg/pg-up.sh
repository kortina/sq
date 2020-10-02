#!/bin/bash
sudo su - postgres -c "$PG_CTL -D $PGDATA -l $PGLOGFILE start -c \"config_file=$PGCONF\""