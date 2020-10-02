#!/bin/bash
source /home/ubuntu/sq/pg/pg-vars.sh
sudo su - postgres -c "$pg_ctl -D $datadir -l $logfile -o \"--config_file=$conf\" start"
