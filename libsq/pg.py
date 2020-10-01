import click
from . import docker, pg, HOST_MAC_IP
from .utils import (
    _docker_exec,
    _ensure_docker,
    _ensure_host,
    _run_command,
    PG_CONTAINER,
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


@pg.command(help="Stop the Mac DaVinci db (to free port 5432).")
def stop_mac():
    _ensure_host()
    cmd = "sudo -u postgres" f" {HOST_MAC_PG_CTL}" " stop" f" -D {HOST_MAC_DATA}"
    _run_command(cmd)


@pg.command(help="Start the Mac DaVinci db.")
def start_mac():
    _ensure_host()
    # TODO: this may require some additional flags
    cmd = "sudo -u postgres" f" {HOST_MAC_PG_CTL}" " start" f" -D {HOST_MAC_DATA}"
    _run_command(cmd)
