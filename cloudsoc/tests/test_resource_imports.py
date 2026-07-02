"""Tests for Terraform resource import helpers."""

from unittest.mock import MagicMock, patch

from cloudsoc.models.resources import S3Bucket
from cloudsoc.terraform.imports import ResourceImporter
from cloudsoc.terraform.runner import TerraformRunner


@patch("cloudsoc.terraform.imports.EC2Service")
@patch("cloudsoc.terraform.imports.IAMService")
@patch("cloudsoc.terraform.imports.S3Service")
@patch("cloudsoc.terraform.imports.ECRService")
def test_import_random_id_bucket_suffix_imports_suffix(
    mock_ecr_service,
    mock_s3_service,
    mock_iam_service,
    mock_ec2_service,
):
    runner = MagicMock(spec=TerraformRunner)
    runner.state_contains.return_value = False

    importer = ResourceImporter(tf_runner=runner)
    importer._import_random_id_bucket_suffix("cloud-soc-wazuh-assets-602664594292-d7252a74")

    runner.import_resource.assert_called_once_with(
        "random_id.bucket_suffix",
        "d7252a74"
    )


@patch("cloudsoc.terraform.imports.EC2Service")
@patch("cloudsoc.terraform.imports.IAMService")
@patch("cloudsoc.terraform.imports.S3Service")
@patch("cloudsoc.terraform.imports.ECRService")
def test_import_s3_objects_imports_existing_objects(
    mock_ecr_service,
    mock_s3_service,
    mock_iam_service,
    mock_ec2_service,
):
    runner = MagicMock(spec=TerraformRunner)
    runner.state_contains.return_value = False

    s3_client = mock_s3_service.return_value
    s3_client.list_buckets.return_value = [
        S3Bucket(
            name="cloud-soc-wazuh-assets-123456789",
            creation_date="",
            region="us-east-1",
            tags={"Project": "cloud-soc"},
        )
    ]
    s3_client.get_bucket_versioning.return_value = {"Status": "Enabled"}
    s3_client.list_objects.return_value = [
        {"Key": "wazuh-docker/docker-compose.yml"},
        {"Key": "wazuh-docker/config/certs.yml"},
    ]

    importer = ResourceImporter(tf_runner=runner)
    importer._import_s3_resources()

    imported_addresses = [call.args[0] for call in runner.import_resource.call_args_list]
    assert "aws_s3_bucket.wazuh_assets" in imported_addresses
    assert "aws_s3_bucket_versioning.wazuh_assets" in imported_addresses
    assert "aws_s3_object.wazuh_docker_compose" in imported_addresses
    assert "aws_s3_object.wazuh_config_certs" in imported_addresses


@patch("cloudsoc.terraform.imports.EC2Service")
@patch("cloudsoc.terraform.imports.IAMService")
@patch("cloudsoc.terraform.imports.S3Service")
@patch("cloudsoc.terraform.imports.ECRService")
def test_import_iam_policy_attachments_imports_existing_attachments(
    mock_ecr_service,
    mock_s3_service,
    mock_iam_service,
    mock_ec2_service,
):
    runner = MagicMock(spec=TerraformRunner)
    runner.state_contains.return_value = False

    iam_client = mock_iam_service.return_value
    iam_client.get_policy_arn.side_effect = [
        "arn:aws:iam::602664594292:policy/wazuh-ec2-policy",
        "arn:aws:iam::602664594292:policy/victim-ec2-policy",
    ]

    importer = ResourceImporter(tf_runner=runner)
    importer._import_iam_policy_attachments()

    expected_calls = [
        ("aws_iam_role_policy_attachment.attach_wazuh_policy", "wazuh-ec2-role:arn:aws:iam::602664594292:policy/wazuh-ec2-policy"),
        ("aws_iam_role_policy_attachment.attach_ssm_managed", "wazuh-ec2-role:arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"),
        ("aws_iam_role_policy_attachment.attach_victim_ssm_managed", "victim-ec2-role:arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"),
        ("aws_iam_role_policy_attachment.attach_victim_policy", "victim-ec2-role:arn:aws:iam::602664594292:policy/victim-ec2-policy"),
    ]

    actual_calls = [call.args for call in runner.import_resource.call_args_list]
    assert actual_calls == expected_calls
