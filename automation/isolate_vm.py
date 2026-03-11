#!/usr/bin/env python3
"""Wazuh active response helper to isolate an EC2 instance (DevOps-first)."""

import os
import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ec2 = boto3.client("ec2")


def isolate_instance(instance_id: str, security_group_id: str):
    """Add a restrictive security group to block inbound access for compromised instance."""
    try:
        logger.info("Isolating instance %s using security group %s", instance_id, security_group_id)
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[security_group_id],
        )
        logger.info("Instance %s isolated successfully", instance_id)
    except ClientError as err:
        logger.error("Failed to isolate instance %s: %s", instance_id, err)
        raise


def get_local_instance_id() -> str:
    """Attempt to get instance id from EC2 metadata when running inside EC2."""
    try:
        import requests
        meta_url = "http://169.254.169.254/latest/meta-data/instance-id"
        response = requests.get(meta_url, timeout=2)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        raise RuntimeError("Could not determine instance id from metadata") from exc


if __name__ == "__main__":
    target_instance = os.getenv("TARGET_INSTANCE_ID")
    target_sg = os.getenv("ISOLATION_SG_ID")

    if not target_instance or not target_sg:
        logger.error("Environment variables TARGET_INSTANCE_ID and ISOLATION_SG_ID are required")
        raise SystemExit(1)

    isolate_instance(target_instance, target_sg)
