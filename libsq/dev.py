import click
import os
from . import dev
from .utils import (
    _aws_kwargs,
    _docker_exec,
    _ensure_host,
    _run_command,
    _running_ec2_docker_public_hostname,
    _sq_path_join,
)

EC2_USER = "ubuntu"  # ec2-user


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
@click.option(
    "--print-only", is_flag=True, help="Print cmd (for sending to someone else)."
)
def tunnel(host=None, local_port=None, print_only=None):
    if host is None:
        host = _running_ec2_docker_public_hostname()

    user = EC2_USER
    info = "---------------- local_port:remote_addr:remote_port remote_user@remote_host ----------------"
    cmd = f"ssh -vvv -TnN -L {local_port}:0.0.0.0:5432 {user}@{host}"
    if print_only:
        print(info)
        print(cmd)
    else:
        _run_command(cmd, capture_output=False)


@dev.command(help="ssh to the aws docker host.")
def ssh():
    host = _running_ec2_docker_public_hostname()
    user = EC2_USER
    cmd = f"ssh {user}@{host}"
    _run_command(cmd, capture_output=False)


@dev.command(help="pre bootstrap.")
def pre_bootstrap():
    home = os.environ.get("HOME")
    _scp(f"{home}/.ssh/sq_github_deploy_key", None)
    _scp(_sq_path_join("tf/modules/ec2_docker/ec2-bootstrap.sh"), None)
    _scp(_sq_path_join("tf/modules/ec2_docker/ec2-mount-vol.sh"), None)

    host = _running_ec2_docker_public_hostname()
    user = EC2_USER
    k = _aws_kwargs()
    r = k["region_name"]
    s = k["aws_secret_access_key"]
    a = k["aws_access_key_id"]

    ssh_run = f"""ssh {user}@{host}"""
    _run_command(f"{ssh_run} touch .bash_profile", capture_output=False)

    cmd = (
        f"""{ssh_run}"""
        f""" "grep -q AWS_ACCESS_KEY_ID .bash_profile || echo \\"export AWS_DEFAULT_REGION='{r}';"""
        f""" export AWS_SECRET_ACCESS_KEY='{s}';"""
        f""" export AWS_ACCESS_KEY_ID='{a}';\\" """
        """ >> .bash_profile " """
    )

    _run_command(cmd, capture_output=False)


@dev.command(help="scp to the aws docker host.")
@click.argument("local_file_path", type=click.Path(exists=True), required=True)
@click.argument("remote_path", type=click.STRING, required=False)
def scp(local_file_path, remote_path):
    _scp(local_file_path, remote_path)


def _scp(local_file_path, remote_path):
    host = _running_ec2_docker_public_hostname()
    user = EC2_USER
    if not remote_path:
        remote_path = ""
    cmd = f"scp {local_file_path} {user}@{host}:{remote_path}"
    _run_command(cmd, capture_output=False)
