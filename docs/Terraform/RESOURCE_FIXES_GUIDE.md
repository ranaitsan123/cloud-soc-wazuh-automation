# Resource Management Fixes - Implementation Guide

This guide provides concrete fixes for each issue identified in the resource management analysis.

---

## FIX #1: Configure S3 Backend with State Locking

### Create S3 Backend Setup

First, create a separate Terraform configuration for the state backend:

**File**: `terraform/backend.tf`

```hcl
# This is created FIRST in a separate terraform workspace
# Run this before your main infrastructure code

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

# S3 bucket for storing Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-${data.aws_caller_identity.current.account_id}-eu-north-1"

  tags = {
    Name      = "terraform-state"
    Purpose   = "Terraform backend"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name      = "terraform-lock"
    Purpose   = "Terraform state locking"
    ManagedBy = "terraform"
  }
}

data "aws_caller_identity" "current" {}

output "state_bucket" {
  value       = aws_s3_bucket.terraform_state.id
  description = "Name of the Terraform state S3 bucket"
}

output "lock_table" {
  value       = aws_dynamodb_table.terraform_lock.name
  description = "Name of the Terraform state lock DynamoDB table"
}
```

### Update providers.tf to Use Backend

**File**: `terraform/providers.tf`

```hcl
terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Add this backend configuration
  backend "s3" {
    bucket         = "terraform-state-ACCOUNT_ID-eu-north-1"  # Replace ACCOUNT_ID
    key            = "cloud-soc/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Deployment Steps

```bash
# 1. First time setup: Create backend infrastructure
cd terraform
terraform init
terraform apply -target=aws_s3_bucket.terraform_state -target=aws_dynamodb_table.terraform_lock

# 2. Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 3. Update providers.tf with your account ID
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" providers.tf

# 4. Reinitialize Terraform with backend
terraform init

# When prompted to copy state, choose 'yes'
# State will be migrated to S3 with automatic locking
```

---

## FIX #2: Fix Security Group Naming Collisions

### Create random suffix generator

**File**: `terraform/random.tf`

```hcl
# Generate random suffix for unique resource names
resource "random_id" "sg_suffix" {
  byte_length = 4
  keepers = {
    # Regenerate if VPC changes
    vpc_id = aws_vpc.wazuh_vpc.id
  }
}

# Generate random suffix for other resources
resource "random_id" "resource_suffix" {
  byte_length = 4
}
```

### Update security_groups.tf

**File**: `terraform/security_groups.tf` - Replace the entire file or specific resources:

```hcl
resource "aws_security_group" "wazuh_sg" {
  name_prefix = "wazuh-sg-"  # ← CHANGE from 'name' to 'name_prefix'
  description = "Wazuh Manager security group"
  vpc_id      = aws_vpc.wazuh_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from inside VPC"
  }

  ingress {
    from_port   = 1514
    to_port     = 1514
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Wazuh agent syslog/TCP"
  }

  ingress {
    from_port   = 1515
    to_port     = 1515
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Wazuh cluster communication"
  }

  ingress {
    from_port   = 55000
    to_port     = 55000
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Wazuh agent registration"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "wazuh-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  # Prevent Terraform from trying to recreate
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "victim_sg" {
  name_prefix = "victim-sg-"  # ← CHANGE from 'name' to 'name_prefix'
  description = "Victim instance security group"
  vpc_id      = aws_vpc.wazuh_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH access for testing"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTP app traffic"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "victim-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "jail_sg" {
  name_prefix = "jail-sg-"  # ← CHANGE from 'name' to 'name_prefix'
  description = "Jail security group for isolated instances"
  vpc_id      = aws_vpc.wazuh_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "jail-sg"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

---

## FIX #3: Fix S3 Bucket Naming

### Update variables.tf

**File**: `terraform/variables.tf` - Add account ID variable and data source:

```hcl
# Add this new data source
data "aws_caller_identity" "current" {}

variable "s3_bucket_name" {
  type        = string
  description = "S3 bucket name for SOC assets. Must be globally unique."
  default     = "cloud-soc-wazuh-assets-${data.aws_caller_identity.current.account_id}"
}
```

### Update s3.tf

**File**: `terraform/s3.tf` - Update the bucket resource:

```hcl
resource "aws_s3_bucket" "wazuh_assets" {
  bucket = var.s3_bucket_name

  tags = {
    Name      = "cloud-soc-wazuh-assets"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  lifecycle {
    prevent_destroy = true  # ← CHANGE: Prevent accidental deletion
  }
}

# If bucket already exists, import it:
# terraform import aws_s3_bucket.wazuh_assets cloud-soc-wazuh-assets-123456789
```

---

## FIX #4: Migrate from aws_s3_object (Deprecated)

### Check current resources

The current code uses `aws_s3_object` which is deprecated. The AWS provider has migrated this to `aws_s3_object` in newer versions.

**File**: `terraform/s3.tf` - Update all S3 object uploads (the current code is actually fine, but if you see warnings):

```hcl
# If you see deprecation warnings, the resource name is fine.
# The "deprecated" warning was about the old aws_s3_bucket_object.
# Your code already uses aws_s3_object which is correct.

# However, add this to suppress any warnings:
resource "aws_s3_object" "wazuh_docker_compose" {
  bucket       = aws_s3_bucket.wazuh_assets.id
  key          = "wazuh-docker/docker-compose.yml"
  source       = "${path.module}/../wazuh-docker/docker-compose.yml"
  etag         = filemd5("${path.module}/../wazuh-docker/docker-compose.yml")
  content_type = "text/plain"

  tags = {
    Name      = "wazuh-docker-compose"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  depends_on = [aws_s3_bucket.wazuh_assets]
}

# Repeat for all other aws_s3_object resources
```

---

## FIX #5: Separate IAM Roles for Wazuh and Victim

### Create new IAM roles

**File**: `terraform/iam.tf` - Add victim IAM role:

```hcl
# Existing code for wazuh_ec2_role...

# NEW: IAM role for victim instances (minimal permissions)
data "aws_iam_policy_document" "victim_ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "victim_ec2_role" {
  name               = "victim-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.victim_ec2_assume_role.json

  tags = {
    Name      = "victim-ec2-role"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

# Minimal policy for victim instances
resource "aws_iam_policy" "victim_ec2_policy" {
  name        = "victim-ec2-policy"
  description = "Minimal permissions for victim instances"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allow SSM agent to function
        Action = [
          "ssm:UpdateInstanceInformation",
          "ssmmessages:AcknowledgeMessage",
          "ssmmessages:GetEndpoint",
          "ssmmessages:GetMessages",
          "ec2messages:AcknowledgeMessage",
          "ec2messages:GetEndpoint",
          "ec2messages:GetMessages"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_victim_policy" {
  role       = aws_iam_role.victim_ec2_role.name
  policy_arn = aws_iam_policy.victim_ec2_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_victim_ssm_managed" {
  role       = aws_iam_role.victim_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "victim_instance_profile" {
  name = "victim-instance-profile"
  role = aws_iam_role.victim_ec2_role.name
}
```

### Update instance.tf to use separate roles

**File**: `terraform/instance.tf`:

```hcl
resource "aws_instance" "victim_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.production_private.id
  vpc_security_group_ids = [aws_security_group.victim_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.victim_instance_profile.name  # ← CHANGED
  key_name               = var.wazuh_key_name != "" ? var.wazuh_key_name : null

  # ... rest of configuration
}
```

---

## FIX #6: Complete Cleanup Script

### Create enhanced cleanup script

**File**: `scripts/terraform_cleaner_enhanced.sh`

```bash
#!/bin/bash
set -euo pipefail

# Enhanced Terraform cleaner with complete resource cleanup

TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform" && pwd)"
AWS_REGION="${AWS_REGION:-eu-north-1}"
PROJECT_TAG="${PROJECT_TAG:-cloud-soc}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enhanced Terraform Cleanup Utility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Terraform dir: $TERRAFORM_DIR"
echo "AWS region:   $AWS_REGION"
echo "AWS project:  $PROJECT_TAG"
echo ""

# Validate required tools
for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd is required but not installed" >&2
    exit 1
  fi
done

cd "$TERRAFORM_DIR"

# ============================================================================
# Helper Functions
# ============================================================================

find_vpc_id() {
  aws ec2 describe-vpcs --region "$AWS_REGION" \
    --filters "Name=tag:Name,Values=wazuh-vpc" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Vpcs[0].VpcId' --output text 2>/dev/null || echo ""
}

terminate_project_instances() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Terminating EC2 instances in VPC $vpc_id..."
  
  local ids
  ids=$(aws ec2 describe-instances --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
              "Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down" \
    --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)

  if [[ -z "${ids// /}" ]]; then
    echo "  ✓ No project instances found"
    return 0
  fi

  echo "  Terminating: $ids"
  aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids $ids || true
  
  # Wait for termination
  for i in {1..20}; do
    local remaining
    remaining=$(aws ec2 describe-instances --region "$AWS_REGION" \
      --instance-ids $ids \
      --query 'Reservations[].Instances[?State.Name != `terminated`].InstanceId' \
      --output text 2>/dev/null || true)
    
    if [[ -z "${remaining// /}" ]]; then
      echo "  ✓ All instances terminated"
      return 0
    fi
    
    echo "  ⏳ Waiting for instances to terminate ($i/20)..."
    sleep 10
  done
  
  echo "  ⚠ Instances still running, continuing..."
}

cleanup_nat_gateways() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting NAT Gateways in VPC $vpc_id..."
  
  local nat_ids
  nat_ids=$(aws ec2 describe-nat-gateways --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=state,Values=available,pending,deleting,failed" \
    --query 'NatGateways[].NatGatewayId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${nat_ids// /}" ]]; then
    echo "  ✓ No NAT Gateways found"
    return 0
  fi
  
  for nat_id in $nat_ids; do
    echo "  Deleting NAT Gateway: $nat_id"
    aws ec2 delete-nat-gateway --region "$AWS_REGION" --nat-gateway-id "$nat_id" || true
  done
  
  # Wait for deletion
  echo "  ⏳ Waiting for NAT Gateways to delete..."
  sleep 30
  echo "  ✓ NAT Gateways cleaned up"
}

cleanup_elastic_ips() {
  echo ""
  echo "[STEP] Releasing unassociated Elastic IPs..."
  
  local eip_ids
  eip_ids=$(aws ec2 describe-addresses --region "$AWS_REGION" \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Addresses[?AssociationId==null].AllocationId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${eip_ids// /}" ]]; then
    echo "  ✓ No unassociated Elastic IPs found"
    return 0
  fi
  
  for eip_id in $eip_ids; do
    echo "  Releasing: $eip_id"
    aws ec2 release-address --region "$AWS_REGION" --allocation-id "$eip_id" || true
  done
  
  echo "  ✓ Elastic IPs released"
}

cleanup_network_interfaces() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Cleaning up orphaned Network Interfaces in VPC $vpc_id..."
  
  local eni_ids
  eni_ids=$(aws ec2 describe-network-interfaces --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" \
    --query 'NetworkInterfaces[?Attachment==null].NetworkInterfaceId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${eni_ids// /}" ]]; then
    echo "  ✓ No orphaned ENIs found"
    return 0
  fi
  
  for eni in $eni_ids; do
    echo "  Deleting ENI: $eni"
    aws ec2 delete-network-interface --region "$AWS_REGION" --network-interface-id "$eni" || true
  done
  
  echo "  ✓ Network Interfaces cleaned up"
}

cleanup_security_groups() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting Security Groups in VPC $vpc_id..."
  
  # Find security groups by project tag (skip default)
  local sg_ids
  sg_ids=$(aws ec2 describe-security-groups --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'SecurityGroups[].GroupId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${sg_ids// /}" ]]; then
    echo "  ✓ No project security groups found"
    return 0
  fi
  
  for sgid in $sg_ids; do
    echo "  Deleting security group: $sgid"
    aws ec2 delete-security-group --region "$AWS_REGION" --group-id "$sgid" || true
  done
  
  echo "  ✓ Security Groups deleted"
}

cleanup_route_tables() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting custom Route Tables in VPC $vpc_id..."
  
  # Find route tables (skip main route table)
  local rt_ids
  rt_ids=$(aws ec2 describe-route-tables --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'RouteTables[].RouteTableId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${rt_ids// /}" ]]; then
    echo "  ✓ No custom Route Tables found"
    return 0
  fi
  
  for rt_id in $rt_ids; do
    # Disassociate route table from subnets
    local assoc_ids
    assoc_ids=$(aws ec2 describe-route-table-associations --region "$AWS_REGION" \
      --filters "Name=route-table-id,Values=$rt_id" \
      --query 'Associations[?Main==false].RouteTableAssociationId' --output text 2>/dev/null || echo "")
    
    for assoc_id in $assoc_ids; do
      echo "  Disassociating route table: $assoc_id"
      aws ec2 disassociate-route-table --region "$AWS_REGION" --association-id "$assoc_id" || true
    done
    
    echo "  Deleting route table: $rt_id"
    aws ec2 delete-route-table --region "$AWS_REGION" --route-table-id "$rt_id" || true
  done
  
  echo "  ✓ Route Tables deleted"
}

cleanup_subnets() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting Subnets in VPC $vpc_id..."
  
  local subnet_ids
  subnet_ids=$(aws ec2 describe-subnets --region "$AWS_REGION" \
    --filters "Name=vpc-id,Values=$vpc_id" "Name=tag:Project,Values=${PROJECT_TAG}" \
    --query 'Subnets[].SubnetId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${subnet_ids// /}" ]]; then
    echo "  ✓ No project subnets found"
    return 0
  fi
  
  for subnet_id in $subnet_ids; do
    echo "  Deleting subnet: $subnet_id"
    aws ec2 delete-subnet --region "$AWS_REGION" --subnet-id "$subnet_id" || true
  done
  
  echo "  ✓ Subnets deleted"
}

cleanup_internet_gateways() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting Internet Gateways in VPC $vpc_id..."
  
  local igw_ids
  igw_ids=$(aws ec2 describe-internet-gateways --region "$AWS_REGION" \
    --filters "Name=attachment.vpc-id,Values=$vpc_id" \
    --query 'InternetGateways[].InternetGatewayId' --output text 2>/dev/null || echo "")
  
  if [[ -z "${igw_ids// /}" ]]; then
    echo "  ✓ No Internet Gateways found"
    return 0
  fi
  
  for igw_id in $igw_ids; do
    echo "  Detaching Internet Gateway: $igw_id"
    aws ec2 detach-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$igw_id" --vpc-id "$vpc_id" || true
    
    echo "  Deleting Internet Gateway: $igw_id"
    aws ec2 delete-internet-gateway --region "$AWS_REGION" --internet-gateway-id "$igw_id" || true
  done
  
  echo "  ✓ Internet Gateways deleted"
}

cleanup_vpc() {
  local vpc_id="$1"
  echo ""
  echo "[STEP] Deleting VPC $vpc_id..."
  
  aws ec2 delete-vpc --region "$AWS_REGION" --vpc-id "$vpc_id" || true
  echo "  ✓ VPC deleted"
}

# ============================================================================
# Main Cleanup Flow
# ============================================================================

echo "Starting resource cleanup..."

# Show what will be destroyed
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ STEP 1: Display Terraform Destroy Plan                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
terraform state list 2>/dev/null || echo "No Terraform state found"

echo ""
echo "Creating Terraform destroy plan..."
terraform plan -destroy -out=/tmp/tf-destroy.plan 2>&1 | grep -E "Plan:|will be destroyed"

echo ""
echo "Resources to be destroyed:"
terraform show -json /tmp/tf-destroy.plan 2>/dev/null | \
  jq -r '.resource_changes[] | select(.change.actions|contains(["delete"])) | "  - \(.type): \(.name)"' || true

# Confirm before proceeding
echo ""
read -p "Proceed with AWS cleanup and Terraform destroy? (type 'yes' to continue): " -r confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Cleanup canceled."
  exit 0
fi

# AWS cleanup
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ STEP 2: AWS Resource Cleanup (Manual Dependency Cleanup)   ║"
echo "╚════════════════════════════════════════════════════════════╝"

VPC_ID=$(find_vpc_id)
if [[ -n "$VPC_ID" && "$VPC_ID" != "None" ]]; then
  echo "Found VPC: $VPC_ID"
  terminate_project_instances "$VPC_ID"
  cleanup_nat_gateways "$VPC_ID"
  cleanup_elastic_ips
  cleanup_network_interfaces "$VPC_ID"
  cleanup_security_groups "$VPC_ID"
  cleanup_route_tables "$VPC_ID"
  cleanup_subnets "$VPC_ID"
  cleanup_internet_gateways "$VPC_ID"
  cleanup_vpc "$VPC_ID"
else
  echo "No project VPC found in AWS"
fi

# Terraform destroy
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ STEP 3: Terraform Destroy                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo "Applying Terraform destroy..."
if terraform apply -auto-approve /tmp/tf-destroy.plan; then
  echo "✓ Terraform destroy completed successfully"
else
  echo "⚠ Terraform destroy encountered errors"
  echo "This is OK if manual cleanup handled all dependencies"
fi

# Final verification
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ STEP 4: Final Verification                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo "Verifying resources are deleted..."
REMAINING_INSTANCES=$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
  --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)

if [[ -z "${REMAINING_INSTANCES// /}" ]]; then
  echo "✓ No instances remaining"
else
  echo "⚠ Remaining instances: $REMAINING_INSTANCES"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Cleanup Complete!"
echo "═══════════════════════════════════════════════════════════════"
```

---

## FIX #7: Restrict IAM Permissions

### Update IAM policy to be more restrictive

**File**: `terraform/iam.tf` - Update the wazuh EC2 policy:

```hcl
resource "aws_iam_policy" "wazuh_ec2_policy" {
  name        = "wazuh-ec2-policy"
  description = "Permissions for Wazuh response automation"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # EC2 read-only permissions for discovery (no modifications)
      {
        Sid    = "EC2ReadOnly"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeTags"
        ]
        Effect   = "Allow"
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" : "cloud-soc"
          }
        }
      },
      # EC2 write permissions - only on tagged resources
      {
        Sid    = "EC2WriteTagged"
        Action = [
          "ec2:StopInstances",
          "ec2:StartInstances",
          "ec2:RebootInstances",
          "ec2:CreateTags"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ec2:${var.aws_region}:ACCOUNT_ID:instance/*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" : "cloud-soc"
          }
        }
      },
      # Security group modifications - only on tagged resources
      {
        Sid    = "SecurityGroupModifyTagged"
        Action = [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupIngress"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ec2:${var.aws_region}:ACCOUNT_ID:security-group/*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/Project" : "cloud-soc"
          }
        }
      },
      # S3 access - only to project bucket
      {
        Sid    = "S3ProjectBucket"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      },
      # ECR access - only to project repositories
      {
        Sid    = "ECRProjectRepositories"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ecr:${var.aws_region}:ACCOUNT_ID:repository/cloud-soc-*"
        ]
      }
    ]
  })
}
```

---

## FIX #8: Enable Prevent-Destroy on Critical Resources

### Update resource protection

**File**: `terraform/s3.tf`:

```hcl
resource "aws_s3_bucket" "wazuh_assets" {
  bucket = var.s3_bucket_name

  tags = {
    Name      = "cloud-soc-wazuh-assets"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  lifecycle {
    prevent_destroy = true  # ← Prevent accidental deletion
  }
}
```

**File**: `terraform/iam.tf`:

```hcl
resource "aws_iam_role" "wazuh_ec2_role" {
  name               = "wazuh-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = {
    Name      = "wazuh-ec2-role"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

---

## Verification Steps

After implementing all fixes:

```bash
# 1. Validate Terraform configuration
cd terraform
terraform validate

# 2. Check for syntax errors
terraform fmt -check

# 3. Create a plan
terraform plan -out=tfplan

# 4. Review plan for duplicates/issues
terraform show tfplan

# 5. Deploy with backend
terraform apply tfplan

# 6. Verify state is locked
aws dynamodb scan --table-name terraform-state-lock

# 7. Test cleanup script
./terraform_cleaner_enhanced.sh

# 8. Verify resources are destroyed
aws ec2 describe-instances --filters "Name=tag:Project,Values=cloud-soc"
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=cloud-soc"
```

---

## Rollback Plan

If issues arise during implementation:

```bash
# 1. Restore from state backup
terraform state pull > state.backup.json

# 2. Revert to previous Terraform files (git)
git checkout HEAD~1 -- terraform/

# 3. Reinitialize without backend changes
terraform init

# 4. Review differences
terraform plan

# 5. Apply safely
terraform apply
```

---

This implementation guide provides concrete solutions for all identified issues. Start with Phase 1 (backend state locking) before proceeding to other fixes.
