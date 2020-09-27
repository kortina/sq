import click
import os
import sys
from . import docker, tf
from .utils import _docker_exec, _ensure_docker, _run_command

PLAN_FILE = "plan.tfplan"
PLAN_FILE_PATH = os.path.join("tf", "plan.tfplan")


@docker.command(help="Run tf plan in docker.")
@click.argument("targets", type=click.STRING, required=False)
def tf_plan(targets):
    _ensure_docker()
    plan_args = []
    if targets:
        targets = targets.split(" ")
        for target in targets:
            plan_args.append(f"-target={target}")
    plan_args = " ".join(plan_args)
    cmd = f"cd tf && terraform plan -out={PLAN_FILE} {plan_args} . | landscape"
    _run_command(cmd)


@tf.command(help="Run tf plan in docker.")
@click.option("--no-inherit-env", is_flag=True, help="Do NOT inherit SQ__ env vars.")
@click.argument("targets", type=click.STRING, required=False)
def plan(no_inherit_env, targets=""):
    _docker_exec("./sq docker tf-plan {0}".format(targets or ""), not no_inherit_env)


@docker.command(help="Apply tf plan in docker.")
def tf_apply():
    _ensure_docker()

    # Check whether the current directory is tf
    # and if so, ensure that this is is done on a clean master branch
    # if os.path.basename(os.getcwd()) == "tf":
    #     pass
    #     _verify_clean_master()

    # Perform apply
    if os.path.isfile(PLAN_FILE_PATH):
        if os.path.getsize(PLAN_FILE_PATH):
            _run_command(f"cd tf && terraform apply {PLAN_FILE}")
            _run_command(
                f"cd tf && test -f {PLAN_FILE} && mv {PLAN_FILE} plan.after.tfplan"
            )
        else:
            click.secho(f"Plan file {PLAN_FILE} unexpectedly empty, exiting.")
            sys.exit(1)
    else:
        click.secho(f"No {PLAN_FILE} found, exiting.")
        sys.exit(1)


@tf.command(help="Apply tf plan in docker.")
@click.option("--no-inherit-env", is_flag=True, help="Do NOT inherit SQ__ env vars.")
def apply(no_inherit_env):
    _docker_exec("./sq docker tf-apply", not no_inherit_env)
