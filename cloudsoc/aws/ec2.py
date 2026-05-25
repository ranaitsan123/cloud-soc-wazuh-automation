"""EC2 service for AWS interactions"""

from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger
from cloudsoc.models.resources import VPC, Subnet, SecurityGroup, EC2Instance


class EC2Service:
    """Service for EC2 operations using Boto3"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize EC2 service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("ec2", region_name=region)
        self.region = region
        self.logger = logger

    def find_vpc(self, name: Optional[str] = None, project_tag: Optional[str] = None) -> Optional[VPC]:
        """
        Find VPC by name or project tag.

        Args:
            name: VPC name tag
            project_tag: Project tag value

        Returns:
            VPC object or None if not found
        """
        filters = []

        if name:
            filters.append({"Name": "tag:Name", "Values": [name]})

        if project_tag:
            filters.append({"Name": "tag:Project", "Values": [project_tag]})

        try:
            response = self.client.describe_vpcs(Filters=filters)
            vpcs = response.get("Vpcs", [])

            if not vpcs:
                self.logger.info(f"No VPC found with filters: {filters}")
                return None

            vpc_data = vpcs[0]
            return VPC(
                id=vpc_data["VpcId"],
                cidr_block=vpc_data["CidrBlock"],
                state=vpc_data["State"],
                tags={tag["Key"]: tag["Value"] for tag in vpc_data.get("Tags", [])},
                name=next(
                    (tag["Value"] for tag in vpc_data.get("Tags", []) if tag["Key"] == "Name"),
                    ""
                ),
                project=next(
                    (tag["Value"] for tag in vpc_data.get("Tags", []) if tag["Key"] == "Project"),
                    ""
                )
            )

        except ClientError as e:
            self.logger.error(f"Failed to find VPC: {e}")
            return None

    def find_subnets(self, vpc_id: str, name: Optional[str] = None) -> List[Subnet]:
        """
        Find subnets in a VPC.

        Args:
            vpc_id: VPC ID to search in
            name: Optional subnet name pattern

        Returns:
            List of Subnet objects
        """
        filters = [{"Name": "vpc-id", "Values": [vpc_id]}]

        if name:
            filters.append({"Name": "tag:Name", "Values": [name]})

        try:
            response = self.client.describe_subnets(Filters=filters)
            subnets = []

            for subnet_data in response.get("Subnets", []):
                subnets.append(
                    Subnet(
                        id=subnet_data["SubnetId"],
                        vpc_id=subnet_data["VpcId"],
                        cidr_block=subnet_data["CidrBlock"],
                        availability_zone=subnet_data["AvailabilityZone"],
                        state=subnet_data["State"],
                        name=next(
                            (tag["Value"] for tag in subnet_data.get("Tags", []) if tag["Key"] == "Name"),
                            ""
                        )
                    )
                )

            self.logger.info(f"Found {len(subnets)} subnets in {vpc_id}")
            return subnets

        except ClientError as e:
            self.logger.error(f"Failed to find subnets: {e}")
            return []

    def find_security_groups(
        self,
        vpc_id: str,
        names: Optional[List[str]] = None
    ) -> List[SecurityGroup]:
        """
        Find security groups in a VPC.

        Args:
            vpc_id: VPC ID to search in
            names: Optional list of security group names

        Returns:
            List of SecurityGroup objects
        """
        filters = [{"Name": "vpc-id", "Values": [vpc_id]}]

        if names:
            filters.append({"Name": "group-name", "Values": names})

        try:
            response = self.client.describe_security_groups(Filters=filters)
            groups = []

            for group_data in response.get("SecurityGroups", []):
                groups.append(
                    SecurityGroup(
                        id=group_data["GroupId"],
                        vpc_id=group_data["VpcId"],
                        name=group_data["GroupName"],
                        description=group_data.get("GroupDescription", ""),
                        state=group_data.get("State", "available"),
                        tags={tag["Key"]: tag["Value"] for tag in group_data.get("Tags", [])}
                    )
                )

            self.logger.info(f"Found {len(groups)} security groups in {vpc_id}")
            return groups

        except ClientError as e:
            self.logger.error(f"Failed to find security groups: {e}")
            return []

    def find_instances(
        self,
        vpc_id: Optional[str] = None,
        project_tag: Optional[str] = None,
        states: Optional[List[str]] = None
    ) -> List[EC2Instance]:
        """
        Find EC2 instances.

        Args:
            vpc_id: Optional VPC ID to filter
            project_tag: Optional project tag value
            states: Optional instance states to filter (default: running)

        Returns:
            List of EC2Instance objects
        """
        if states is None:
            states = ["running"]

        filters = [{"Name": "instance-state-name", "Values": states}]

        if vpc_id:
            filters.append({"Name": "vpc-id", "Values": [vpc_id]})

        if project_tag:
            filters.append({"Name": "tag:Project", "Values": [project_tag]})

        try:
            response = self.client.describe_instances(Filters=filters)
            instances = []

            for reservation in response.get("Reservations", []):
                for instance_data in reservation.get("Instances", []):
                    instances.append(
                        EC2Instance(
                            id=instance_data["InstanceId"],
                            type=instance_data["InstanceType"],
                            state=instance_data["State"]["Name"],
                            vpc_id=instance_data.get("VpcId"),
                            subnet_id=instance_data.get("SubnetId"),
                            private_ip=instance_data.get("PrivateIpAddress"),
                            public_ip=instance_data.get("PublicIpAddress"),
                            tags={tag["Key"]: tag["Value"] for tag in instance_data.get("Tags", [])}
                        )
                    )

            self.logger.info(f"Found {len(instances)} instances")
            return instances

        except ClientError as e:
            self.logger.error(f"Failed to find instances: {e}")
            return []

    def get_instance(self, instance_id: str) -> Optional[EC2Instance]:
        """Get specific instance details"""
        try:
            response = self.client.describe_instances(InstanceIds=[instance_id])
            instance_data = response["Reservations"][0]["Instances"][0]

            return EC2Instance(
                id=instance_data["InstanceId"],
                type=instance_data["InstanceType"],
                state=instance_data["State"]["Name"],
                vpc_id=instance_data.get("VpcId"),
                subnet_id=instance_data.get("SubnetId"),
                private_ip=instance_data.get("PrivateIpAddress"),
                public_ip=instance_data.get("PublicIpAddress"),
                tags={tag["Key"]: tag["Value"] for tag in instance_data.get("Tags", [])}
            )

        except ClientError as e:
            self.logger.error(f"Failed to get instance {instance_id}: {e}")
            return None

    def terminate_instances(self, instance_ids: List[str]) -> bool:
        """
        Terminate EC2 instances.

        Args:
            instance_ids: List of instance IDs to terminate

        Returns:
            True if successful
        """
        if not instance_ids:
            self.logger.info("No instances to terminate")
            return True

        try:
            self.logger.warning(f"Terminating instances: {instance_ids}")
            self.client.terminate_instances(InstanceIds=instance_ids)
            self.logger.info("✓ Termination request sent")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to terminate instances: {e}")
            return False
