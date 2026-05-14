"""Tests for AWS EC2 service"""

import pytest
from unittest.mock import Mock, patch
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.models.resources import VPC, EC2Instance


@pytest.fixture
def ec2_service():
    """Create EC2Service instance for testing"""
    with patch("boto3.Session"):
        return EC2Service(region="eu-north-1")


def test_find_vpc_by_name(ec2_service):
    """Test finding VPC by name tag"""
    # Mock the boto3 response
    mock_response = {
        "Vpcs": [
            {
                "VpcId": "vpc-12345",
                "CidrBlock": "10.0.0.0/16",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "wazuh-vpc"}]
            }
        ]
    }

    ec2_service.client.describe_vpcs = Mock(return_value=mock_response)

    # Test
    vpc = ec2_service.find_vpc(name="wazuh-vpc")

    assert vpc is not None
    assert vpc.id == "vpc-12345"
    assert vpc.cidr_block == "10.0.0.0/16"
    assert vpc.name == "wazuh-vpc"


def test_find_vpc_not_found(ec2_service):
    """Test VPC not found scenario"""
    ec2_service.client.describe_vpcs = Mock(return_value={"Vpcs": []})

    vpc = ec2_service.find_vpc(name="nonexistent")

    assert vpc is None


def test_find_instances(ec2_service):
    """Test finding EC2 instances"""
    mock_response = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-12345",
                        "InstanceType": "t2.micro",
                        "State": {"Name": "running"},
                        "VpcId": "vpc-12345",
                        "SubnetId": "subnet-12345",
                        "PrivateIpAddress": "10.0.1.10",
                        "PublicIpAddress": "1.2.3.4",
                        "Tags": [{"Key": "Name", "Value": "wazuh-manager"}]
                    }
                ]
            }
        ]
    }

    ec2_service.client.describe_instances = Mock(return_value=mock_response)

    instances = ec2_service.find_instances(vpc_id="vpc-12345")

    assert len(instances) == 1
    assert instances[0].id == "i-12345"
    assert instances[0].state == "running"
