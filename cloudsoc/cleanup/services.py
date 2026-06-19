"""Cleanup and resource management services"""

from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.models.resources import NetworkInterface


class NetworkCleanupService:
    """Service for cleaning up orphaned network resources"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize cleanup service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.ec2_client = session.client("ec2", region_name=region)
        self.logger = logger

    def find_orphaned_enis(self, vpc_id: Optional[str] = None) -> List[NetworkInterface]:
        """
        Find orphaned (detached) ENIs.

        Args:
            vpc_id: Optional VPC ID to filter

        Returns:
            List of detached NetworkInterface objects
        """
        filters = [{"Name": "status", "Values": ["available"]}]

        if vpc_id:
            filters.append({"Name": "vpc-id", "Values": [vpc_id]})

        try:
            response = self.ec2_client.describe_network_interfaces(Filters=filters)
            enis = []

            for eni_data in response.get("NetworkInterfaces", []):
                enis.append(
                    NetworkInterface(
                        id=eni_data["NetworkInterfaceId"],
                        vpc_id=eni_data["VpcId"],
                        subnet_id=eni_data["SubnetId"],
                        status=eni_data["Status"],
                        instance_id=None,  # These are detached
                        private_ips=[ip["PrivateIpAddress"] for ip in eni_data.get("PrivateIpAddresses", [])]
                    )
                )

            self.logger.info(f"Found {len(enis)} orphaned ENIs")
            return enis

        except ClientError as e:
            self.logger.error(f"Failed to find orphaned ENIs: {e}")
            return []

    def delete_eni(self, eni_id: str) -> bool:
        """
        Delete a network interface.

        Args:
            eni_id: ENI ID to delete

        Returns:
            True if successful
        """
        try:
            self.ec2_client.delete_network_interface(NetworkInterfaceId=eni_id)
            self.logger.info(f"✓ Deleted ENI: {eni_id}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to delete ENI {eni_id}: {e}")
            return False

    def cleanup_orphaned_enis(self, vpc_id: Optional[str] = None) -> int:
        """
        Delete all orphaned ENIs in a VPC.

        Args:
            vpc_id: Optional VPC ID to filter

        Returns:
            Number of deleted ENIs
        """
        enis = self.find_orphaned_enis(vpc_id=vpc_id)

        if not enis:
            self.logger.info("No orphaned ENIs found")
            return 0

        deleted_count = 0
        for eni in enis:
            if self.delete_eni(eni.id):
                deleted_count += 1

        self.logger.info(f"Cleaned up {deleted_count} orphaned ENIs")
        return deleted_count


class VPCCleanupService:
    """Service for cleaning up VPC resources"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize VPC cleanup service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.ec2_client = session.client("ec2", region_name=region)
        self.ec2_service = EC2Service(region=region, profile=profile)
        self.logger = logger

    def cleanup_vpc_instances(self, vpc_id: str) -> int:
        """
        Terminate all instances in a VPC.

        Args:
            vpc_id: VPC ID to clean

        Returns:
            Number of terminated instances
        """
        instances = self.ec2_service.find_instances(
            vpc_id=vpc_id,
            states=["running", "stopped"]
        )

        if not instances:
            self.logger.info(f"No instances found in VPC {vpc_id}")
            return 0

        instance_ids = [inst.id for inst in instances]
        success = self.ec2_service.terminate_instances(instance_ids)

        return len(instance_ids) if success else 0

    def cleanup_security_groups(self, vpc_id: str) -> int:
        """
        Delete security groups in a VPC (except default).

        Args:
            vpc_id: VPC ID to clean

        Returns:
            Number of deleted security groups
        """
        try:
            response = self.ec2_client.describe_security_groups(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )

            deleted_count = 0
            for sg in response.get("SecurityGroups", []):
                if sg["GroupName"] != "default":
                    try:
                        self.ec2_client.delete_security_group(GroupId=sg["GroupId"])
                        self.logger.info(f"✓ Deleted security group: {sg['GroupId']}")
                        deleted_count += 1
                    except ClientError as e:
                        self.logger.warning(f"Failed to delete SG {sg['GroupId']}: {e}")

            return deleted_count

        except ClientError as e:
            self.logger.error(f"Failed to cleanup security groups: {e}")
            return 0
