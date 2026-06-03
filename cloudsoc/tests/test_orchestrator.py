"""Tests for orchestration helpers."""

from pathlib import Path
from unittest.mock import Mock, patch
import json
import yaml
from botocore.exceptions import ClientError

from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.aws.ssm import SSMService
from cloudsoc.orchestrator import DashboardOrchestrator


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


def test_ssm_wait_for_command_handles_pending_invocation(tmp_path):
    with patch("cloudsoc.aws.ssm.boto3.Session") as mock_session:
        mock_client = Mock()
        responses = [
            ClientError(
                {"Error": {"Code": "InvocationDoesNotExist", "Message": "Invocation does not exist."}},
                "GetCommandInvocation"
            ),
            {
                "Status": "Success",
                "StandardOutputContent": "ok",
                "StandardErrorContent": "",
                "ResponseCode": 0
            }
        ]

        def get_command_invocation_side_effect(**kwargs):
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        mock_client.get_command_invocation.side_effect = get_command_invocation_side_effect
        mock_session.return_value.client.return_value = mock_client

        ssm = SSMService(region="eu-north-1")
        invocation = ssm.wait_for_command("cmd-123", "i-123", timeout=1, poll_interval=0.01)

        assert invocation is not None
        assert invocation["status"] == "Success"
        assert invocation["return_code"] == 0


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


def test_deployment_service_reports_remote_failure_details(tmp_path):
    deployment_dir = tmp_path / "deployments"
    deployment_dir.mkdir()

    deployment_yaml = {
        "name": "test_remote_failure",
        "description": "Test remote deployment failure",
        "tasks": [
            {
                "name": "Failing task",
                "type": "shell",
                "cmd": "exit 1"
            }
        ]
    }

    deployment_file = deployment_dir / "test_remote_failure.yml"
    with open(deployment_file, "w") as f:
        yaml.dump(deployment_yaml, f)

    mock_ssm = Mock(spec=SSMService)
    mock_ssm.send_command.return_value = "command-456"
    mock_ssm.wait_for_command.return_value = {
        "status": "Failed",
        "return_code": 1,
        "output": "",
        "error": "Command failed"
    }

    deployment_service = DeploymentService(deployment_dir=deployment_dir)
    result = deployment_service.run_deployment(
        "test_remote_failure",
        variables={},
        ssm_service=mock_ssm,
        instance_ids=["i-123"]
    )

    assert result is False
    assert "status=Failed" in deployment_service.last_error


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


def test_dashboard_open_tunnel_expose_does_not_send_local_address():
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_service_cls, \
         patch("cloudsoc.orchestrator.run_command") as mock_run_command, \
         patch.object(DashboardOrchestrator, "_monitor_dashboard_service", return_value=(True, "")):
        mock_ssm_service = Mock()
        mock_ssm_service.wait_for_instance.return_value = True
        mock_ssm_service_cls.return_value = mock_ssm_service

        dashboard = DashboardOrchestrator(settings=mock_settings)
        dashboard.open_tunnel(
            {"wazuh_instance_id": {"value": "i-123"}},
            local_port=9443,
            remote_port=443,
            expose=True,
        )

        assert mock_run_command.called
        command = mock_run_command.call_args[0][0]
        assert "AWS-StartPortForwardingSession" in command
        params = json.loads(command[-1])
        assert "localAddress" not in params
        assert params["localPortNumber"] == ["9443"]
