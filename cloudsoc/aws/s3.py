"""S3 service for AWS interactions"""

from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger
from cloudsoc.models.resources import S3Bucket


class S3Service:
    """Service for S3 operations using Boto3"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize S3 service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("s3", region_name=region)
        self.region = region
        self.logger = logger

    def list_buckets(self) -> List[S3Bucket]:
        """
        List all S3 buckets.

        Returns:
            List of S3Bucket objects
        """
        try:
            response = self.client.list_buckets()
            buckets = []

            for bucket_data in response.get("Buckets", []):
                # Get tags for bucket
                tags = {}
                try:
                    tags_response = self.client.get_bucket_tagging(
                        Bucket=bucket_data["Name"]
                    )
                    tags = {
                        tag["Key"]: tag["Value"]
                        for tag in tags_response.get("TagSet", [])
                    }
                except ClientError:
                    pass  # Bucket might not have tags

                buckets.append(
                    S3Bucket(
                        name=bucket_data["Name"],
                        creation_date=str(bucket_data["CreationDate"]),
                        region=self.region,
                        tags=tags
                    )
                )

            self.logger.info(f"Found {len(buckets)} buckets")
            return buckets

        except ClientError as e:
            self.logger.error(f"Failed to list buckets: {e}")
            return []

    def find_bucket(self, name: str) -> Optional[S3Bucket]:
        """
        Find specific bucket by name.

        Args:
            name: Bucket name to find

        Returns:
            S3Bucket object or None if not found
        """
        try:
            location = self.client.get_bucket_location(Bucket=name)
            region = location.get("LocationConstraint", "us-east-1")

            # Get tags
            tags = {}
            try:
                tags_response = self.client.get_bucket_tagging(Bucket=name)
                tags = {
                    tag["Key"]: tag["Value"]
                    for tag in tags_response.get("TagSet", [])
                }
            except ClientError:
                pass

            # Get creation date from bucket versioning (fallback)
            response = self.client.head_bucket(Bucket=name)

            return S3Bucket(
                name=name,
                creation_date=response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("date", ""),
                region=region,
                tags=tags
            )

        except ClientError as e:
            self.logger.error(f"Bucket not found or not accessible: {name}")
            return None

    def create_bucket(
        self,
        name: str,
        region: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[S3Bucket]:
        """
        Create S3 bucket.

        Args:
            name: Bucket name
            region: Region for bucket (default: service region)
            tags: Tags to attach

        Returns:
            Created S3Bucket or None if failed
        """
        bucket_region = region or self.region

        try:
            if bucket_region == "us-east-1":
                self.client.create_bucket(Bucket=name)
            else:
                self.client.create_bucket(
                    Bucket=name,
                    CreateBucketConfiguration={"LocationConstraint": bucket_region}
                )

            # Add tags if provided
            if tags:
                self.client.put_bucket_tagging(
                    Bucket=name,
                    Tagging={
                        "TagSet": [{"Key": k, "Value": v} for k, v in tags.items()]
                    }
                )

            self.logger.info(f"✓ Created bucket: {name}")

            return S3Bucket(
                name=name,
                creation_date="",
                region=bucket_region,
                tags=tags or {}
            )

        except ClientError as e:
            self.logger.error(f"Failed to create bucket {name}: {e}")
            return None

    def delete_bucket(self, name: str, force: bool = False) -> bool:
        """
        Delete S3 bucket.

        Args:
            name: Bucket name
            force: Force delete even if not empty

        Returns:
            True if successful
        """
        try:
            if force:
                # Delete all objects first
                paginator = self.client.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=name):
                    for obj in page.get("Contents", []):
                        self.client.delete_object(Bucket=name, Key=obj["Key"])

            self.client.delete_bucket(Bucket=name)
            self.logger.info(f"✓ Deleted bucket: {name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to delete bucket {name}: {e}")
            return False

    def get_bucket_tags(self, name: str) -> Dict[str, str]:
        """
        Get tags for a bucket.

        Args:
            name: Bucket name

        Returns:
            Dictionary of tags
        """
        try:
            response = self.client.get_bucket_tagging(Bucket=name)
            return {
                tag["Key"]: tag["Value"]
                for tag in response.get("TagSet", [])
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchTagSet":
                self.logger.debug(f"Bucket {name} has no tags")
                return {}
            self.logger.warning(f"Failed to get tags for bucket {name}: {e}")
            return {}
