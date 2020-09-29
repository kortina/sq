import boto3
import click
import os
import re
import subprocess
import sys

TF_CONTAINER = "sq_tf"
PG_CONTAINER = "sq_pg"
EC2_DOCKER_HOST_NAME_TAG = "docker-host"


def _aws_kwargs():
    e = os.environ.get
    if _is_docker_container():
        aws_access_key_id = e("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = e("AWS_SECRET_ACCESS_KEY")
        region_name = e("AWS_DEFAULT_REGION")
    else:
        aws_access_key_id = e("SQ__AWS_ACCESS_KEY_ID")
        aws_secret_access_key = e("SQ__AWS_SECRET_KEY")
        region_name = e("SQ__AWS_DEFAULT_REGION")

    return {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "region_name": region_name,
    }


def _aws_client(service):
    return boto3.client(service, **_aws_kwargs())
    # return Config(
    #     region_name = 'us-west-2',
    #     signature_version = 'v4',
    #     retries = {
    #         'max_attempts': 10,
    #         'mode': 'standard'
    #     }
    # )


def _running_ec2_docker_instance():
    client = _aws_client("ec2")
    d = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [EC2_DOCKER_HOST_NAME_TAG]},
            {"Name": "instance-state-name", "Values": ["running"]},
        ]
    )
    if len(d["Reservations"]) > 1:
        raise ValueError(
            f"More than one reservation matches name: {EC2_DOCKER_HOST_NAME_TAG}"
        )
    if len(d["Reservations"][0]["Instances"]) > 1:
        raise ValueError(
            f"More than one instance matches name: {EC2_DOCKER_HOST_NAME_TAG}"
        )
    return d["Reservations"][0]["Instances"][0]


def _running_ec2_docker_public_hostname():
    i = _running_ec2_docker_instance()
    return i["PublicDnsName"]


def _is_docker_container():
    return os.path.exists("/.dockerenv")


def _ensure_host():
    if _is_docker_container():
        raise click.UsageError(
            "This command should only be run on the host, not in the docker container."
        )


def _ensure_docker():
    if not _is_docker_container():
        raise click.UsageError(
            "This command should only be run in the docker container, ie,"
            " via some other sq command, not directly."
        )


def _run_command(
    cmd,
    error_message=None,
    capture_output=False,
    hide_command=False,
    decode_output=True,
):
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
            p = subprocess.run(
                cmd, shell=True, check=True, capture_output=capture_output
            )
        except subprocess.CalledProcessError as e:  # remote commands sometimes throw this
            p = subprocess.CompletedProcess(cmd, e.returncode, stderr=e.output)
        # return this as a string you can actually work with:
        if capture_output and decode_output:
            return p.stdout.decode("utf-8").strip()
        else:
            return p


def _docker_exec(cmd, inherit_env, container=TF_CONTAINER):
    e_vars = _env_vars(inherit_env)
    _run_command("docker exec {0} -it {1} {2}".format(e_vars, container, cmd))


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
                # different tools expect different var names for this:
                args.append('-e AWS_SECRET_ACCESS_KEY="${0}"'.format(k))

    return " ".join(args)
