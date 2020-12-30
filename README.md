Tools for video editing / using a Postgres server on AWS EC2 for DaVinci Resolve remote collaboration.

NB / warning: There is a lot of configuration specific to particular projects throughout that should really be moved into separate config files.

### Setup

```sh
brew install duck
pip install click boto3

dk up --build

export SQ__ ....
sq dev bash

```

### sq

This is a click command line tool with some of these commands:

```sh

❯ sq           
dev     -- Local (mac host) commands.
docker  -- Commands to be run inside the docker host...
ffmpeg  -- ffmpeg commands.
pg      -- pg commands.
tf      -- Terraform commands.

❯ sq dev       
bash          -- Start bash in docker container, inheriting...
bootstrap     -- pre bootstrap.
mk-opt-ebs    -- Create mac host /opt/ebs/pgdata
project-init  -- Init project directory on mac host in...
s3-down       -- Download s3 to local.
s3-up         -- Push local up to s3.
scp           -- scp to the aws docker host.
ssh           -- ssh to the aws docker host.
tail-davinci  -- Tail the DaVinci Resolve log on mac host.
tail-pg       -- Tail the pg log on host.
tail-pg-ec2   -- Tail the pg log on ec2.
tunnel        -- Tunnel to the aws docker pg db.

❯ sq docker
pg-dump     -- pg_dump the Mac DaVinci db.
pg-restore  -- restore db.
tf-apply    -- Apply tf plan in docker.
tf-plan     -- Run tf plan in docker.

❯ sq docker
resolve-mp4  -- Convert to mp4 for import to DaVinci Resolve.

❯ sq pg         
dump                  -- pg_dump the Mac DaVinci db.                                                                                                                                                       
ec2-dump              -- backup all ec2 dbs in cluster to s3                                                                                                                                               
mac-down              -- Stop the Mac DaVinci db (to free port 5432).                                                                                                                                      
mac-up                -- Start the Mac DaVinci db.                                                                                                                                                         
restore-ec2  restore  -- restore db.  

❯ sq tf      
apply  -- Apply tf plan in docker.
plan   -- Run tf plan in docker.

```

### sq_pg docker container

Runs `postgres:9.5.23` in docker and fwds host port `54325` to container port `5432`, ie, you can connect to the docker postgres instance on mac port `54325` from Posticco or DaVinci. See `docker-compose.yml` for the rest of the db config.

### sq_tf docker container

Has all the terraform deps and inherits some env vars from the mac host.
