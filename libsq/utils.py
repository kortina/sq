import boto3
from boto3.s3.transfer import TransferConfig
import click
from dataclasses import dataclass
import datetime
import hashlib
from mimetypes import guess_type
import pathlib
import pytz
import os
import re
import shutil
import subprocess
import sys
import threading


TF_CONTAINER = "sq_tf"
PG_CONTAINER = "sq_pg"
EC2_DOCKER_HOST_NAME_TAG = "docker-host"
EC2_USER = "ubuntu"  # ec2-user for Amazon Linux
EBS_PATH = "/opt/ebs"
S3_PATH = "/opt/s3"
S3_PROJECTS_PATH = "/opt/s3/projects"
PGDATA_PATH = f"{EBS_PATH}/pgdata"
PG_LOG_PATH = f"{EBS_PATH}/pg_log"
S3_BUCKET = "sq-us-west-1"
PROJECT_DIRS = [
    "clips-audio",
    "clips-video",  # for youtube-dl etc.
    "exports",
    "films",  # for films referenced
    "gallery",  # for DaVinci
    "live-audio",
    "live-video",
    "music",
]

MULTIPART_THRESHOLD = 1024 * 1024 * 100  # 100mb
MULTIPART_CHUNKSIZE = 1024 * 1024 * 100  # 100mb
TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=MULTIPART_THRESHOLD,
    max_concurrency=10,
    multipart_chunksize=MULTIPART_CHUNKSIZE,
    use_threads=True,
)

SKIP_NONE = None
SKIP_ETAG = "etag"
SKIP_SIZE = "size"
SKIP_LMOD = "lmod"
SKIP_REGX = "regx"


def _md5(filepath, blocksize=2 ** 20):
    m = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest().strip('"')


@dataclass(frozen=True)
class S3File:
    key: str
    last_modified: datetime.datetime
    etag: str
    size: int
    storage_class: str

    @property
    def local_path(self):
        return _local_from(self.key)

    @property
    def tmp_local_path(self):
        return os.path.join("/tmp", _local_from(self.key).strip("/"))

    def skip_replace_local_reason(self, skip_on_same_size=True):
        # local does not exist, so download
        if not os.path.exists(self.local_path):
            return SKIP_NONE
        loc = LocalFile.from_path(self.local_path)
        # same md5 checksum, so no replace
        if self.etag == loc.etag or self.etag == loc.md5:
            return SKIP_ETAG
        # skip files with same size even if checksum is different
        if skip_on_same_size and self.size == loc.size:
            return SKIP_SIZE
        # diff md5, so only replace if remote is newer
        if False:
            print(f"l: {loc.last_modified}")
            print(f"r: {self.last_modified}")
        return SKIP_LMOD if self.last_modified > loc.last_modified else SKIP_NONE


@dataclass(frozen=True)
class LocalFile:
    key: str
    local_path: str
    last_modified: datetime.datetime
    etag: str
    md5: str
    size: int
    mime_type: str

    @classmethod
    def from_path(cls, local_path):
        d = datetime.datetime.utcfromtimestamp(os.path.getmtime(local_path))

        d_tz = datetime.datetime(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=d.hour,
            minute=d.minute,
            second=d.second,
            tzinfo=pytz.UTC,
        )
        # calculate md5 and size only on init:
        return LocalFile(
            key=_remote_from(local_path),
            local_path=local_path,
            last_modified=d_tz,
            etag=calculate_multipart_etag(local_path, MULTIPART_CHUNKSIZE).strip('"'),
            md5=_md5(local_path),
            size=int(os.path.getsize(local_path)),
            mime_type=guess_type(local_path)[0],
        )

    def skip_replace_remote_reason(self, remote_ix, skip_on_same_size=True):
        r = remote_ix.get(self.key, None)
        # does not exist on remote
        if r is None:
            return SKIP_NONE
        # same md5 checksum, so no replace
        if self.etag == r.etag or self.md5 == r.etag:
            return SKIP_ETAG
        # skip files with same size even if checksum is different
        if skip_on_same_size and self.size == r.size:
            return SKIP_SIZE
        # diff md5, so only replace if local is newer
        if False:
            print(f"l: {self.last_modified}")
            print(f"r: {r.last_modified}")
        return SKIP_LMOD if self.last_modified > r.last_modified else SKIP_NONE


def _sq_root_path():
    return pathlib.Path(__file__).parent.parent.absolute()


def _sq_path_join(p):
    return os.path.join(_sq_root_path(), p)


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


def _aws_env_string():
    k = _aws_kwargs()
    return "AWS_ACCESS_KEY_ID='{}' AWS_SECRET_ACCESS_KEY='{}' AWS_DEFAULT_REGION='{}'".format(
        k["aws_access_key_id"], k["aws_secret_access_key"], k["region_name"],
    )


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


def _ssh_add():
    home = os.environ.get("HOME")
    ssh_key_path = f"{home}/.ssh/sq_aws.pem"
    _run_command(f"ssh-add {ssh_key_path}", capture_output=True, hide_command=True)


# if running multiple times
# you should set user and host yourself
# and pass them as args
# rather than doing the _running_ec2_docker_public_hostname check every time
def _ssh_run(cmd, user=None, host=None):
    if user is None:
        user = EC2_USER
    if host is None:
        host = _running_ec2_docker_public_hostname()
    _ssh_add()
    _run_command(
        f"ssh {user}@{host} 'source .bash_profile && {cmd}'", capture_output=False
    )


def _s3_local_project_path(project):
    return f"{S3_PROJECTS_PATH}/{project}"


def _s3_bucket_project_url(project):
    return f"s3://{S3_BUCKET}/projects/{project}"


def _validate_project(project):
    if not re.search(r"^[\w\-_]+$", project):
        raise ValueError("Invalid project name.")


def _duck(cmd, project):
    _validate_project(project)
    flags = " --existing=compare"
    if cmd == "upload":
        local = _s3_local_project_path(project)
        remote = f"  s3:{S3_BUCKET}/projects/{project}"
    elif cmd == "download":
        local = S3_PROJECTS_PATH
        remote = f"  s3:{S3_BUCKET}/projects/{project}/"  # need trailing slash
    else:
        raise Exception(f"{cmd} NOT_IMPLEMENTED")

    cmd = (
        "duck"
        " -v"
        ' --username="$SQ__AWS_ACCESS_KEY_ID"'
        ' --password="$SQ__AWS_SECRET_KEY"'
        f" {flags}"
        f" --{cmd}"
        f" {remote}"
        f" {local}"
        f" | rg 'Uploading|Downloading'"
    )
    _run_command(cmd)


def _remote_ix(client, bucket, project):
    project_prefix = f"projects/{project}"
    remote_ix = {}
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=project_prefix)
    for page in page_iterator:
        for o in page.get("Contents", []):
            s3f = S3File(
                key=o["Key"],
                last_modified=o["LastModified"],
                etag=o["ETag"].strip('"'),
                size=o["Size"],
                storage_class=o["StorageClass"],
            )
            remote_ix[s3f.key] = s3f
    return remote_ix


def _just(op, skip_reason=None):
    s = op
    if skip_reason not in [SKIP_NONE, None]:
        s = f"{op}:{skip_reason}"
    return f"{s}:".ljust(10)


def _sq_s3_xfer(cmd, project, skip_on_same_size=True, skip_regx=None):
    _validate_project(project)
    client = _aws_client("s3")
    remote_ix = _remote_ix(client, S3_BUCKET, project)
    local_project_path = _s3_local_project_path(project)
    skip_rx = None
    if skip_regx is not None:
        skip_rx = re.compile(skip_regx, re.I)

    if cmd == "upload":
        for subdir, dirs, files in os.walk(local_project_path):
            for file in files:
                local_path = os.path.join(subdir, file)

                # skip DS_STORE files
                if re.search(r"\.DS_Store$", file):
                    continue
                if skip_rx and skip_rx.search(file):
                    skip_reason = SKIP_REGX
                else:
                    loc = LocalFile.from_path(local_path)
                    skip_reason = loc.skip_replace_remote_reason(
                        remote_ix, skip_on_same_size
                    )
                if skip_reason == SKIP_NONE:
                    s = _just("UPLOAD")
                    print(f"{s} {local_path}")
                    _upload(client, loc)
                else:
                    s = _just("skip", skip_reason)
                    print(f"{s} {local_path}")

    elif cmd == "download":
        for key, s3_file in remote_ix.items():
            if skip_rx and skip_rx.search(s3_file.key):
                skip_reason = SKIP_REGX
            else:
                skip_reason = s3_file.skip_replace_local_reason(skip_on_same_size)
            if skip_reason == SKIP_NONE:
                s = _just("DOWNLOAD")
                print(f"{s} {s3_file.key}")
                _download(client, s3_file)
            else:
                s = _just("skip", skip_reason)
                print(f"{s} {s3_file.key}")
    else:
        raise Exception(f"{cmd} NOT_IMPLEMENTED")


# /opt/s3/projects/can-we-survive-technology/clips-video/.touch
# ->
# projects/can-we-survive-technology/clips-video/.touch
def _remote_from(local: str):
    rx = re.compile(S3_PATH)
    # remove /opt/s3
    remote = re.sub(rx, "", local)
    # remove leading slash
    remote = re.sub("^/", "", remote)
    return remote


# projects/can-we-survive-technology/clips-video/.touch
# ->
# /opt/s3/projects/can-we-survive-technology/clips-video/.touch
def _local_from(remote: str):
    return f"{S3_PATH}/{remote}"


def _download(client, s3_file):
    # ensure tmp dir path exists
    tmp_dir = os.path.dirname(s3_file.tmp_local_path)
    os.makedirs(tmp_dir, exist_ok=True)

    # ensure target dir path exists
    target_dir = os.path.dirname(s3_file.local_path)
    os.makedirs(target_dir, exist_ok=True)

    size = (
        client.head_object(Bucket=S3_BUCKET, Key=s3_file.key).get("ContentLength", None)
        or 1
    )

    client.download_file(
        S3_BUCKET,
        s3_file.key,
        s3_file.tmp_local_path,
        Config=TRANSFER_CONFIG,
        Callback=ProgressPercentage(s3_file.key, size),
    )
    # add a newline since we have been flushing stdout:
    print("")
    shutil.move(s3_file.tmp_local_path, s3_file.local_path)


def _upload(client, local_file):
    x = {}
    # x["MetaData"] = {"Content-MD5": local_file.etag}
    if local_file.mime_type:
        x["ContentType"] = local_file.mime_type
        # , "ETag": local_file.etag

    client.upload_file(
        local_file.local_path,
        S3_BUCKET,
        local_file.key,
        Config=TRANSFER_CONFIG,
        Callback=ProgressPercentage(local_file.local_path, local_file.size),
        ExtraArgs=x,
    )
    # add a newline since we have been flushing stdout:
    print("")


class ProgressPercentage(object):
    def __init__(self, filename, size):
        self._filename = filename
        self._size = float(size)
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)"
                % (self._filename, self._seen_so_far, self._size, percentage,)
            )
            sys.stdout.flush()


# via: https://github.com/tlastowka/calculate_multipart_etag/blob/master/calculate_multipart_etag.py
# calculate_multipart_etag  Copyright (C) 2015
#      Tony Lastowka <tlastowka at gmail dot com>
#      https://github.com/tlastowka
#
#
# calculate_multipart_etag is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# calculate_multipart_etag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with calculate_multipart_etag.  If not, see <http://www.gnu.org/licenses/>.


def calculate_multipart_etag(source_path, chunk_size, expected=None):

    """
    calculates a multipart upload etag for amazon s3
    Arguments:
    source_path -- The file to calculate the etag for
    chunk_size -- The chunk size to calculate for.
    Keyword Arguments:
    expected -- If passed a string, the string will be compared to the resulting etag
    and raise an exception if they don't match
    """

    md5s = []

    with open(source_path, "rb") as fp:
        while True:

            data = fp.read(chunk_size)

            if not data:
                break
            md5s.append(hashlib.md5(data))

    if len(md5s) > 1:
        digests = b"".join(m.digest() for m in md5s)
        new_md5 = hashlib.md5(digests)
        new_etag = '"%s-%s"' % (new_md5.hexdigest(), len(md5s))
    elif len(md5s) == 1:  # file smaller than chunk size
        new_etag = '"%s"' % md5s[0].hexdigest()
    else:  # empty file
        new_etag = '""'

    if expected:
        if not expected == new_etag:
            raise ValueError(
                "new etag %s does not match expected %s" % (new_etag, expected)
            )

    return new_etag
