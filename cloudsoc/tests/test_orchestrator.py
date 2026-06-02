"""Tests for orchestration helpers."""

from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from cloudsoc.playbooks.executor import DeploymentService
from cloudsoc.aws.ssm import SSMService


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


def test_deployment_service_remote_execution(tmp_path):
    deployment_dir = tmp_path / "deployments"
    deployment_dir.mkdir()

    deployment_yaml = {
        "name": "test_remote_deployment",
        "description": "Test remote deployment",
        "tasks": [
            {
                "name": "Echo test",
                "type": "shell",
                "cmd": "echo hello"
            }
        ]
    }

    deployment_file = deployment_dir / "test_remote.yml"
    with open(deployment_file, "w") as f:
        yaml.dump(deployment_yaml, f)

    mock_ssm = Mock(spec=SSMService)
    mock_ssm.send_command.return_value = "command-123"
    mock_ssm.wait_for_command.return_value = {"status": "Success", "return_code": 0, "output": "hello"}

    deployment_service = DeploymentService(deployment_dir=deployment_dir)
    result = deployment_service.run_deployment(
        "test_remote",
        variables={},
        ssm_service=mock_ssm,
        instance_ids=["i-123"]
    )

    assert result is True
    mock_ssm.send_command.assert_called_once()


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
    
    with patch("cloudsoc.playbooks.executor.run_command") as mock_run:
        mock_run.return_value = None
        result = deployment_service.run_deployment("test_deploy", variables={})
        assert result is True
