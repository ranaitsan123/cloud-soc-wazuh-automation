# IAM Permissions Architecture - S3, ECR & EC2 Integration

## Overview

This diagram details the IAM (Identity and Access Management) architecture that enables secure interactions between EC2 instances, S3 buckets, ECR repositories, and EC2 management operations. It shows how permissions are structured and used throughout the system.

## Diagram

```mermaid
graph TD
    subgraph IAMSetup["🔐 IAM Role & Policy Setup"]
        ROLE["aws_iam_role<br/>wazuh-ec2-role"]
        POLICY["aws_iam_policy<br/>wazuh-ec2-policy"]
        PROFILE["aws_iam_instance_profile<br/>wazuh-instance-profile"]

        ROLE -->|Assume Role| EC2_SR["Service: ec2.amazonaws.com"]
        POLICY -->|Attached to| ROLE
        ROLE -->|Used by| PROFILE
        PROFILE -->|Attached to| EC2_INST["EC2 Instances<br/>Wazuh Manager &amp; Victim VM"]
    end

    subgraph S3_PERMS["📦 S3 Permissions"]
        S3_P["s3:ListBucket<br/>s3:ListBucketVersions<br/>s3:GetObject<br/>s3:GetObjectVersion<br/>s3:PutObject<br/>s3:PutObjectVersionAcl"]

        S3_P -->|Allow on| S3_R["Resource ARNs:<br/>arn:aws:s3:::bucket<br/>arn:aws:s3:::bucket/*"]

        S3_R -->|Enables Pull| S3_GET["Pull Operations<br/>- Get docker-compose.yml<br/>- Get config files<br/>- Get audit logs<br/>- Get attack scripts"]

        S3_R -->|Enables Push| S3_PUT["Push Operations<br/>- Put audit logs<br/>- Put metrics<br/>- Put versioned configs<br/>- Put incident responses"]
    end

    subgraph ECR_PERMS["🐳 ECR Permissions"]
        ECR_P["ecr:BatchCheckLayerAvailability<br/>ecr:PutImage<br/>ecr:GetDownloadUrlForLayer<br/>ecr:BatchGetImage<br/>ecr:DescribeRepositories<br/>ecr:CreateRepository<br/>ecr:InitiateLayerUpload<br/>ecr:UploadLayerPart<br/>ecr:CompleteLayerUpload"]

        ECR_P -->|Allow on| ECR_R["Resource: *<br/>Account-scoped access"]

        ECR_R -->|Enables Pull| ECR_GET["Pull Operations<br/>- Get container images<br/>- Batch check layers<br/>- Download URLs"]

        ECR_R -->|Enables Push| ECR_PUT["Push Operations<br/>- Upload custom images<br/>- Create repo if needed<br/>- Upload layer parts"]
    end

    subgraph EC2_PERMS["🖥️ EC2 Management Permissions"]
        EC2_P["ec2:DescribeInstances<br/>ec2:StopInstances<br/>ec2:StartInstances<br/>ec2:RebootInstances<br/>ec2:DescribeNetworkInterfaces<br/>ec2:ModifyInstanceAttribute<br/>ec2:DescribeSecurityGroups<br/>ec2:AuthorizeSecurityGroupIngress<br/>ec2:RevokeSecurityGroupIngress<br/>ec2:CreateTags"]

        EC2_P -->|Allow on| EC2_R["Resource: *<br/>Full control for automation"]

        EC2_R -->|Enables| EC2_OPS["VM Management<br/>- Query instance metadata<br/>- Describe network interfaces<br/>- Modify security groups<br/>- Isolate compromised VMs<br/>- Tag instances"]
    end

    PROFILE -->|Grants| S3_PERMS
    PROFILE -->|Grants| ECR_PERMS
    PROFILE -->|Grants| EC2_PERMS

    S3_GET -->|Used by| EC2_INST
    S3_PUT -->|Used by| EC2_INST
    ECR_GET -->|Used by| EC2_INST
    ECR_PUT -->|Used by| EC2_INST
    EC2_OPS -->|Used by| EC2_INST

    subgraph DataFlow["📊 Complete Permission Flow"]
        BLOCK["Incident Detected<br/>by Wazuh Manager"]
        BLOCK -->|Trigger| RESP_SCRIPT["Active Response<br/>Python Script"]
        RESP_SCRIPT -->|Use EC2 Permissions| ISOLATE["Modify Instance<br/>Add Jail SG"]
        RESP_SCRIPT -->|Read Logs| S3_LOGS["s3:GetObject<br/>Fetch evidence"]
        RESP_SCRIPT -->|Store Logs| S3_SAVE["s3:PutObject<br/>Save incident data"]
    end

    EC2_INST -->|Executes| RESP_SCRIPT

    style IAMSetup fill:#ffcdd2
    style S3_PERMS fill:#f3e5f5
    style ECR_PERMS fill:#e0f2f1
    style EC2_PERMS fill:#fff9c4
    style DataFlow fill:#c8e6c9
```

## IAM Architecture Components

### IAM Role & Policy Setup (Red)
**Core Security Foundation**:
- **IAM Role**: `wazuh-ec2-role` - Defines the service that can assume the role
- **IAM Policy**: `wazuh-ec2-policy` - Contains specific permissions and restrictions
- **Instance Profile**: `wazuh-instance-profile` - Attaches role to EC2 instances
- **Trust Relationship**: Allows EC2 service to assume the role automatically

**Security Principle**: EC2 instances get temporary credentials through instance metadata, eliminating the need for hardcoded AWS credentials.

### S3 Permissions (Purple)
**Storage Access Control**:

**Permissions Granted**:
- `s3:ListBucket` - List objects in bucket
- `s3:ListBucketVersions` - List versioned objects
- `s3:GetObject` - Download files and configurations
- `s3:GetObjectVersion` - Access specific versions for rollback
- `s3:PutObject` - Upload logs, metrics, and incident data
- `s3:PutObjectVersionAcl` - Manage version access controls

**Resource Scope**: Limited to specific S3 bucket ARN for security

**Pull Operations**:
- Retrieve docker-compose.yml files
- Download configuration files
- Access audit logs and evidence
- Get attack simulation scripts

**Push Operations**:
- Store security audit logs
- Save performance metrics
- Upload versioned configurations
- Archive incident response data

### ECR Permissions (Cyan)
**Container Registry Access**:

**Permissions Granted**:
- `ecr:BatchCheckLayerAvailability` - Verify image layers exist
- `ecr:PutImage` - Upload container images
- `ecr:GetDownloadUrlForLayer` - Get download URLs for layers
- `ecr:BatchGetImage` - Download complete images
- `ecr:DescribeRepositories` - List and describe repositories
- `ecr:CreateRepository` - Create repositories if needed
- `ecr:InitiateLayerUpload` - Start layer upload process
- `ecr:UploadLayerPart` - Upload image layer parts
- `ecr:CompleteLayerUpload` - Finalize image uploads

**Resource Scope**: Account-wide access (`*`) for flexibility

**Pull Operations**:
- Download container images during deployment
- Batch verification of image layers
- Access to download URLs for efficient transfers

**Push Operations**:
- Upload custom-built container images
- Create repositories dynamically
- Multi-part upload of large image layers

### EC2 Management Permissions (Yellow)
**Virtual Machine Control**:

**Permissions Granted**:
- `ec2:DescribeInstances` - Query instance information
- `ec2:StopInstances` - Stop running instances
- `ec2:StartInstances` - Start stopped instances
- `ec2:RebootInstances` - Reboot instances
- `ec2:DescribeNetworkInterfaces` - Network interface information
- `ec2:ModifyInstanceAttribute` - Change instance attributes (security groups)
- `ec2:DescribeSecurityGroups` - Security group details
- `ec2:AuthorizeSecurityGroupIngress` - Add inbound rules
- `ec2:RevokeSecurityGroupIngress` - Remove inbound rules
- `ec2:CreateTags` - Add metadata tags

**Resource Scope**: Full account access (`*`) for automation

**Operations Enabled**:
- Query EC2 instance metadata
- Modify network interfaces and security groups
- Implement VM isolation during incidents
- Apply resource tagging for organization

## Complete Permission Flow Example

### Incident Response Scenario:
1. **Detection**: Wazuh Manager identifies security threat
2. **Trigger**: Active response Python script executes
3. **Authorization**: Script uses EC2 permissions to modify instance
4. **Isolation**: Compromised VM moved to "jail" security group
5. **Evidence**: Script reads incident logs using S3 permissions
6. **Archival**: Incident data saved to S3 using PutObject permission

## Security Best Practices

- **Least Privilege**: Each permission serves a specific operational need
- **Resource Restrictions**: S3 access limited to specific bucket ARNs
- **Temporary Credentials**: No long-term credentials stored on instances
- **Audit Trail**: All actions logged through CloudTrail
- **Version Control**: S3 versioning provides complete change history