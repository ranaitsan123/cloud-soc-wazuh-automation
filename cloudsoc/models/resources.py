"""Pydantic models for AWS resources and system state"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VPC(BaseModel):
    """Virtual Private Cloud model"""
    id: str = Field(..., description="VPC ID")
    cidr_block: str = Field(..., description="CIDR block")
    name: str = Field(default="", description="VPC name from tags")
    project: str = Field(default="", description="Project tag")
    state: str = Field(default="available", description="VPC state")
    tags: Dict[str, str] = Field(default_factory=dict, description="VPC tags")

    class Config:
        """Pydantic config"""
        extra = "allow"


class Subnet(BaseModel):
    """Subnet model"""
    id: str = Field(..., description="Subnet ID")
    vpc_id: str = Field(..., description="Parent VPC ID")
    cidr_block: str = Field(..., description="CIDR block")
    name: str = Field(default="", description="Subnet name")
    availability_zone: str = Field(default="", description="Availability zone")
    state: str = Field(default="available", description="Subnet state")

    class Config:
        """Pydantic config"""
        extra = "allow"


class SecurityGroup(BaseModel):
    """Security Group model"""
    id: str = Field(..., description="Security Group ID")
    vpc_id: str = Field(..., description="Parent VPC ID")
    name: str = Field(..., description="Group name")
    description: str = Field(default="", description="Group description")
    state: str = Field(default="available", description="Group state")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags")

    class Config:
        """Pydantic config"""
        extra = "allow"


class EC2Instance(BaseModel):
    """EC2 Instance model"""
    id: str = Field(..., description="Instance ID")
    type: str = Field(..., description="Instance type")
    state: str = Field(..., description="Instance state")
    vpc_id: Optional[str] = Field(default=None, description="Parent VPC ID")
    subnet_id: Optional[str] = Field(default=None, description="Subnet ID")
    private_ip: Optional[str] = Field(default=None, description="Private IP")
    public_ip: Optional[str] = Field(default=None, description="Public IP")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags")

    class Config:
        """Pydantic config"""
        extra = "allow"


class NetworkInterface(BaseModel):
    """Network Interface model"""
    id: str = Field(..., description="ENI ID")
    vpc_id: str = Field(..., description="Parent VPC ID")
    subnet_id: str = Field(..., description="Subnet ID")
    status: str = Field(default="available", description="ENI status")
    instance_id: Optional[str] = Field(default=None, description="Attached instance ID")
    private_ips: List[str] = Field(default_factory=list, description="Private IPs")

    class Config:
        """Pydantic config"""
        extra = "allow"


class IAMRole(BaseModel):
    """IAM Role model"""
    name: str = Field(..., description="Role name")
    arn: str = Field(..., description="Role ARN")
    create_date: str = Field(..., description="Creation date")
    trust_policy: Dict[str, Any] = Field(default_factory=dict, description="Trust policy")

    class Config:
        """Pydantic config"""
        extra = "allow"


class S3Bucket(BaseModel):
    """S3 Bucket model"""
    name: str = Field(..., description="Bucket name")
    creation_date: str = Field(..., description="Creation date")
    region: str = Field(default="", description="Region")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags")

    class Config:
        """Pydantic config"""
        extra = "allow"


class OperationResult(BaseModel):
    """Result of an operation"""
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(default="", description="Operation message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    errors: List[str] = Field(default_factory=list, description="Error messages")

    class Config:
        """Pydantic config"""
        extra = "allow"
