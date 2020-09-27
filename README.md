### Getting Started

```sh
dk up --build

export SQ__ ....
sq dev bash

```

### pg docker container

Runs `postgres:9.5.23` in docker and fwds host port `54325` to container port `5432`, ie, you can connect to the docker postgres instance on mac port `54325` from Posticco or DaVinci. See `docker-compose.yml` for the rest of the db config.

### stop davinci postgres

sudo -u postgres /Library/PostgreSQL/9.5/bin/pg_ctl stop -D /Library/PostgreSQL/9.5/data
