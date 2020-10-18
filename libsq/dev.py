import click
import getpass
import os
from . import dev
from .utils import (
    _aws_kwargs,
    _docker_exec,
    _duck,
    _ensure_host,
    _run_command,
    _running_ec2_docker_public_hostname,
    _s3_local_project_path,
    _ssh_add,
    _ssh_run,
    _sq_path_join,
    _sq_s3_xfer,
    _validate_project,
    EBS_PATH,
    EC2_USER,
    PGDATA_PATH,
    PG_LOG_PATH,
    PROJECT_DIRS,
    S3_PATH,
    S3_PROJECTS_PATH,
)
from .pg import mac_down, ec2_dump

STRATEGY_DUCK = "duck"
STRATEGY_SQ = "sq"
STRATEGY = STRATEGY_SQ


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


def _tail_pg_cmd(lines=None, sudo=False):
    s = "sudo" if sudo else ""
    n = f"-n {lines} " if lines else ""
    return f"{s} ls -d {PG_LOG_PATH}/* | tail -n 1 | xargs {s} tail {n} -f"


@dev.command(help="Tail the pg log on host.")
@click.argument("lines", type=int, required=False)
def tail_pg(lines):
    _ensure_host()
    cmd = _tail_pg_cmd
    _run_command(cmd)


@dev.command(help="Tail the pg log on ec2.")
@click.argument("lines", type=int, required=False)
def tail_pg_ec2(lines):
    _ensure_host()
    cmd = _tail_pg_cmd()
    _ssh_run(f"sudo chmod -R 755 {EBS_PATH}")
    _ssh_run(f"{cmd}")


@dev.command(help=f"Create mac host {PGDATA_PATH}")
def mk_opt_ebs():
    p = PGDATA_PATH
    _run_command(f"sudo mkdir -p {p}")
    _run_command(f'sudo chown -R "`id -u -n`":staff {p}')


@dev.command(help="Tunnel to the aws docker pg db.")
@click.argument("host", type=click.STRING, required=False)
@click.option("--local-port", type=click.STRING, required=False, default="5432")
@click.option(
    "--print-only", is_flag=True, help="Print cmd (for sending to someone else)."
)
@click.pass_context
def tunnel(ctx, host=None, local_port=None, print_only=None):
    ctx.allow_extra_args = True
    ctx.invoke(mac_down)
    _ssh_add()
    if host is None:
        host = _running_ec2_docker_public_hostname()

    # dump a backup first
    ctx.invoke(ec2_dump)

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
@click.option(
    "--full", is_flag=True, help="Execute ec2-bootstrap.sh and ec2-mount-vol.sh"
)
def bootstrap(full):
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

    _ssh_run("touch .aws", user, host)

    cmd = (
        f""" "grep -q AWS_ACCESS_KEY_ID .aws || echo \\"export AWS_DEFAULT_REGION='{r}';"""
        f""" export AWS_SECRET_ACCESS_KEY='{s}';"""
        f""" export AWS_ACCESS_KEY_ID='{a}';\\" """
        """ >> .aws " """
    )
    _ssh_run(cmd, user, host)

    if full:
        _ssh_run(" ./ec2-bootstrap.sh", user, host)
        _ssh_run(" ./ec2-mount-vol.sh", user, host)
        _ssh_run(" ./pg/ec2-pg-bootstrap.sh", user, host)
        _ssh_run("mv YOU_MUST_RUN_BOOTSTRAP .RAN_BOOTSTRAP", user, host)
        # print("Now you can:\ncd sq && docker-compose up -d")
        # print("NB: if you get the error:")
        # print(
        #     "-- ERROR: Couldn't connect to Docker daemon at http+docker://localhost - is it running? --"
        # )
        # print("Logout, and re-ssh in.")


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


@dev.command(help="Init project directory on mac host in /opt/s3/projects")
@click.argument("project", type=click.STRING, required=True)
@click.pass_context
def project_init(ctx, project):
    _validate_project(project)
    u = getpass.getuser()
    #####################
    # create davinci dirs
    #####################
    p = "/opt/davinci"
    _run_command(f"test -e {p} || ( sudo mkdir {p} && sudo chown -R {u}:staff {p} )")

    # create a cache directory
    p = "/opt/davinci/cache"
    _run_command(f"test -e {p} || mkdir {p}")

    # create a capture directory
    p = "/opt/davinci/capture"
    _run_command(f"test -e {p} || mkdir {p}")

    #####################
    # create project dirs
    #####################
    p = S3_PATH
    _run_command(f"test -e {p} || ( sudo mkdir {p} && sudo chown -R {u}:staff {p} )")

    p = S3_PROJECTS_PATH
    _run_command(f"test -e {p} || mkdir {p}")
    project_path = _s3_local_project_path(project)
    p = project_path
    _run_command(f"test -e {p} || mkdir {p}")

    for d in PROJECT_DIRS:
        p = f"{project_path}/{d}"
        _run_command(f"test -e {p} || mkdir {p}")
        _run_command(f"touch {p}/.touch")
    ctx.invoke(s3_up, project=project)


@dev.command(help="Push local up to s3.")
@click.argument("project", type=click.STRING, required=True)
@click.option(
    "--no-skip-on-same-size",
    is_flag=True,
    help="""Do NOT skip xfer when files have same size.
(Normally, we skip files with same size BUT different checksum.)""",
)
@click.option(
    "--skip-regx", type=str, help="""SKIP files matching a pattern, eg, "\.braw$".""",
)
def s3_up(project, no_skip_on_same_size=False, skip_regx=None):
    # local = _s3_local_project_path(project)
    # e = _aws_env_string()
    # b = _s3_bucket_project_url(project)
    # The following sync command syncs objects under a specified prefix and
    # bucket to files in a local directory by uploading the local files to s3.
    # A local file will require uploading if the size of the local file is
    # different than the size of the s3 object, the last modified time of the
    # local file is newer than the last modified time of the s3 object, or the
    # local file does not exist under the specified bucket and prefix.
    #
    # WARNING: s3 sync will overwrite newer target files with older source files!
    # DON'T USE IT
    # _run_command(f"{e} aws s3 sync {local} {b}")
    if STRATEGY == STRATEGY_DUCK:
        _duck("upload", project)
    else:
        _sq_s3_xfer("upload", project, not no_skip_on_same_size, skip_regx)


@dev.command(help="Download s3 to local.")
@click.argument("project", type=click.STRING, required=True)
@click.option(
    "--no-skip-on-same-size",
    is_flag=True,
    help="""Do NOT skip xfer when files have same size.
(Normally, we skip files with same size BUT different checksum.)""",
)
@click.option(
    "--skip-regx", type=str, help="""SKIP files matching a pattern, eg, "\.braw$".""",
)
def s3_down(project, no_skip_on_same_size=False, skip_regx=None):
    if STRATEGY == STRATEGY_DUCK:
        _duck("download", project)
    else:
        _sq_s3_xfer("download", project, not no_skip_on_same_size, skip_regx)
