import click
from . import dev
from .utils import (
    _docker_exec,
    _ensure_host,
    _run_command,
    _running_ec2_docker_public_hostname,
)


@dev.command(help="Start bash in docker container, inheriting SQ__ prefixed env vars.")
@click.option("--no-inherit-env", is_flag=True, help="Do NOT inherit SQ__ env vars.")
def bash(no_inherit_env):
    _docker_exec("bash", not no_inherit_env)


@dev.command(help="Tail the DaVinci Resolve log on mac host.")
@click.argument("lines", type=int, required=False)
def tail_davinci(lines):
    _ensure_host()
    cmd = "tail -f"
    if lines:
        cmd = f"{cmd} -n {lines} "
    cmd = f'{cmd} "/Library/Application Support/Blackmagic Design/DaVinci Resolve/logs/davinci_resolve.log" '
    _run_command(cmd)


@dev.command(help="Create mac host /opt/ebs")
def mk_opt_ebs():
    p = "/opt/ebs/pgdata"
    _run_command(f"sudo mkdir -p {p}")
    _run_command(f'sudo chown -R "`id -u -n`":staff {p}')


@dev.command(help="Tunnel to the aws docker pg db.")
@click.argument("host", type=click.STRING, required=False)
@click.option("--local-port", type=click.STRING, required=False, default="54320")
def tunnel(host=None, local_port="54320"):
    if host is None:
        host = _running_ec2_docker_public_hostname()

    user = "ubuntu"
    cmd = f"ssh -vvv -TnN -L {local_port}:0.0.0.0:5432 {user}@{host}"
    _run_command(cmd, capture_output=False)
