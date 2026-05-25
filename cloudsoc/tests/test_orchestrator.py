"""Tests for orchestration helpers."""

from pathlib import Path
from unittest.mock import Mock, patch

from cloudsoc.ansible.deploy import AnsibleService
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


def test_inventory_generator_uses_temporary_file_by_default():
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
        )
    ]

    generator = InventoryGenerator(mock_ec2)
    result_path = generator.generate(project_tag="cloud-soc")

    assert result_path.exists()
    assert "[wazuh]" in result_path.read_text()
    result_path.unlink()


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


def test_ansible_playbook_missing_binary(tmp_path):
    ansible_service = AnsibleService(playbooks_dir=tmp_path)
    playbook = tmp_path / "test_playbook.yml"
    playbook.write_text("- hosts: all\n  tasks: []\n")

    with patch("cloudsoc.ansible.deploy.shutil.which", return_value=None):
        assert ansible_service.run_playbook(str(playbook.name)) is False
