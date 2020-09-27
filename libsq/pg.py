import click
from . import docker, pg, HOST_MAC_IP
from .utils import _docker_exec, _ensure_docker, _run_command


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
    _run_command(cmd, False)


@pg.command(help="pg_dump the Mac DaVinci db.")
@click.argument("dbname", type=click.STRING, required=True)
def dump(dbname):
    _docker_exec("./sq docker pg-dump {0}".format(dbname), True)
