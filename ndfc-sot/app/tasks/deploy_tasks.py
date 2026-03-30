"""Celery tasks for YAML generation and Ansible deployment."""

from __future__ import annotations

import asyncio
import logging

from app.config import settings
from app.database import async_session_factory
from app.services.ansible_deployer import AnsibleDeployer
from app.services.yaml_builder import YamlBuilder
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from sync Celery task context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="deploy_fabric")
def deploy_fabric_task(self, fabric_id: str, check_mode: bool = False):
    """Generate YAML for a fabric and deploy via Ansible."""
    logger.info("Starting deploy for fabric %s (check_mode=%s)", fabric_id, check_mode)

    self.update_state(state="PROGRESS", meta={"step": "building_yaml"})

    async def _build_and_deploy():
        async with async_session_factory() as session:
            builder = YamlBuilder(session)
            yaml_data = await builder.build_fabric_yaml(fabric_id)

            deployer = AnsibleDeployer(
                playbook_dir=settings.ANSIBLE_PLAYBOOK_DIR,
                inventory_path=settings.ANSIBLE_INVENTORY,
                output_dir=settings.YAML_OUTPUT_DIR,
            )

            result = await deployer.deploy_fabric(
                yaml_data=yaml_data,
                fabric_name=yaml_data["fabric"]["name"],
                check_mode=check_mode,
            )
            return result

    try:
        result = _run_async(_build_and_deploy())
        if result["rc"] != 0:
            self.update_state(
                state="FAILURE",
                meta={
                    "step": "ansible_failed",
                    "rc": result["rc"],
                    "stderr": result["stderr"][:2000],
                },
            )
            raise Exception(f"Ansible playbook failed with rc={result['rc']}")

        return {
            "status": "success",
            "rc": result["rc"],
            "stdout_lines": result["stdout"].split("\n")[-20:],
        }
    except Exception as exc:
        logger.exception("Deploy task failed for fabric %s", fabric_id)
        raise self.retry(exc=exc, countdown=30, max_retries=2)


@celery_app.task(bind=True, name="generate_yaml")
def generate_yaml_task(self, fabric_id: str):
    """Generate YAML for a fabric without deploying."""
    logger.info("Generating YAML for fabric %s", fabric_id)

    async def _build():
        async with async_session_factory() as session:
            builder = YamlBuilder(session)
            yaml_data = await builder.build_fabric_yaml(fabric_id)

            deployer = AnsibleDeployer(
                output_dir=settings.YAML_OUTPUT_DIR,
            )
            filepath = deployer.write_yaml(
                yaml_data, f"{yaml_data['fabric']['name']}.yml"
            )
            return {"path": str(filepath), "fabric": yaml_data["fabric"]["name"]}

    return _run_async(_build())