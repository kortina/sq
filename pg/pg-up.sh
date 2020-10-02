#!/bin/bash
sudo su - postgres -c "$PG_CTL -D $PGDATA -l $PGLOG start -c \"config_file=$PGCONF\""