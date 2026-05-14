"""ECR service for AWS interactions"""

from typing import Optional, List
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger


class ECRService:
    """Service for ECR operations using Boto3"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize ECR service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("ecr", region_name=region)
        self.region = region
        self.logger = logger

    def list_repositories(self) -> List[dict]:
        """
        List ECR repositories.

        Returns:
            List of repository details
        """
        try:
            response = self.client.describe_repositories()
            repositories = []

            for repo in response.get("repositories", []):
                repositories.append({
                    "name": repo["repositoryName"],
                    "uri": repo["repositoryUri"],
                    "arn": repo["repositoryArn"],
                    "created_date": str(repo.get("createdAt", "")),
                    "image_count": repo.get("imageSizeInBytes", 0)
                })

            self.logger.info(f"Found {len(repositories)} repositories")
            return repositories

        except ClientError as e:
            self.logger.error(f"Failed to list repositories: {e}")
            return []

    def get_repository(self, name: str) -> Optional[dict]:
        """
        Get specific repository details.

        Args:
            name: Repository name

        Returns:
            Repository details or None
        """
        try:
            response = self.client.describe_repositories(repositoryNames=[name])
            repos = response.get("repositories", [])

            if repos:
                repo = repos[0]
                return {
                    "name": repo["repositoryName"],
                    "uri": repo["repositoryUri"],
                    "arn": repo["repositoryArn"],
                    "created_date": str(repo.get("createdAt", "")),
                    "image_count": repo.get("imageSizeInBytes", 0)
                }

            return None

        except ClientError as e:
            self.logger.error(f"Repository not found: {name}")
            return None

    def create_repository(self, name: str, tags: Optional[dict] = None) -> Optional[dict]:
        """
        Create ECR repository.

        Args:
            name: Repository name
            tags: Tags to attach

        Returns:
            Repository details or None
        """
        try:
            kwargs = {
                "repositoryName": name,
                "imageScanningConfiguration": {"scanOnPush": True},
                "encryptionConfiguration": {"encryptionType": "AES256"}
            }

            if tags:
                kwargs["tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

            response = self.client.create_repository(**kwargs)
            repo = response["repository"]

            self.logger.info(f"✓ Created repository: {name}")

            return {
                "name": repo["repositoryName"],
                "uri": repo["repositoryUri"],
                "arn": repo["repositoryArn"],
            }

        except ClientError as e:
            self.logger.error(f"Failed to create repository {name}: {e}")
            return None

    def delete_repository(self, name: str, force: bool = False) -> bool:
        """
        Delete ECR repository.

        Args:
            name: Repository name
            force: Force delete even if not empty

        Returns:
            True if successful
        """
        try:
            self.client.delete_repository(
                repositoryName=name,
                force=force
            )
            self.logger.info(f"✓ Deleted repository: {name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to delete repository {name}: {e}")
            return False

    def get_login_token(self) -> Optional[str]:
        """
        Get ECR login token for Docker.

        Returns:
            Login token or None
        """
        try:
            response = self.client.get_authorization_token()
            auth_data = response["authorizationData"][0]
            return auth_data["authorizationToken"]

        except ClientError as e:
            self.logger.error(f"Failed to get login token: {e}")
            return None
