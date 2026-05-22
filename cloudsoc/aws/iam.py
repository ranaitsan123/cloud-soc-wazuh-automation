"""IAM service for AWS interactions"""

from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger
from cloudsoc.models.resources import IAMRole


class IAMService:
    """Service for IAM operations using Boto3"""

    def __init__(self, profile: Optional[str] = None):
        """
        Initialize IAM service.

        Args:
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("iam")
        self.logger = logger

    def get_role(self, role_name: str) -> Optional[IAMRole]:
        """
        Get IAM role by name.

        Args:
            role_name: Name of the role

        Returns:
            IAMRole object or None if not found
        """
        try:
            response = self.client.get_role(RoleName=role_name)
            role_data = response["Role"]

            return IAMRole(
                name=role_data["RoleName"],
                arn=role_data["Arn"],
                create_date=str(role_data["CreateDate"]),
                trust_policy=role_data.get("AssumeRolePolicyDocument", {})
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                self.logger.debug(f"Role not found: {role_name}")
            else:
                self.logger.error(f"Failed to get role {role_name}: {e}")
            return None

    def get_policy_arn(self, policy_name: str) -> Optional[str]:
        """
        Get the ARN for an IAM policy by name.

        Args:
            policy_name: Name of the policy

        Returns:
            Policy ARN if found, otherwise None
        """
        try:
            paginator = self.client.get_paginator("list_policies")
            for page in paginator.paginate(Scope="Local"):
                for policy_data in page.get("Policies", []):
                    if policy_data.get("PolicyName") == policy_name:
                        return policy_data.get("Arn")
        except ClientError as e:
            self.logger.error(f"Failed to list IAM policies: {e}")
        return None

    def get_instance_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an IAM instance profile by name.

        Args:
            profile_name: Name of the instance profile

        Returns:
            Instance profile data if found, otherwise None
        """
        try:
            response = self.client.get_instance_profile(InstanceProfileName=profile_name)
            return response.get("InstanceProfile")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                self.logger.debug(f"Instance profile not found: {profile_name}")
            else:
                self.logger.error(f"Failed to get instance profile {profile_name}: {e}")
            return None

    def list_roles(self, path_prefix: str = "/") -> List[IAMRole]:
        """
        List IAM roles.

        Args:
            path_prefix: Optional path prefix to filter

        Returns:
            List of IAMRole objects
        """
        try:
            roles = []
            paginator = self.client.get_paginator("list_roles")

            for page in paginator.paginate(PathPrefix=path_prefix):
                for role_data in page.get("Roles", []):
                    roles.append(
                        IAMRole(
                            name=role_data["RoleName"],
                            arn=role_data["Arn"],
                            create_date=str(role_data["CreateDate"]),
                            trust_policy=role_data.get("AssumeRolePolicyDocument", {})
                        )
                    )

            self.logger.info(f"Found {len(roles)} roles")
            return roles

        except ClientError as e:
            self.logger.error(f"Failed to list roles: {e}")
            return []

    def create_role(
        self,
        role_name: str,
        assume_role_policy: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[IAMRole]:
        """
        Create IAM role.

        Args:
            role_name: Name for the new role
            assume_role_policy: Trust policy document
            tags: Optional tags to attach

        Returns:
            Created IAMRole object or None if failed
        """
        import json

        try:
            kwargs = {
                "RoleName": role_name,
                "AssumeRolePolicyDocument": json.dumps(assume_role_policy)
            }

            if tags:
                kwargs["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

            response = self.client.create_role(**kwargs)
            role_data = response["Role"]

            self.logger.info(f"✓ Created role: {role_name}")

            return IAMRole(
                name=role_data["RoleName"],
                arn=role_data["Arn"],
                create_date=str(role_data["CreateDate"]),
                trust_policy=assume_role_policy
            )

        except ClientError as e:
            self.logger.error(f"Failed to create role {role_name}: {e}")
            return None

    def delete_role(self, role_name: str) -> bool:
        """
        Delete IAM role.

        Args:
            role_name: Name of role to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_role(RoleName=role_name)
            self.logger.info(f"✓ Deleted role: {role_name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to delete role {role_name}: {e}")
            return False
