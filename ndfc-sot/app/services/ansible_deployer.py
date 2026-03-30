"""Ansible deployment service – writes YAML and runs playbooks."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class AnsibleDeployer:
    """Writes YAML files and optionally executes Ansible playbooks."""

    def __init__(
        self,
        playbook_dir: str = "/opt/ansible/playbooks",
        inventory_path: str = "/opt/ansible/inventory",
        output_dir: str | None = None,
    ) -> None:
        self.playbook_dir = Path(playbook_dir)
        self.inventory_path = Path(inventory_path)
        self.output_dir = Path(output_dir) if output_dir else None

    def write_yaml(self, data: dict, filename: str) -> Path:
        """Write a YAML dict to a file and return the path."""
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.output_dir / filename
        else:
            tmpdir = Path(tempfile.mkdtemp(prefix="ndfc_sot_"))
            filepath = tmpdir / filename

        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info("Wrote YAML to %s", filepath)
        return filepath

    async def run_playbook(
        self,
        playbook_name: str,
        extra_vars_file: Path | None = None,
        tags: list[str] | None = None,
        check_mode: bool = False,
    ) -> dict:
        """Run an Ansible playbook and return stdout/stderr/rc."""
        cmd = [
            "ansible-playbook",
            str(self.playbook_dir / playbook_name),
            "-i",
            str(self.inventory_path),
        ]

        if extra_vars_file:
            cmd.extend(["-e", f"@{extra_vars_file}"])
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        if check_mode:
            cmd.append("--check")

        logger.info("Running: %s", " ".join(cmd))

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        result = {
            "rc": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
        }

        if process.returncode != 0:
            logger.error(
                "Playbook %s failed (rc=%d): %s",
                playbook_name,
                process.returncode,
                result["stderr"],
            )
        else:
            logger.info("Playbook %s completed successfully", playbook_name)

        return result

    async def deploy_fabric(
        self,
        yaml_data: dict,
        fabric_name: str,
        check_mode: bool = False,
    ) -> dict:
        """Full deploy pipeline: write YAML → run playbook."""
        filename = f"{fabric_name}_deploy.yml"
        yaml_path = self.write_yaml(yaml_data, filename)
        return await self.run_playbook(
            "site.yml",
            extra_vars_file=yaml_path,
            check_mode=check_mode,
        )