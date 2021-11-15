import click
import datetime
import re
from . import docker, pg, HOST_MAC_IP
from .utils import (
    _docker_exec,
    _ensure_docker,
    _ensure_host,
    _run_command,
    _running_ec2_docker_public_hostname,
    _ssh_run,
    EC2_USER,
    PG_CONTAINER,
    S3_BUCKET,
)

HOST_MAC_PG_CTL = "/Library/PostgreSQL/9.5/bin/pg_ctl "
HOST_MAC_DATA = "/Library/PostgreSQL/9.5/data"


@docker.command(help="pg_dump the Mac DaVinci db.")
@click.argument("dbname", type=click.STRING, required=True)
def pg_dump(dbname):
    _ensure_docker()
    cmd = (
        ' PGPASSWORD="$MAC_PG_PASS"'
        " pg_dump"
        f" -h {HOST_MAC_IP}"
        "  -U $MAC_PG_USER"
        f" -d {dbname}"
        f" > {dbname}.dump.sql"
    )
    _run_command(cmd)


@pg.command(help="pg_dump the Mac DaVinci db.")
@click.argument("dbname", type=click.STRING, required=True)
def dump(dbname):
    _docker_exec("./sq docker pg-dump {0}".format(dbname), True)


@docker.command(help="restore db.")
@click.argument("dbname", type=click.STRING, required=True)
@click.argument("dumpfile", type=click.Path(exists=True), required=True)
def pg_restore(dbname, dumpfile):
    _ensure_docker()
    _run_command(
        (
            ' PGPASSWORD="$POSTGRES_PASSWORD"'
            " psql"
            f" -h {PG_CONTAINER}"
            f' -U "$POSTGRES_USER"'
            f" -d {dbname}"
            f" -f {dumpfile}"
        )
    )


@pg.command(help="restore db.")
@click.argument("dbname", type=click.STRING, required=True)
@click.argument("dumpfile", type=click.Path(exists=True), required=True)
def restore(dbname, dumpfile):
    _docker_exec(f"./sq docker pg-restore {dbname} {dumpfile}", True)


@pg.command(help="restore db.")
@click.argument("dbname", type=click.STRING, required=True)
@click.argument("dumpfile", type=click.Path(exists=True), required=True)
def restore_ec2(dbname, dumpfile):
    # sq dev scp cyberpunk202x.dump.sql
    # ssh run:
    # cd ~/sq
    # mv ../___________sql ./
    # ./sq pg restore cyberpunk202x cyberpunk202x.dump.sql
    raise Exception("NOT_IMPLEMENTED")
    # _docker_exec(f"./sq docker pg-restore {dbname} {dumpfile}", True)


def _mac_is_running():
    # lsof should show ssh bound to 5432 on local, not postgres
    port = "5432"  # postgres port
    cmd = "lsof -i :{}".format(port)
    o = _run_command(cmd, capture_output=True)
    rgx = re.compile(r"^ControlCe")
    if o:
        for line in o.split("\n"):
            print(line)
            if rgx.search(line):
                return True
    return False


@pg.command(help="Stop the Mac DaVinci db (to free port 5432).")
def mac_down():
    _ensure_host()

    # kill the DaVinci pg server:
    click.secho("WARNING: killing Mac Postgres process", fg="red")
    cmd = (
        f"test -e {HOST_MAC_PG_CTL} "
        f" &&  sudo -u postgres {HOST_MAC_PG_CTL} stop"
        f" -D {HOST_MAC_DATA}"
    )
    _run_command(cmd)

    # kill homebrew pg server:
    # rob is pinned to @12
    cmd = "brew services | grep -q postgresql && brew services stop postgresql@12"
    _run_command(cmd)

    if _mac_is_running():
        raise Exception(
            "ERROR: Tried to kill mac pg, but process run by postgres user is still bound to localhost 5432."
        )


@pg.command(help="Start the Mac DaVinci db.")
def mac_up():
    _ensure_host()
    # TODO: this may require some additional flags
    cmd = "sudo -u postgres" f" {HOST_MAC_PG_CTL}" " start" f" -D {HOST_MAC_DATA}"
    _run_command(cmd)


@pg.command(help="backup all ec2 dbs in cluster to s3")
def ec2_dump():
    # TODO: we could also backup just a single project db here...
    user = EC2_USER
    host = _running_ec2_docker_public_hostname()
    n = datetime.datetime.now()
    d = n.strftime("%Y-%m-%d--%H-%M-%S")
    fn = f"cluster-{d}.sql"
    local_path = f"db/{fn}"
    cmd = f"pg_dumpall -U postgres | gzip > {local_path}"
    _ssh_run(cmd, user=user, host=host)

    d = n.strftime("%Y/%m/%d")
    s3_path = f"s3://{S3_BUCKET}/backups/{d}/{fn}"
    cmd = f"aws s3 cp {local_path} {s3_path} && rm {local_path}"
    _ssh_run(cmd, user=user, host=host)
