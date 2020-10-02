#!/bin/bash
sudo su - postgres -c "$PG_CTL -D $PGDATA  -o \"--config_file=$PGCONF\" start"