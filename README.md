### Getting Started

```sh
brew install duck
pip install click boto3

dk up --build

export SQ__ ....
sq dev bash

```

### sq_pg docker container

Runs `postgres:9.5.23` in docker and fwds host port `54325` to container port `5432`, ie, you can connect to the docker postgres instance on mac port `54325` from Posticco or DaVinci. See `docker-compose.yml` for the rest of the db config.

### sq_tf docker container

Has all the terraform deps and inherits some env vars from the mac host.
