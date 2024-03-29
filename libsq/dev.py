import getpass
import os

import click

from . import dev
from .pg import ec2_dump, mac_down
from .utils import (
    EBS_PATH,
    EC2_USER,
    PG_LOG_PATH,
    PGDATA_PATH,
    PROJECT_CHOICES,
    PROJECT_DIRS,
    S3_PATH,
    S3_PROJECTS_PATH,
    _abort_all_incomplete_multipart_uploads,
    _aws_kwargs,
    _docker_exec,
    _ensure_host,
    _ensure_local_path,
    _run_command,
    _running_ec2_docker_public_hostname,
    _s3_local_project_path,
    _s3_local_projects,
    _sq_path_join,
    _sq_s3_xfer,
    _ssh_add,
    _ssh_run,
    _validate_project,
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
    lp = "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/logs/davinci_resolve.log"
    cmd = f'{cmd} "{lp}" '
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


def _mk_opt_davinci():
    p = "/opt/__RESOLVE__"
    _run_command(f"test -e {p}/capture || sudo mkdir -p {p}/capture")
    _run_command(f"test -e {p}/proxy || sudo mkdir -p {p}/proxy")
    _run_command(f'sudo chown -R "`id -u -n`":staff {p}')


@dev.command(help="Create mac host /opt/__RESOLVE__ cache dirs")
def mk_opt_davinci():
    _mk_opt_davinci()


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


@dev.command(help="List projects on mac host in /opt/s3/projects")
@click.pass_context
def project_list(ctx):
    for p in _s3_local_projects():
        print(p)


@dev.command(help="Init project directory on mac host in /opt/s3/projects")
@click.argument("project", type=click.STRING, required=True)
@click.pass_context
def project_init(ctx, project):
    _validate_project(project)
    u = getpass.getuser()
    #####################
    # create davinci dirs
    #####################
    p = "/opt/__RESOLVE__"
    _run_command(f"test -e {p} || ( sudo mkdir {p} && sudo chown -R {u}:staff {p} )")

    # create a cache directory
    p = "/opt/__RESOLVE__/CacheClip"
    _run_command(f"test -e {p} || mkdir {p}")

    # create a capture directory
    p = "/opt/__RESOLVE__/capture"
    _run_command(f"test -e {p} || mkdir {p}")

    # create a gallery directory
    p = "/opt/__RESOLVE__/.gallery"
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


@dev.command(help="Abort all incomplete multipart uploads.")
@click.argument("project", type=PROJECT_CHOICES, required=True)
def abort_all_incomplete_multipart_uploads(project):
    _abort_all_incomplete_multipart_uploads(project)


@dev.command(help="Push local up to s3.")
@click.argument("project", type=PROJECT_CHOICES, required=True)
@click.option(
    "--no-skip-on-same-size",
    is_flag=True,
    help="""Do NOT skip xfer when files have same size.
(Normally, we skip files with same size BUT different checksum.)""",
)
@click.option(
    "--skip-if-same-size-without-etag-check",
    is_flag=True,
    help="""Do NOT check etag if files have exactly same size.
(Normally, we skip files with same size BUT different checksum.)""",
)
@click.option(
    "--skip-regx",
    type=str,
    help="""SKIP files matching a pattern, eg, "\\.braw$".""",
)
@click.option(
    "--match-regx",
    type=str,
    help="""SKIP files NOT-matching a pattern, eg, "\\.braw$".""",
)
@click.option(
    "--max-bandwidth-mb",
    type=int,
    help="""Maximum bandwidth MBps.""",
)
def s3_up(
    project,
    no_skip_on_same_size=False,
    skip_if_same_size_without_etag_check=False,
    skip_regx=None,
    match_regx=None,
    max_bandwidth_mb=None,
):
    _sq_s3_xfer(
        "upload",
        project,
        not no_skip_on_same_size,
        skip_if_same_size_without_etag_check,
        skip_regx,
        match_regx,
        max_bandwidth_mb,
    )


@dev.command(help="Download s3 to local.")
@click.argument("project", type=PROJECT_CHOICES, required=True)
@click.option(
    "--no-skip-on-same-size",
    is_flag=True,
    help="""Do NOT skip xfer when files have same size.
(Normally, we skip files with same size BUT different checksum.)""",
)
@click.option(
    "--skip-regx",
    type=str,
    help="""SKIP files matching a pattern, eg, "\\.braw$".""",
)
@click.option(
    "--match-regx",
    type=str,
    help="""SKIP files NOT-matching a pattern, eg, "\\.braw$".""",
)
@click.option(
    "--max-bandwidth-mb",
    type=int,
    help="""Maximum bandwidth MBps.""",
)
def s3_down(
    project,
    no_skip_on_same_size=False,
    skip_regx=None,
    match_regx=None,
    max_bandwidth_mb=None,
):
    skip_if_same_size_without_etag_check = False
    _sq_s3_xfer(
        "download",
        project,
        not no_skip_on_same_size,
        skip_if_same_size_without_etag_check,
        skip_regx,
        match_regx,
        max_bandwidth_mb,
    )


@dev.command(
    help="rsync Proxies (and exclude .braw files) from external Volume to local."
)
@click.argument("project", type=PROJECT_CHOICES, required=True)
@click.argument("volume-path", type=click.Path(exists=True))
def rsync_proxies_from_volume_to_opt(
    project,
    volume_path,
):
    cmd = "rsync -av"
    flags = "--exclude='*.braw'"
    project_path = _s3_local_project_path(project)

    # ensure volume_path has trailing slash (for rsync)
    if volume_path[-1] != "/":
        volume_path = f"{volume_path}/"

    _ensure_local_path(volume_path)

    cmd = f'{cmd} "{volume_path}" "{project_path}" {flags}'
    print(cmd)
    _run_command(cmd)
