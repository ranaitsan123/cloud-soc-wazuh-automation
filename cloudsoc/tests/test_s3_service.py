"""Tests for AWS S3 service."""

import pytest
from unittest.mock import Mock, patch

from cloudsoc.aws.s3 import S3Service


@pytest.fixture
def s3_service():
    """Create S3Service instance for testing."""
    with patch("cloudsoc.aws.s3.boto3.Session"):
        yield S3Service(region="eu-north-1")


def test_delete_bucket_force_deletes_object_versions(s3_service):
    """Force delete should remove all versions and delete markers before deleting the bucket."""
    paginator = Mock()
    paginator.paginate.return_value = [
        {
            "Versions": [
                {"Key": "file1.txt", "VersionId": "v1"},
                {"Key": "file2.txt", "VersionId": "v2"}
            ],
            "DeleteMarkers": [
                {"Key": "file1.txt", "VersionId": "m1"}
            ]
        }
    ]
    s3_service.client.get_paginator.return_value = paginator
    s3_service.client.delete_objects = Mock()
    s3_service.client.delete_bucket = Mock()

    result = s3_service.delete_bucket("cloud-soc-wazuh-assets-123", force=True)

    assert result is True
    s3_service.client.get_paginator.assert_called_once_with("list_object_versions")
    s3_service.client.delete_objects.assert_called_once_with(
        Bucket="cloud-soc-wazuh-assets-123",
        Delete={
            "Objects": [
                {"Key": "file1.txt", "VersionId": "v1"},
                {"Key": "file2.txt", "VersionId": "v2"},
                {"Key": "file1.txt", "VersionId": "m1"}
            ],
            "Quiet": True,
        },
    )
    s3_service.client.delete_bucket.assert_called_once_with(Bucket="cloud-soc-wazuh-assets-123")
