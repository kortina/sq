#!/bin/bash
sudo su - postgres -c "$PG_CTL -D $PGDATA stop"
