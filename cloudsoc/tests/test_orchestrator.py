"""Tests for orchestration helpers."""

from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.models.resources import EC2Instance
from cloudsoc.orchestrator import InventoryGenerator
from cloudsoc.aws.ssm import SSMService


def test_inventory_generator_groups_hosts(tmp_path):
    mock_ec2 = Mock()
    mock_ec2.find_instances.return_value = [
        EC2Instance(
            id="i-0",
            type="t3.micro",
            state="running",
            private_ip="10.0.1.10",
            public_ip=None,
            vpc_id="vpc-123",
            subnet_id="subnet-123",
            tags={"Name": "wazuh-manager", "Project": "cloud-soc"}
        ),
        EC2Instance(
            id="i-1",
            type="t3.micro",
            state="running",
            private_ip="10.0.2.10",
            public_ip=None,
            vpc_id="vpc-123",
            subnet_id="subnet-123",
            tags={"Name": "victim-server", "Project": "cloud-soc"}
        )
    ]

    inventory_path = tmp_path / "generated_hosts.ini"
    generator = InventoryGenerator(mock_ec2, inventory_path=inventory_path)
    result_path = generator.generate(project_tag="cloud-soc")

    assert result_path == inventory_path
    contents = inventory_path.read_text()
    assert "[wazuh]" in contents
    assert "10.0.1.10" in contents
    assert "[victims]" in contents
    assert "10.0.2.10" in contents


def test_ssm_wait_for_instance_online():
    with patch("cloudsoc.aws.ssm.boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.describe_instance_information.return_value = {
            "InstanceInformationList": [
                {"PingStatus": "Online"}
            ]
        }
        mock_session.return_value.client.return_value = mock_client

        ssm = SSMService(region="eu-north-1")
        assert ssm.wait_for_instance("i-123", timeout=1, poll_interval=0.01)
        mock_client.describe_instance_information.assert_called()


def test_deployment_service_missing_file(tmp_path):
    """Test that deployment service handles missing deployment files gracefully."""
    deployment_service = DeploymentService(deployment_dir=tmp_path)
    
    result = deployment_service.run_deployment("nonexistent", variables={})
    assert result is False


def test_deployment_service_runs_tasks(tmp_path):
    """Test that deployment service can execute deployment tasks."""
    deployment_dir = tmp_path / "deployments"
    deployment_dir.mkdir()
    
    # Create a simple deployment YAML file
    deployment_yaml = {
        "name": "test_deployment",
        "description": "Test deployment",
        "tasks": [
            {
                "name": "Test task",
                "type": "shell",
                "cmd": "echo 'test'",
                "skip_if_exists": "/nonexistent/path"
            }
        ]
    }
    
    deployment_file = deployment_dir / "test_deploy.yml"
    with open(deployment_file, "w") as f:
        yaml.dump(deployment_yaml, f)
    
    deployment_service = DeploymentService(deployment_dir=deployment_dir)
    
    with patch("cloudsoc.deployment.executor.run_command") as mock_run:
        mock_run.return_value = None
        result = deployment_service.run_deployment("test_deploy", variables={})
        assert result is True
