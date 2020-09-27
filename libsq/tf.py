import click
from . import docker, tf
from .utils import _docker_exec, _ensure_docker, _run_command


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
    cmd = f"cd tf && terraform plan -out=plan.tfplan {plan_args} . | landscape"
    _run_command(cmd)


@tf.command(help="Run tf plan in docker.")
@click.option("--no-inherit-env", is_flag=True, help="Do NOT inherit SQ__ env vars.")
@click.argument("targets", type=click.STRING, required=False)
def plan(no_inherit_env, targets=""):
    _docker_exec("./sq docker tf-plan {0}".format(targets or ""), not no_inherit_env)
