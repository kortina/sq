#!/usr/bin/env python
import click


HOST_MAC_IP = "host.docker.internal"


@click.group(help="Studio Quixote cli commands.")
def cli():
    pass


@cli.group(help="Local (mac host) commands.")
def dev():
    pass


@cli.group(help="ffmpeg commands.")
def ffmpeg():
    pass


@cli.group(help="Commands to be run inside the docker host only.")
def docker():
    pass


@cli.group(help="Terraform commands.")
def tf():
    pass


@cli.group(help="pg commands.")
def pg():
    pass


# Load the definitions we need to include in fa script.
from .dev import *  # noqa: F401, E402, F403
from .ffmpeg import *  # noqa: F401, E402, F403
from .pg import *  # noqa: F401, E402, F403
from .tf import *  # noqa: F401, E402, F403
