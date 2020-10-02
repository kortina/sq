#!/bin/bash
source /home/ubuntu/sq/pg/pg-vars.sh
sudo su - postgres -c "$pg_ctl -D $datadir stop"
