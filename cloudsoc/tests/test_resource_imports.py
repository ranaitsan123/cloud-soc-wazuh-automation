"""Tests for Terraform resource import helpers."""

from unittest.mock import MagicMock, patch

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
