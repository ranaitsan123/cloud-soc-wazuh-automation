"""Resource import mechanism for existing AWS resources into Terraform state"""

from typing import List, Optional, Tuple, Dict
from pathlib import Path

from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.aws.iam import IAMService
from cloudsoc.aws.s3 import S3Service
from cloudsoc.aws.ecr import ECRService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.terraform.runner import TerraformRunner
from cloudsoc.utils.logger import logger


class ResourceImporter:
    """Imports existing AWS resources into Terraform state to prevent recreation."""

    def __init__(
        self,
        tf_runner: TerraformRunner,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize resource importer.

        Args:
            tf_runner: TerraformRunner instance
            settings: Optional Settings instance
        """
        self.tf_runner = tf_runner
        self.settings = settings or get_settings()
        self.ec2_service = EC2Service(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.iam_service = IAMService(profile=self.settings.project.aws.profile)
        self.s3_service = S3Service(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.ecr_service = ECRService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )

    def import_all_existing_resources(self) -> None:
        """Import all existing resources that match the project configuration."""
        logger.info("Checking for existing AWS resources to import...")

        # Import resources in order of dependencies
        self._import_iam_resources()
        self._import_iam_policy_attachments()
        self._import_vpc_and_networking()
        self._import_security_groups()
        self._import_instances()
        self._import_s3_resources()
        self._import_ecr_resources()

    def _import_iam_resources(self) -> None:
        """Import existing IAM resources."""
        logger.info("Importing existing IAM resources...")

        iam_resources = [
            ("aws_iam_role.wazuh_ec2_role", "wazuh-ec2-role", "role"),
            ("aws_iam_role.victim_ec2_role", "victim-ec2-role", "role"),
            ("aws_iam_policy.wazuh_ec2_policy", "wazuh-ec2-policy", "policy"),
            ("aws_iam_policy.victim_ec2_policy", "victim-ec2-policy", "policy"),
            ("aws_iam_instance_profile.wazuh_instance_profile", "wazuh-instance-profile", "instance_profile"),
            ("aws_iam_instance_profile.victim_instance_profile", "victim-instance-profile", "instance_profile"),
        ]

        for address, name, resource_type in iam_resources:
            if self.tf_runner.state_contains(address):
                logger.debug(f"Terraform state already contains {address}")
                continue

            resource_id = None
            if resource_type == "role":
                role = self.iam_service.get_role(name)
                resource_id = role.name if role else None
            elif resource_type == "policy":
                resource_id = self.iam_service.get_policy_arn(name)
            elif resource_type == "instance_profile":
                profile = self.iam_service.get_instance_profile(name)
                resource_id = profile.get("InstanceProfileName") if profile else None

            if resource_id:
                logger.info(f"Importing existing IAM resource: {address}")
                self.tf_runner.import_resource(address, resource_id)
            else:
                logger.debug(f"No existing IAM {resource_type} found for {name}")

    def _import_vpc_and_networking(self) -> None:
        """Import existing VPC and networking resources."""
        logger.info("Importing existing VPC and networking resources...")

        # Find VPC by project tag
        vpc = self.ec2_service.find_vpc(project_tag=self.settings.project.tag)

        if not vpc:
            logger.debug("No existing VPC found with project tag")
            return

        # Import VPC
        if not self.tf_runner.state_contains("aws_vpc.wazuh_vpc"):
            logger.info(f"Importing VPC: {vpc.id}")
            self.tf_runner.import_resource("aws_vpc.wazuh_vpc", vpc.id)
        else:
            logger.debug("VPC already in state")

        # Import subnets
        subnets = self.ec2_service.find_subnets(vpc_id=vpc.id)
        subnet_mappings = {
            "management_private": "wazuh-management-private-subnet",
            "production_private": "wazuh-production-private-subnet",
            "nat_public": "wazuh-nat-public-subnet",
        }

        for subnet_key, subnet_name in subnet_mappings.items():
            address = f"aws_subnet.{subnet_key}"

            if self.tf_runner.state_contains(address):
                logger.debug(f"Subnet already in state: {address}")
                continue

            matching_subnet = next(
                (s for s in subnets if s.name == subnet_name),
                None
            )

            if matching_subnet:
                logger.info(f"Importing subnet: {address} ({matching_subnet.id})")
                self.tf_runner.import_resource(address, matching_subnet.id)
            else:
                logger.debug(f"No existing subnet found for {subnet_name}")

        # Import internet gateway
        if not self.tf_runner.state_contains("aws_internet_gateway.igw"):
            igw_id = self._find_internet_gateway_for_vpc(vpc.id)
            if igw_id:
                logger.info(f"Importing internet gateway: {igw_id}")
                self.tf_runner.import_resource("aws_internet_gateway.igw", igw_id)

        # Import NAT gateway and EIP
        nat_gateway_id = None
        if not self.tf_runner.state_contains("aws_nat_gateway.nat"):
            nat_gateway_id = self._find_nat_gateway_for_vpc(vpc.id)
            if nat_gateway_id:
                logger.info(f"Importing NAT gateway: {nat_gateway_id}")
                self.tf_runner.import_resource("aws_nat_gateway.nat", nat_gateway_id)

        if not self.tf_runner.state_contains("aws_eip.nat"):
            eip_id = self._find_eip_for_nat_gateway(nat_gateway_id=nat_gateway_id)
            if eip_id:
                logger.info(f"Importing EIP: {eip_id}")
                self.tf_runner.import_resource("aws_eip.nat", eip_id)

        # Import route tables
        if not self.tf_runner.state_contains("aws_route_table.public"):
            public_rt_id = self._find_route_table_for_vpc(vpc.id, "public")
            if public_rt_id:
                logger.info(f"Importing public route table: {public_rt_id}")
                self.tf_runner.import_resource("aws_route_table.public", public_rt_id)

        if not self.tf_runner.state_contains("aws_route_table.private"):
            private_rt_id = self._find_route_table_for_vpc(vpc.id, "private")
            if private_rt_id:
                logger.info(f"Importing private route table: {private_rt_id}")
                self.tf_runner.import_resource("aws_route_table.private", private_rt_id)

        # Import route table associations
        self._import_route_table_associations(vpc.id)

    def _import_security_groups(self) -> None:
        """Import existing security groups."""
        logger.info("Importing existing security groups...")

        vpc = self.ec2_service.find_vpc(project_tag=self.settings.project.tag)
        if not vpc:
            logger.debug("No VPC found, skipping security group import")
            return

        sg_mappings = [
            ("aws_security_group.wazuh_sg", "wazuh-sg"),
            ("aws_security_group.victim_sg", "victim-sg"),
        ]

        for address, sg_name in sg_mappings:
            if self.tf_runner.state_contains(address):
                logger.debug(f"Security group already in state: {address}")
                continue

            security_groups = self.ec2_service.find_security_groups(
                vpc_id=vpc.id,
                names=[sg_name]
            )

            if security_groups:
                sg = security_groups[0]
                logger.info(f"Importing security group: {address} ({sg.id})")
                self.tf_runner.import_resource(address, sg.id)
            else:
                logger.debug(f"No existing security group found for {sg_name}")

    def _import_instances(self) -> None:
        """Import existing EC2 instances."""
        logger.info("Importing existing EC2 instances...")

        # Find instances by project tag (allow all states)
        instances = self.ec2_service.find_instances(
            project_tag=self.settings.project.tag,
            states=["running", "stopped", "pending"]
        )

        instance_mappings = {
            "aws_instance.wazuh_server": "wazuh-server",
            "aws_instance.victim_server": "victim-server",
        }

        for address, instance_name in instance_mappings.items():
            if self.tf_runner.state_contains(address):
                logger.debug(f"Instance already in state: {address}")
                continue

            matching_instance = next(
                (i for i in instances if i.tags.get("Name") == instance_name),
                None
            )

            if matching_instance:
                logger.info(f"Importing instance: {address} ({matching_instance.id})")
                self.tf_runner.import_resource(address, matching_instance.id)
            else:
                logger.debug(f"No existing instance found for {instance_name}")

    def _import_s3_resources(self) -> None:
        """Import existing S3 bucket, versioning, and tracked objects."""
        logger.info("Importing existing S3 resources...")

        # Try to find S3 bucket by tag
        bucket_name = self._find_s3_bucket_by_tag(
            project_tag=self.settings.project.tag
        )

        if not bucket_name:
            logger.debug("No existing S3 bucket found with project tag")
            return

        self._import_random_id_bucket_suffix(bucket_name)

        if not self.tf_runner.state_contains("aws_s3_bucket.wazuh_assets"):
            logger.info(f"Importing S3 bucket: {bucket_name}")
            self.tf_runner.import_resource("aws_s3_bucket.wazuh_assets", bucket_name)

        versioning = self.s3_service.get_bucket_versioning(bucket_name)
        if versioning.get("Status") == "Enabled" and not self.tf_runner.state_contains("aws_s3_bucket_versioning.wazuh_assets"):
            logger.info(f"Importing S3 bucket versioning for: {bucket_name}")
            self.tf_runner.import_resource("aws_s3_bucket_versioning.wazuh_assets", bucket_name)

        object_mappings = [
            ("aws_s3_object.wazuh_docker_compose", "wazuh-docker/docker-compose.yml"),
            ("aws_s3_object.wazuh_certs_generator", "wazuh-docker/generate-indexer-certs.yml"),
            ("aws_s3_object.wazuh_config_certs", "wazuh-docker/config/certs.yml"),
            ("aws_s3_object.wazuh_manager_conf", "wazuh-docker/config/wazuh_cluster/wazuh_manager.conf"),
            ("aws_s3_object.wazuh_indexer_config", "wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml"),
            ("aws_s3_object.wazuh_indexer_users", "wazuh-docker/config/wazuh_indexer/internal_users.yml"),
            ("aws_s3_object.wazuh_dashboard_config", "wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml"),
            ("aws_s3_object.wazuh_dashboard_wazuh_yml", "wazuh-docker/config/wazuh_dashboard/wazuh.yml"),
        ]

        existing_objects = {
            obj.get("Key")
            for obj in self.s3_service.list_objects(bucket_name)
            if obj.get("Key")
        }

        for address, key in object_mappings:
            if self.tf_runner.state_contains(address):
                logger.debug(f"S3 object already in state: {address}")
                continue

            if key in existing_objects:
                logger.info(f"Importing S3 object: {address} ({bucket_name}/{key})")
                self.tf_runner.import_resource(address, f"{bucket_name}/{key}")
            else:
                logger.debug(f"S3 object not found, skipping import: {address} ({key})")

    def _import_iam_policy_attachments(self) -> None:
        """Import IAM role policy attachments if they exist."""
        logger.info("Importing existing IAM policy attachments...")

        attachments = [
            (
                "aws_iam_role_policy_attachment.attach_wazuh_policy",
                "wazuh-ec2-role",
                "wazuh-ec2-policy",
            ),
            (
                "aws_iam_role_policy_attachment.attach_ssm_managed",
                "wazuh-ec2-role",
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            ),
            (
                "aws_iam_role_policy_attachment.attach_victim_ssm_managed",
                "victim-ec2-role",
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            ),
            (
                "aws_iam_role_policy_attachment.attach_victim_policy",
                "victim-ec2-role",
                "victim-ec2-policy",
            ),
        ]

        for address, role_name, policy_identifier in attachments:
            if self.tf_runner.state_contains(address):
                logger.debug(f"IAM attachment already in state: {address}")
                continue

            policy_arn = policy_identifier
            if policy_identifier.endswith("-policy"):
                policy_arn = self.iam_service.get_policy_arn(policy_identifier)
                if not policy_arn:
                    logger.debug(f"No existing policy found for {policy_identifier}")
                    continue

            attachment_id = f"{role_name}:{policy_arn}"
            logger.info(f"Importing IAM attachment: {address} ({attachment_id})")
            self.tf_runner.import_resource(address, attachment_id)

    def _import_random_id_bucket_suffix(self, bucket_name: str) -> None:
        """Import the random_id used to generate the S3 bucket suffix."""
        if self.tf_runner.state_contains("random_id.bucket_suffix"):
            logger.debug("Random id bucket suffix already in state")
            return

        suffix = bucket_name.split("-")[-1]
        if not suffix:
            logger.warning(
                f"Could not determine random bucket suffix from bucket name: {bucket_name}"
            )
            return

        logger.info(f"Importing random bucket suffix for S3 bucket: {suffix}")
        self.tf_runner.import_resource("random_id.bucket_suffix", suffix)

    def _import_ecr_resources(self) -> None:
        """Import existing ECR repositories."""
        logger.info("Importing existing ECR resources...")

        ecr_repos = [
            ("aws_ecr_repository.manager_repo", "cloud-soc-wazuh-manager"),
            ("aws_ecr_repository.victim_repo", "cloud-soc-victim"),
        ]

        for address, repo_name in ecr_repos:
            if self.tf_runner.state_contains(address):
                logger.debug(f"ECR repository already in state: {address}")
                continue

            if self.ecr_service.get_repository(repo_name):
                logger.info(f"Importing ECR repository: {address} ({repo_name})")
                self.tf_runner.import_resource(address, repo_name)
            else:
                logger.debug(f"No existing ECR repository found for {repo_name}")

    # Helper methods for finding AWS resources

    def _import_route_table_associations(self, vpc_id: str) -> None:
        """Import route table associations."""
        try:
            # Get all subnets in the VPC
            subnets = self.ec2_service.find_subnets(vpc_id=vpc_id)
            
            for subnet in subnets:
                # Find route table for this subnet
                try:
                    response = self.ec2_service.client.describe_route_tables(
                        Filters=[
                            {"Name": "association.subnet-id", "Values": [subnet.id]}
                        ]
                    )
                    route_tables = response.get("RouteTables", [])
                    
                    if route_tables:
                        rt = route_tables[0]
                        associations = rt.get("Associations", [])
                        
                        for assoc in associations:
                            if assoc.get("SubnetId") == subnet.id:
                                # Determine association resource name
                                if "nat-public" in subnet.name or "nat_public" in subnet.name:
                                    address = "aws_route_table_association.nat_public"
                                elif "management" in subnet.name:
                                    address = "aws_route_table_association.management_private"
                                elif "production" in subnet.name:
                                    address = "aws_route_table_association.production_private"
                                else:
                                    continue
                                
                                if not self.tf_runner.state_contains(address):
                                    assoc_id = assoc.get("RouteTableAssociationId")
                                    if assoc_id:
                                        logger.info(f"Importing route table association: {address}")
                                        self.tf_runner.import_resource(address, assoc_id)
                                else:
                                    logger.debug(f"Route table association already in state: {address}")
                except Exception as e:
                    logger.warning(f"Failed to import route table association for {subnet.id}: {e}")
        except Exception as e:
            logger.warning(f"Failed to import route table associations: {e}")

    def _find_internet_gateway_for_vpc(self, vpc_id: str) -> Optional[str]:
        """Find internet gateway attached to a VPC."""
        try:
            response = self.ec2_service.client.describe_internet_gateways(
                Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
            )
            igws = response.get("InternetGateways", [])
            if igws:
                return igws[0]["InternetGatewayId"]
        except Exception as e:
            logger.warning(f"Failed to find internet gateway: {e}")
        return None

    def _find_nat_gateway_for_vpc(self, vpc_id: str) -> Optional[str]:
        """Find NAT gateway in a VPC."""
        try:
            response = self.ec2_service.client.describe_nat_gateways(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "state", "Values": ["available"]}
                ]
            )
            nat_gateways = response.get("NatGateways", [])
            if nat_gateways:
                return nat_gateways[0]["NatGatewayId"]
        except Exception as e:
            logger.warning(f"Failed to find NAT gateway: {e}")
        return None

    def _find_eip_for_nat_gateway(self, nat_gateway_id: Optional[str]) -> Optional[str]:
        """Find EIP associated with a NAT gateway."""
        if not nat_gateway_id:
            return None

        try:
            response = self.ec2_service.client.describe_nat_gateways(
                NatGatewayIds=[nat_gateway_id]
            )
            nat_gateways = response.get("NatGateways", [])
            if nat_gateways and "NatGatewayAddresses" in nat_gateways[0]:
                addresses = nat_gateways[0]["NatGatewayAddresses"]
                if addresses and "AllocationId" in addresses[0]:
                    return addresses[0]["AllocationId"]
        except Exception as e:
            logger.warning(f"Failed to find EIP for NAT gateway: {e}")
        return None

    def _find_route_table_for_vpc(self, vpc_id: str, route_table_type: str) -> Optional[str]:
        """Find route table for a VPC."""
        try:
            # Try to find by tag first
            response = self.ec2_service.client.describe_route_tables(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "tag:Name", "Values": [f"wazuh-{route_table_type}-rt"]}
                ]
            )
            route_tables = response.get("RouteTables", [])
            if route_tables:
                return route_tables[0]["RouteTableId"]
        except Exception as e:
            logger.warning(f"Failed to find route table: {e}")
        return None

    def _find_s3_bucket_by_tag(self, project_tag: str) -> Optional[str]:
        """Find an existing S3 bucket by project tag or by the expected Cloud SOC naming pattern."""
        try:
            buckets = self.s3_service.list_buckets()
            for bucket in buckets:
                bucket_tags = getattr(bucket, "tags", {}) or {}
                if bucket_tags.get("Project") == project_tag:
                    return bucket.name

            for bucket in buckets:
                bucket_name = getattr(bucket, "name", "")
                if bucket_name.startswith("cloud-soc-wazuh-assets"):
                    return bucket_name
        except Exception as e:
            logger.warning(f"Failed to find S3 bucket by tag: {e}")
        return None
