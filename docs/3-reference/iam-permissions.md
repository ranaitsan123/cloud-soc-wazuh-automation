# IAM Permissions Architecture

## Overview

This document explains the IAM permissions used by the Cloud SOC deployment, including S3, ECR, and EC2 integration.

## Architecture

The system uses an IAM role attached to EC2 instances to authorize secure access without hardcoded credentials.

### Core components

- **IAM Role**: `wazuh-ec2-role`
- **IAM Policy**: `wazuh-ec2-policy`
- **Instance Profile**: `wazuh-instance-profile`

## Permissions

### S3

The EC2 instances are granted permissions such as:

- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:PutObjectVersionAcl`

These permissions are scoped to the project S3 bucket and allow secure asset retrieval and log storage.

### ECR

ECR permissions include:

- `ecr:BatchCheckLayerAvailability`
- `ecr:PutImage`
- `ecr:GetDownloadUrlForLayer`
- `ecr:CreateRepository`

These permissions support image pulls and pushes for container deployment.

### EC2

EC2 management permissions include:

- `ec2:DescribeInstances`
- `ec2:StopInstances`
- `ec2:StartInstances`
- `ec2:ModifyInstanceAttribute`
- `ec2:AuthorizeSecurityGroupIngress`

These permissions enable secure runtime automation and incident response actions.

## Data flow

The IAM role grants the EC2 instances the ability to:

- read and write deployment artifacts in S3
- manage container images in ECR
- query and modify EC2 resources for automation

## Security notes

- Use least privilege whenever possible.
- Keep resource scopes limited to project-specific resources.
- Rely on instance metadata for temporary credentials.
- Audit actions through CloudTrail and logging.
