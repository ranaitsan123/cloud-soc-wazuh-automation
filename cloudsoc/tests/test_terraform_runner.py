"""Tests for Terraform runner"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError


@pytest.fixture
def temp_tf_dir(tmp_path):
    """Create temporary Terraform directory"""
    tf_dir = tmp_path / "terraform"
    tf_dir.mkdir()
    (tf_dir / "main.tf").touch()
    return tf_dir


def test_terraform_init(temp_tf_dir):
    """Test Terraform initialization"""
    with patch("cloudsoc.terraform.runner.run_command") as mock_run:
        runner = TerraformRunner(terraform_dir=temp_tf_dir)
        runner.init()

        # Verify the command was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "terraform" in call_args[0][0]
        assert "init" in call_args[0][0]


def test_terraform_init_with_backend_config(temp_tf_dir):
    """Test Terraform init passes backend configuration"""
    with patch("cloudsoc.terraform.runner.run_command") as mock_run:
        backend_config = {
            "bucket": "my-bucket",
            "key": "cloud-soc/terraform.tfstate",
            "region": "eu-north-1",
            "dynamodb_table": "terraform-state-lock",
        }
        runner = TerraformRunner(
            terraform_dir=temp_tf_dir,
            backend_config=backend_config,
        )
        runner.init()

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "terraform" in call_args
        assert "init" in call_args
        assert "-backend-config" in call_args
        assert "bucket=my-bucket" in call_args
        assert "key=cloud-soc/terraform.tfstate" in call_args
        assert "region=eu-north-1" in call_args
        assert "dynamodb_table=terraform-state-lock" in call_args


def test_terraform_plan(temp_tf_dir):
    """Test Terraform planning"""
    with patch("cloudsoc.terraform.runner.run_command") as mock_run:
        runner = TerraformRunner(terraform_dir=temp_tf_dir)
        plan_file = runner.plan()

        assert plan_file == "tfplan"
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "plan" in call_args[0][0]


def test_terraform_invalid_dir():
    """Test initialization with invalid directory"""
    with pytest.raises(ValueError):
        TerraformRunner(terraform_dir=Path("/nonexistent"))
