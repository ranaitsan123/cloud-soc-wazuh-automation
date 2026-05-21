# AWS Resource Management Issues - Analysis Report

## Executive Summary
Your Cloud SOC project has several critical issues that can lead to **resource duplication**, **failed destruction**, and **mismatched resources** in AWS. This document outlines each issue with severity levels and recommended fixes.

---

## 🔴 CRITICAL ISSUES

### 1. **Resource Name Collisions - Security Groups**
**File**: [terraform/security_groups.tf](terraform/security_groups.tf)  
**Problem**: Security groups use hardcoded names without uniqueness constraints.

```hcl
resource "aws_security_group" "wazuh_sg" {
  name        = "wazuh-sg"        # ← HARDCODED, NOT UNIQUE
  ...
}

resource "aws_security_group" "victim_sg" {
  name        = "victim-sg"       # ← HARDCODED, NOT UNIQUE
  ...
}
```

**Impact**: 
- If you run terraform multiple times, it tries to create SGs with the same name in the same VPC
- AWS will either fail with "name already exists" OR use existing SG (silent mismatch)
- Terraform destroy may fail because the SG is not managed by the current state

**Fix**: Use unique names with timestamps or random suffixes:
```hcl
resource "aws_security_group" "wazuh_sg" {
  name        = "wazuh-sg-${random_id.sg_suffix.hex}"
  # OR
  name_prefix = "wazuh-sg-"
}
```

---

### 2. **S3 Bucket Name Collision**
**File**: [terraform/s3.tf](terraform/s3.tf)  
**Problem**: S3 bucket names are globally unique across AWS. Hardcoded defaults cause failures on retry.

```hcl
variable "s3_bucket_name" {
  default     = "cloud-soc-wazuh-assets"  # ← GLOBALLY UNIQUE, MAY ALREADY EXIST
}
```

**Impact**:
- First run: Creates bucket successfully
- Second run: Fails with `BucketAlreadyOwnedByYou` or `BucketAlreadyExists`
- Cannot redeploy without changing the bucket name
- If bucket still exists from failed cleanup, new deployment cannot use the same name

**Fix**: Use a project-specific unique identifier:
```hcl
variable "s3_bucket_name" {
  default = "cloud-soc-wazuh-assets-${data.aws_caller_identity.current.account_id}"
}
```

---

### 3. **Deprecated S3 Resource Type**
**File**: [terraform/s3.tf](terraform/s3.tf)  
**Problem**: Uses deprecated `aws_s3_object` resource type.

```hcl
resource "aws_s3_object" "wazuh_docker_compose" {  # ← DEPRECATED
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/docker-compose.yml"
  source = "${path.module}/../wazuh-docker/docker-compose.yml"
}
```

**Impact**:
- Terraform 5.x will remove support for `aws_s3_object`
- May cause unexpected state mismatches
- Community support diminished

**Fix**: Migrate to `aws_s3_object` using the correct reference, or use `aws_s3`:
```hcl
resource "aws_s3_object" "wazuh_docker_compose" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/docker-compose.yml"
  source = "${path.module}/../wazuh-docker/docker-compose.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/docker-compose.yml")
}
```

---

### 4. **No Terraform State Locking**
**File**: [terraform/providers.tf](terraform/providers.tf)  
**Problem**: No remote state backend configured. State stored locally only.

```hcl
# No backend configuration - state is local only!
provider "aws" {
  region = var.aws_region
}
```

**Impact**:
- If two developers/CI jobs run `terraform apply` simultaneously, both will create resources
- Resource duplication and state corruption
- No audit trail of state changes
- Cannot safely collaborate on infrastructure

**Fix**: Configure remote backend with state locking:
```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "cloud-soc/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

---

### 5. **EC2 Instances Share Single IAM Role**
**File**: [terraform/instance.tf](terraform/instance.tf)  
**Problem**: Both Wazuh server and victim server use the same IAM instance profile.

```hcl
resource "aws_instance" "wazuh_server" {
  iam_instance_profile = aws_iam_instance_profile.wazuh_instance_profile.name
}

resource "aws_instance" "victim_server" {
  iam_instance_profile = aws_iam_instance_profile.wazuh_instance_profile.name  # ← SAME ROLE
}
```

**Impact**:
- Victim instances have unnecessary EC2/S3/ECR permissions
- Security violation (principle of least privilege)
- If victim is compromised, attacker gains broad AWS access
- Makes cleanup more complex

**Fix**: Create separate IAM roles:
```hcl
resource "aws_iam_instance_profile" "victim_instance_profile" {
  name = "victim-instance-profile"
  role = aws_iam_role.victim_ec2_role.name
}
```

---

## 🟠 HIGH PRIORITY ISSUES

### 6. **Cleanup Script May Miss Dependent Resources**
**File**: [scripts/terraform_cleaner.sh](scripts/terraform_cleaner.sh)  
**Problem**: Manual cleanup of AWS resources but doesn't cover all resource types.

```bash
# Cleans: instances, ENIs, security groups
# Misses: NAT gateways, Elastic IPs, route tables, subnets, VPC
cleanup_orphaned_aws_resources() {
  ...
  terminate_project_instances "$vpc_id"
  cleanup_network_interfaces "$vpc_id"
  cleanup_security_groups "$vpc_id"
  # ← Missing NAT, EIP, route tables cleanup
}
```

**Impact**:
- `terraform destroy` fails due to dependency issues
- Resources remain in AWS after failed cleanup
- Re-running terraform apply creates new resources instead of reusing old ones
- Increased AWS costs

**Fix**: Add missing cleanup steps:
```bash
cleanup_nat_gateways() {
  # Delete NAT gateways first
  # Then delete Elastic IPs
  # Then delete route tables
}
```

---

### 7. **No Terraform Plan Review Before Destroy**
**File**: [scripts/terraform_cleaner.sh](scripts/terraform_cleaner.sh)  
**Problem**: Creates destroy plan but minimal resource preview.

```bash
echo "Destroy plan resources (preview):"
cat /tmp/tf-destroy-resources.txt  # ← Only shows resource addresses, not details
```

**Impact**:
- User may approve destruction without understanding what will be deleted
- Insufficient validation before destroying infrastructure

**Fix**: Improve plan review:
```bash
# Show more detailed plan output
terraform show -json /tmp/tf-destroy.plan | jq '.resource_changes[] | 
  "\(.type).\(.name): \(.change.before) -> \(.change.after)"'
```

---

### 8. **Resource Destruction Dependency Ordering**
**File**: [terraform/network.tf](terraform/network.tf)  
**Problem**: Multiple resources with implicit dependencies but no explicit cleanup order.

**Impact**:
- VPC cannot be deleted while subnets exist
- Subnets cannot be deleted while instances exist
- ENIs cannot be deleted while attached
- Cleanup order matters, but script doesn't enforce it

**Fix**: Add explicit `depends_on` in reverse order for cleanup.

---

### 9. **Python EC2 Service Missing Resource Tracking**
**File**: [cloudsoc/aws/ec2.py](cloudsoc/aws/ec2.py)  
**Problem**: `find_instances()` only searches by `project_tag`, but doesn't track which resources are "managed".

```python
def find_instances(
    self,
    vpc_id: Optional[str] = None,
    project_tag: Optional[str] = None,  # ← Only filter by tag
    states: Optional[List[str]] = None
) -> List[EC2Instance]:
```

**Impact**:
- If an instance loses its `Project` tag, it won't be found for cleanup
- Orphaned resources accumulate
- No way to detect mismatched resources

**Fix**: Add resource tracking/state file:
```python
class ResourceRegistry:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.resources = self._load_state()
    
    def is_managed(self, resource_id: str) -> bool:
        return resource_id in self.resources
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 10. **IAM Policy Too Permissive**
**File**: [terraform/iam.tf](terraform/iam.tf)  
**Problem**: EC2 instances can modify any security group and any EC2 resource.

```hcl
{
  "Action": [
    "ec2:DescribeInstances",
    "ec2:StopInstances",
    "ec2:StartInstances",
    ...
    "ec2:AuthorizeSecurityGroupIngress",
    "ec2:RevokeSecurityGroupIngress",
    "ec2:CreateTags"
  ],
  "Effect": "Allow",
  "Resource": "*"  # ← TOO PERMISSIVE
}
```

**Impact**:
- If EC2 instance is compromised, attacker has broad AWS access
- Can modify security groups to open ports
- Can launch additional instances
- Can access any S3 bucket

**Fix**: Restrict resource ARNs:
```json
{
  "Action": "ec2:DescribeInstances",
  "Resource": "*",  # ← OK for read-only
  "Condition": {
    "StringEquals": {
      "ec2:ResourceTag/Project": "cloud-soc"
    }
  }
}
```

---

### 11. **No Prevent-Destroy Lifecycle Rule**
**File**: [terraform/s3.tf](terraform/s3.tf)  
**Problem**: Accidental `terraform destroy` could delete critical S3 bucket.

```hcl
resource "aws_s3_bucket" "wazuh_assets" {
  lifecycle {
    prevent_destroy = false  # ← Allows deletion!
  }
}
```

**Impact**:
- Single typo or mistake deletes production assets
- Permanent data loss

**Fix**: 
```hcl
lifecycle {
  prevent_destroy = true
}
```

---

### 12. **Resource Metadata Missing for Orphan Detection**
**File**: [terraform/variables.tf](terraform/variables.tf)  
**Problem**: No resource registry or manifest to track what should exist.

**Impact**:
- Can't detect orphaned resources (resources in AWS but not in Terraform)
- Can't detect rogue resources
- Manual reconciliation required

**Fix**: Create resource manifest:
```json
{
  "managed_resources": [
    "aws_vpc.wazuh_vpc",
    "aws_instance.wazuh_server",
    "aws_instance.victim_server"
  ]
}
```

---

## 📋 RESOURCE DUPLICATION SCENARIOS

### Scenario A: Running `terraform apply` twice
1. First run: All resources created successfully
2. Second run with modified bucket name:
   - **Result**: New S3 bucket created, old one orphaned
   - **Cost**: Double charging for storage

### Scenario B: Failed `terraform destroy`
1. `terraform destroy` fails due to dependent resources
2. Manual AWS cleanup incomplete
3. Running `terraform apply` again:
   - **Result**: Some resources already exist in AWS but not in state
   - **Behavior**: Terraform creates duplicates or fails with "already exists"

### Scenario C: Concurrent deployments
1. Two developers run `terraform apply` simultaneously
2. No state locking configured
3. **Result**: Both create all resources, doubling infrastructure
4. **Outcome**: State corruption, inconsistent resource configuration

---

## ✅ RECOMMENDED FIXES (Priority Order)

### Phase 1: Critical (Do First)
1. **Configure S3 Backend with State Locking** - Prevents concurrent deployments
2. **Fix Security Group Naming** - Use `name_prefix` instead of `name`
3. **Fix S3 Bucket Naming** - Add account ID or unique suffix
4. **Add Terraform Destroy Validation** - Review plan before destroying

### Phase 2: High Priority (Do Soon)
5. **Complete Cleanup Script** - Add NAT, EIP, route tables
6. **Separate IAM Roles** - Victim and Wazuh servers get different permissions
7. **Add Resource Registry** - Track managed resources
8. **Enable Prevent-Destroy** - Protect critical S3 bucket

### Phase 3: Medium Priority (Polish)
9. **Restrict IAM Permissions** - Use resource tags in policies
10. **Add Resource Tagging Strategy** - Consistent tagging for tracking
11. **Migrate from aws_s3_object** - Use modern Terraform providers
12. **Add Terraform State Backup** - Automated state backups

---

## Testing the Issues

### Check for resource duplication:
```bash
# List all resources managed by Terraform
terraform state list

# Compare with AWS actual resources
aws ec2 describe-security-groups --filters "Name=tag:Project,Values=cloud-soc"
aws ec2 describe-instances --filters "Name=tag:Project,Values=cloud-soc"
aws s3api list-buckets --query "Buckets[?contains(Name, 'cloud-soc')]"
```

### Check state consistency:
```bash
# Import orphaned resources
terraform import aws_security_group.wazuh_sg sg-xxxxx

# Or remove from state if incorrect
terraform state rm aws_instance.victim_server
```

---

## Summary Table

| Issue | Severity | Type | Impact |
|-------|----------|------|--------|
| SG name collisions | 🔴 Critical | Duplication | Resources fail to create or mismatch |
| S3 bucket naming | 🔴 Critical | Duplication | Deployment fails on retry |
| No state locking | 🔴 Critical | Concurrency | Resource duplication in team environments |
| Deprecated S3 resources | 🔴 Critical | Compatibility | Future Terraform incompatibility |
| Incomplete cleanup | 🟠 High | Destruction | Resources left behind after destroy |
| Shared IAM role | 🟠 High | Security | Overprivileged victim instances |
| Missing resource tracking | 🟠 High | Management | Orphaned resources undetected |
| Permissive IAM policy | 🟡 Medium | Security | Broad instance permissions |
| No prevent-destroy | 🟡 Medium | Safety | Accidental data deletion |

---

## Next Steps

1. **Read the detailed fix guide** (if provided)
2. **Start with Phase 1 fixes** to stabilize your infrastructure
3. **Add CI/CD validation** to catch these issues automatically
4. **Document your resource naming strategy** for team consistency
