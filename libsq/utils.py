import click
import os
import re
import subprocess
import sys

TF_CONTAINER = "sq_tf"


def _ensure_host():
    if os.path.exists("/.dockerenv"):
        raise click.UsageError(
            "This command should only be run on the host, not in the docker container."
        )


def _ensure_docker():
    if not os.path.exists("/.dockerenv"):
        raise click.UsageError(
            "This command should only be run in the docker container, ie,"
            " via some other sq command, not directly."
        )


def _run_command(cmd, error_message=None, capture_output=False, hide_command=False):
    # hide_command can be used to reduce the amount of output
    if not hide_command:
        click.secho("\n>> Running: {}\n".format(cmd), fg="green")
    if error_message:
        if capture_output:
            raise "capture_output + error_message cannot both \
                   be used, because subprocess.call does not \
                   allow capture_output"

        code = subprocess.call(cmd, shell=True)
        if code != 0:
            click.secho(error_message, fg="red")
            sys.exit(code)
    else:
        try:
            return subprocess.run(
                cmd, shell=True, check=True, capture_output=capture_output
            )
        except subprocess.CalledProcessError as e:  # remote commands sometimes throw this
            return subprocess.CompletedProcess(cmd, e.returncode, stderr=e.output)


def _docker_exec(cmd, inherit_env):
    e_vars = _env_vars(inherit_env)
    _run_command("docker exec {0} -it {1} {2}".format(e_vars, TF_CONTAINER, cmd))


def _env_vars(inherit_env):
    if not inherit_env:
        return ""
    prefix = re.compile(r"^SQ__")
    args = []
    for k, v in os.environ.items():
        if re.match(prefix, k):
            args.append('-e {0}="${1}"'.format(re.sub(prefix, "", k), k))
            # special case set some TF_VAR's
            if k == "SQ__AWS_ACCESS_KEY_ID":
                args.append('-e TF_VAR_access_key="${0}"'.format(k))
            if k == "SQ__AWS_SECRET_KEY":
                args.append('-e TF_VAR_secret_key="${0}"'.format(k))

    return " ".join(args)
