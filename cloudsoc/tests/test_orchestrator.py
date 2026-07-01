"""Tests for orchestration helpers."""

from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import MagicMock, Mock, patch
import json
import time
import yaml
import pytest
from botocore.exceptions import ClientError

from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.aws.ssm import SSMService
from cloudsoc.orchestrator import (
    BuildOrchestrator,
    DashboardOrchestrator,
    DeploymentOrchestrator,
    OrchestrationError,
    SSMDashboardTunnelManager,
    TunnelSession,
)


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


def test_build_orchestrator_resolves_all_targets():
    build_orchestrator = BuildOrchestrator()
    assert build_orchestrator._resolve_build_targets(None) == ["victim"]
    assert build_orchestrator._resolve_build_targets(["all"]) == ["victim"]


def test_build_orchestrator_parses_workflow_run_id():
    build_orchestrator = BuildOrchestrator()
    output = "Created workflow run 1234567"
    assert build_orchestrator._parse_workflow_run_id(output) == "1234567"


def test_build_orchestrator_triggers_workflow_and_waits():
    with patch("cloudsoc.orchestrator.run_command") as mock_run_command:
        mock_run_command.side_effect = [
            Mock(stdout="Created workflow run 1234", stderr="", returncode=0),
            Mock(returncode=0),
        ]
        build_orchestrator = BuildOrchestrator()

        build_orchestrator.build_targets(targets=["victim"], wait=True, ref="main")

        assert mock_run_command.call_count == 2
        assert mock_run_command.call_args_list[0][0][0] == ["gh", "workflow", "run", "build-victim-image.yml", "--ref", "main"]
        assert mock_run_command.call_args_list[1][0][0] == ["gh", "run", "watch", "1234", "--exit-status"]


def test_build_orchestrator_uses_current_branch_when_ref_is_not_specified():
    with patch("cloudsoc.orchestrator.run_command") as mock_run_command:
        mock_run_command.side_effect = [
            Mock(stdout="feature/build-deployment-workflow\n", stderr="", returncode=0),
            Mock(stdout="Created workflow run 1234", stderr="", returncode=0),
            Mock(returncode=0),
        ]
        build_orchestrator = BuildOrchestrator()

        build_orchestrator.build_targets(targets=["victim"], wait=True, ref=None)

        assert mock_run_command.call_count == 3
        assert mock_run_command.call_args_list[0][0][0] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        assert mock_run_command.call_args_list[1][0][0] == ["gh", "workflow", "run", "build-victim-image.yml", "--ref", "feature/build-deployment-workflow"]
        assert mock_run_command.call_args_list[2][0][0] == ["gh", "run", "watch", "1234", "--exit-status"]


def test_build_orchestrator_ensure_image_exists_raises_when_missing_images():
    with patch("cloudsoc.orchestrator.ECRService") as mock_ecr_service_cls:
        mock_ecr = Mock()
        mock_ecr.get_repository.return_value = {"name": "cloud-soc-victim"}
        mock_ecr.list_images.return_value = []
        mock_ecr_service_cls.return_value = mock_ecr

        build_orchestrator = BuildOrchestrator()
        with pytest.raises(OrchestrationError) as exc:
            build_orchestrator.ensure_image_exists("victim")

        assert "No image found in ECR repository cloud-soc-victim" in str(exc.value)


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


def test_deployment_service_clears_previous_errors(tmp_path):
    deployment_dir = tmp_path / "deployments"
    deployment_dir.mkdir()

    deployment_yaml = {
        "name": "test_deployment",
        "description": "Test deployment",
        "tasks": [
            {
                "name": "Success task",
                "type": "shell",
                "cmd": "echo 'ok'"
            }
        ]
    }

    deployment_file = deployment_dir / "test_deploy.yml"
    with open(deployment_file, "w") as f:
        yaml.dump(deployment_yaml, f)

    deployment_service = DeploymentService(deployment_dir=deployment_dir)
    deployment_service.last_error = "previous failure"
    deployment_service.last_error_detail = "previous detail"

    with patch("cloudsoc.deployment.executor.run_command") as mock_run:
        mock_run.return_value = None
        result = deployment_service.run_deployment("test_deploy", variables={})

    assert result is True
    assert deployment_service.last_error == ""
    assert deployment_service.last_error_detail == ""


def test_deployment_orchestrator_saves_failure_log_and_state(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    mock_deployment_service = Mock()
    mock_deployment_service.run_deployment.return_value = False
    mock_deployment_service.last_error = "Deployment failed"
    mock_deployment_service.last_error_detail = "Detailed remote failure output"

    with patch("cloudsoc.orchestrator.DeploymentService", return_value=mock_deployment_service), \
         patch("cloudsoc.orchestrator.ECRService") as mock_ecr_service_cls, \
         patch("cloudsoc.orchestrator.SSMService") as mock_ssm_service_cls:
        mock_ecr = Mock()
        mock_ecr_service_cls.return_value = mock_ecr
        mock_ssm_service_cls.return_value = Mock()
        deployment_orchestrator = DeploymentOrchestrator(settings=mock_settings)

        terraform_outputs = {
            "victim_instance_id": {"value": "i-123"},
            "ecr_victim_repository_url": {"value": "https://example.com/repo"},
            "wazuh_instance_private_ip": {"value": "10.0.0.10"},
        }

        with pytest.raises(OrchestrationError) as exc:
            deployment_orchestrator.deploy_targets(terraform_outputs, targets=["victim"])

        assert "Detailed log saved to" in str(exc.value)

        log_files = list((tmp_path / ".cloud-soc" / "logs").glob("*.log"))
        assert len(log_files) == 1
        log_content = log_files[0].read_text()
        assert "Detailed remote failure output" in log_content

        state = json.loads((tmp_path / ".cloud-soc" / "deployment_state.json").read_text())
        target_state = state["last_deployment"]["targets"]["victim_server"]
        assert target_state["status"] == "failed"
        assert target_state["error_detail"] == "Detailed remote failure output"


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


def test_dashboard_open_tunnel_expose_does_not_send_local_address(tmp_path, monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    monkeypatch.chdir(tmp_path)
    with open(tmp_path / "docker-compose.yml", "w") as f:
        yaml.dump({
            "services": {
                "devops": {
                    "image": "example",
                    "ports": ["9443:9443"]
                }
            }
        }, f)

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_service_cls, \
         patch("cloudsoc.orchestrator.subprocess.Popen") as mock_popen, \
         patch("cloudsoc.orchestrator.subprocess.run", return_value=Mock()), \
         patch("cloudsoc.orchestrator.SSMDashboardTunnelManager.validate_tls", return_value=None), \
         patch.object(DashboardOrchestrator, "_monitor_dashboard_service", return_value=(True, "")):
        mock_ssm_service = Mock()
        mock_ssm_service.wait_for_instance.return_value = True
        mock_ssm_service_cls.return_value = mock_ssm_service

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0
        mock_process.__enter__.return_value = mock_process
        mock_process.__exit__.return_value = None
        mock_popen.return_value = mock_process

        dashboard = DashboardOrchestrator(settings=mock_settings)
        dashboard.open_tunnel(
            {"wazuh_instance_id": {"value": "i-123"}},
            local_port=9443,
            remote_port=443,
            expose=True,
        )

        assert mock_popen.called
        command = mock_popen.call_args[0][0]
        assert "AWS-StartPortForwardingSession" in command
        params = json.loads(command[-1])
        assert params["localAddress"] == ["0.0.0.0"]
        assert params["localPortNumber"] == ["9443"]


def test_dashboard_open_tunnel_expose_validates_container_port(tmp_path, monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    compose_content = {
        "version": "3.8",
        "services": {
            "devops": {
                "image": "example",
                "ports": ["8443:8443"]
            }
        }
    }

    monkeypatch.chdir(tmp_path)
    with open(tmp_path / "docker-compose.yml", "w") as f:
        yaml.dump(compose_content, f)

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_service_cls, \
         patch("cloudsoc.orchestrator.subprocess.Popen") as mock_popen, \
         patch("cloudsoc.orchestrator.subprocess.run", return_value=Mock()), \
         patch("cloudsoc.orchestrator.SSMDashboardTunnelManager.validate_tls", return_value=None), \
         patch.object(DashboardOrchestrator, "_monitor_dashboard_service", return_value=(True, "")):
        mock_ssm_service = Mock()
        mock_ssm_service.wait_for_instance.return_value = True
        mock_ssm_service_cls.return_value = mock_ssm_service

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0
        mock_process.__enter__.return_value = mock_process
        mock_process.__exit__.return_value = None
        mock_popen.return_value = mock_process

        dashboard = DashboardOrchestrator(settings=mock_settings)
        dashboard.open_tunnel(
            {"wazuh_instance_id": {"value": "i-123"}},
            local_port=8443,
            remote_port=443,
            expose=True,
        )

        assert mock_popen.called


def test_dashboard_open_tunnel_expose_rejects_missing_container_port(tmp_path, monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    compose_content = {
        "version": "3.8",
        "services": {
            "devops": {
                "image": "example",
                "ports": ["8080:8080"]
            }
        }
    }

    monkeypatch.chdir(tmp_path)
    with open(tmp_path / "docker-compose.yml", "w") as f:
        yaml.dump(compose_content, f)

    monkeypatch.delenv("CODESPACES", raising=False)
    monkeypatch.delenv("GITHUB_CODESPACES", raising=False)

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_service_cls, \
         patch.object(DashboardOrchestrator, "_monitor_dashboard_service", return_value=(True, "")):
        mock_ssm_service = Mock()
        mock_ssm_service.wait_for_instance.return_value = True
        mock_ssm_service_cls.return_value = mock_ssm_service

        dashboard = DashboardOrchestrator(settings=mock_settings)
        with pytest.raises(OrchestrationError, match="Port 8443 is not published"):
            dashboard.open_tunnel(
                {"wazuh_instance_id": {"value": "i-123"}},
                local_port=8443,
                remote_port=443,
                expose=True,
            )


def test_monitor_dashboard_service_parses_adjacent_markers(monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    mock_ssm = Mock(spec=SSMService)
    mock_ssm.send_command.return_value = "command-123"
    mock_ssm.wait_for_command.return_value = {
        "status": "Success",
        "return_code": 0,
        "output": (
            "---curl-status---\n"
            "302---opensearch-status---\n"
            "200\n"
            "---docker-ps---\n"
            "mock ps output\n"
            "---dashboard-logs---\n"
            "dashboard log line\n"
            "---indexer-logs---\n"
            "indexer log line\n"
        ),
        "error": "",
    }
    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_cls:
        mock_ssm_cls.return_value = mock_ssm

        dashboard = DashboardOrchestrator(settings=mock_settings)
        ready, diagnostics = dashboard._monitor_dashboard_service("i-123", remote_port=443)

    assert ready is True
    assert "Dashboard is responding" in diagnostics
    assert "mock ps output" in diagnostics


def test_monitor_dashboard_service_retries_until_ready(monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    mock_ssm = Mock(spec=SSMService)
    mock_ssm.send_command.side_effect = ["command-1", "command-2"]
    mock_ssm.wait_for_command.side_effect = [
        {
            "status": "Success",
            "return_code": 0,
            "output": (
                "---curl-status---\n"
                "000---opensearch-status---\n"
                "000\n"
                "---docker-ps---\n"
                "mock ps output\n"
                "---dashboard-logs---\n"
                "dashboard log line\n"
                "---indexer-logs---\n"
                "indexer log line\n"
            ),
            "error": "",
        },
        {
            "status": "Success",
            "return_code": 0,
            "output": (
                "---curl-status---\n"
                "200---opensearch-status---\n"
                "200\n"
                "---docker-ps---\n"
                "mock ps output\n"
                "---dashboard-logs---\n"
                "dashboard log line\n"
                "---indexer-logs---\n"
                "indexer log line\n"
            ),
            "error": "",
        },
    ]

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_cls:
        mock_ssm_cls.return_value = mock_ssm

        dashboard = DashboardOrchestrator(settings=mock_settings)
        ready, diagnostics = dashboard._monitor_dashboard_service(
            "i-123",
            remote_port=443,
            max_attempts=2,
            retry_interval=0,
        )

    assert ready is True
    assert mock_ssm.send_command.call_count == 2
    assert mock_ssm.wait_for_command.call_count == 2
    assert "Dashboard is responding" in diagnostics


def test_monitor_dashboard_service_reports_attempt_count_on_failure(monkeypatch):
    mock_settings = Mock()
    mock_settings.project.aws.region = "us-east-1"
    mock_settings.project.aws.profile = "default"

    mock_ssm = Mock(spec=SSMService)
    mock_ssm.send_command.side_effect = ["command-1", "command-2"]
    mock_ssm.wait_for_command.return_value = {
        "status": "Success",
        "return_code": 0,
        "output": (
            "---curl-status---\n"
            "000---opensearch-status---\n"
            "000\n"
            "---docker-ps---\n"
            "mock ps output\n"
            "---dashboard-logs---\n"
            "dashboard log line\n"
            "---indexer-logs---\n"
            "indexer log line\n"
        ),
        "error": "",
    }

    with patch("cloudsoc.orchestrator.SSMService") as mock_ssm_cls:
        mock_ssm_cls.return_value = mock_ssm

        dashboard = DashboardOrchestrator(settings=mock_settings)
        ready, diagnostics = dashboard._monitor_dashboard_service(
            "i-123",
            remote_port=443,
            max_attempts=2,
            retry_interval=0,
        )

    assert ready is False
    assert "Dashboard health check attempted 2 times." in diagnostics
    assert "Dashboard returned HTTP status 000." in diagnostics


def test_dashboard_status_command_no_session(monkeypatch):
    runner = CliRunner()
    with patch("cloudsoc.orchestrator.DashboardOrchestrator.status", return_value={"status": "No active session"}):
        result = runner.invoke(__import__("cloudsoc.main", fromlist=["app"]).app, ["dashboard", "status"])

    assert result.exit_code == 0
    assert "No active dashboard tunnel session" in result.output


def test_dashboard_status_command_reports_active_session(monkeypatch):
    runner = CliRunner()
    with patch("cloudsoc.orchestrator.DashboardOrchestrator.status", return_value={
        "instance_id": "i-123",
        "local_port": 8443,
        "uptime": 5.0,
        "alive": True,
    }):
        result = runner.invoke(__import__("cloudsoc.main", fromlist=["app"]).app, ["dashboard", "status"])

    assert result.exit_code == 0
    assert "Instance ID" in result.output
    assert "i-123" in result.output
    assert "Local Port" in result.output
    assert "8443" in result.output


def test_tunnel_manager_ensure_alive_returns_false_for_dead_process():
    manager = SSMDashboardTunnelManager()
    fake_process = MagicMock()
    fake_process.poll.return_value = 1
    manager.active_session = TunnelSession(
        instance_id="i-123",
        session_id="123",
        local_port=8443,
        remote_port=443,
        process=fake_process,
        started_at=time.time() - 10,
    )

    assert manager.ensure_alive(timeout=0.1) is False


def test_tunnel_manager_get_or_reconnect_restarts_dead_session():
    manager = SSMDashboardTunnelManager()
    fake_process = MagicMock()
    fake_process.poll.return_value = 1
    manager.active_session = TunnelSession(
        instance_id="i-123",
        session_id="123",
        local_port=8443,
        remote_port=443,
        process=fake_process,
        started_at=time.time() - 10,
    )

    with patch.object(manager, "start", return_value=TunnelSession(
        instance_id="i-123",
        session_id="456",
        local_port=9443,
        remote_port=443,
        process=MagicMock(poll=MagicMock(return_value=None), wait=MagicMock(return_value=0)),
        started_at=time.time(),
    )) as mock_start:
        session = manager.get_or_reconnect("i-123", local_port=9443, remote_port=443)

    assert mock_start.called
    assert session.local_port == 9443


def test_tunnel_manager_status_reports_session_details(monkeypatch):
    manager = SSMDashboardTunnelManager()
    fake_process = MagicMock()
    fake_process.poll.return_value = None
    started_at = 1000.0
    manager.active_session = TunnelSession(
        instance_id="i-123",
        session_id="123",
        local_port=8443,
        remote_port=443,
        process=fake_process,
        started_at=started_at,
    )

    monkeypatch.setattr("cloudsoc.orchestrator.time.time", lambda: started_at + 10)
    with patch.object(manager, "ensure_alive", return_value=True):
        status = manager.status()

    assert status["instance_id"] == "i-123"
    assert status["local_port"] == 8443
    assert status["uptime"] == 10
    assert status["alive"] is True


def test_ssm_service_list_active_sessions_and_health():
    with patch("cloudsoc.aws.ssm.boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.describe_sessions.return_value = {
            "Sessions": [
                {
                    "SessionId": "s-123",
                    "Target": "i-123",
                    "DocumentName": "AWS-StartPortForwardingSession",
                    "Status": "Active",
                    "Owner": "tester",
                    "StartDate": "2025-01-01T00:00:00Z",
                }
            ]
        }
        mock_client.describe_instance_information.return_value = {
            "InstanceInformationList": [
                {
                    "InstanceId": "i-123",
                    "PingStatus": "Online",
                    "PlatformType": "Linux",
                    "IPAddress": "10.0.0.1",
                    "ComputerName": "i-123",
                }
            ]
        }
        mock_session.return_value.client.return_value = mock_client

        ssm = SSMService(region="eu-north-1")
        sessions = ssm.list_active_sessions()
        assert sessions is not None
        assert sessions[0]["SessionId"] == "s-123"

        health = ssm.get_instance_health(["i-123"])
        assert health["i-123"]["PingStatus"] == "Online"


def test_ssm_sessions_command_no_sessions(monkeypatch):
    runner = CliRunner()
    with patch("cloudsoc.main.SSMService") as mock_ssm_cls:
        mock_ssm = Mock()
        mock_ssm.list_active_sessions.return_value = []
        mock_ssm_cls.return_value = mock_ssm

        result = runner.invoke(__import__("cloudsoc.main", fromlist=["app"]).app, ["ssm", "sessions"])

    assert result.exit_code == 0
    assert "No active SSM sessions found" in result.output


def test_deployment_status_command_no_history(monkeypatch):
    runner = CliRunner()
    with patch("cloudsoc.orchestrator.DeploymentOrchestrator.get_deployment_status", return_value={"status": "No deployment history recorded"}):
        result = runner.invoke(__import__("cloudsoc.main", fromlist=["app"]).app, ["deployment", "status"])

    assert result.exit_code == 0
    assert "No deployment history found" in result.output
