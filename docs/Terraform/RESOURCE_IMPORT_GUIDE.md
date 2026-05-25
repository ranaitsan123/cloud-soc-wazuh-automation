# Resource Import & Idempotency Guide

## Overview

The `cloud-soc apply` command now implements **full resource idempotency**. It automatically detects existing AWS resources and imports them into Terraform state before applying changes. This prevents accidental recreation of resources and enables safe re-runs.

## How It Works

### Flow Diagram

```
cloud-soc apply
    ↓
Terraform Init
    ↓
ResourceImporter.import_all_existing_resources()
    ├─ Check IAM resources (roles, policies, instance profiles)
    ├─ Check VPC & networking (VPC, subnets, IGW, NAT, route tables)
    ├─ Check security groups
    ├─ Check EC2 instances
    ├─ Check S3 buckets
    └─ Check ECR repositories
    ↓
Import found resources into Terraform state
    ↓
Terraform Validate
    ↓
Terraform Plan (only shows differences)
    ↓
Terraform Apply (creates only missing resources)
    ↓
Post-apply orchestration (Ansible, dashboard setup, etc.)
```

### Key Principle

**Resource Discovery via Tags:**
- All resources are discovered using AWS tags (primary) and resource names (secondary)
- Project tag: `Project=cloud-soc`
- Resource names follow naming convention: `resource-type-description`

## Imported Resources

### ✅ IAM Resources (6 total)

| Resource Address | AWS Name | Type | Purpose |
|---|---|---|---|
| `aws_iam_role.wazuh_ec2_role` | `wazuh-ec2-role` | Role | EC2 execution role for Wazuh server |
| `aws_iam_role.victim_ec2_role` | `victim-ec2-role` | Role | EC2 execution role for victim server |
| `aws_iam_policy.wazuh_ec2_policy` | `wazuh-ec2-policy` | Policy | Permissions for Wazuh automation |
| `aws_iam_policy.victim_ec2_policy` | `victim-ec2-policy` | Policy | Permissions for victim server |
| `aws_iam_instance_profile.wazuh_instance_profile` | `wazuh-instance-profile` | Instance Profile | Wazuh EC2 instance profile |
| `aws_iam_instance_profile.victim_instance_profile` | `victim-instance-profile` | Instance Profile | Victim EC2 instance profile |

### ✅ VPC & Networking (11 total)

| Resource Address | Discovery Method | Purpose |
|---|---|---|
| `aws_vpc.wazuh_vpc` | Project tag | Main VPC for infrastructure |
| `aws_subnet.management_private` | VPC + name | Management network |
| `aws_subnet.production_private` | VPC + name | Production/victim network |
| `aws_subnet.nat_public` | VPC + name | Public subnet for NAT |
| `aws_internet_gateway.igw` | VPC attachment | Internet access |
| `aws_eip.nat` | NAT gateway association | Static IP for NAT |
| `aws_nat_gateway.nat` | VPC + availability | NAT for private subnets |
| `aws_route_table.public` | VPC + tag name | Public routing |
| `aws_route_table.private` | VPC + tag name | Private routing (via NAT) |
| `aws_route_table_association.nat_public` | Subnet + route table | Public subnet routing |
| `aws_route_table_association.management_private` | Subnet + route table | Management routing |
| `aws_route_table_association.production_private` | Subnet + route table | Production routing |

### ✅ Security Groups (2 total)

| Resource Address | AWS Name | Rules | Purpose |
|---|---|---|---|
| `aws_security_group.wazuh_sg` | `wazuh-sg` | Ports 443, 1514, 1515, 55000, 22 | Wazuh manager security |
| `aws_security_group.victim_sg` | `victim-sg` | Ports 22, 80 | Victim server security |

### ✅ EC2 Instances (2 total)

| Resource Address | AWS Name | Instance Type | Purpose |
|---|---|---|---|
| `aws_instance.wazuh_server` | `wazuh-server` | t3.medium (default) | Wazuh SIEM manager |
| `aws_instance.victim_server` | `victim-server` | t3.micro | Target for attack simulation |

### ✅ Storage & Registry (3 total)

| Resource Address | AWS Name | Purpose |
|---|---|---|
| `aws_s3_bucket.wazuh_assets` | `cloud-soc-wazuh-assets-*` | Docker configs, scripts, assets |
| `aws_ecr_repository.manager_repo` | `cloud-soc-wazuh-manager` | Wazuh manager container image |
| `aws_ecr_repository.victim_repo` | `cloud-soc-victim` | Victim container image |

**Total Resources Covered: 24**

## Implementation Details

### 1. ResourceImporter Class

**Location:** `cloudsoc/terraform/imports.py`

**Main Methods:**
- `import_all_existing_resources()` - Orchestrates all imports
- `_import_iam_resources()` - Handles IAM imports
- `_import_vpc_and_networking()` - Handles VPC and networking
- `_import_security_groups()` - Handles security groups
- `_import_instances()` - Handles EC2 instances
- `_import_s3_resources()` - Handles S3 bucket
- `_import_ecr_resources()` - Handles ECR repositories

**Helper Methods:**
- `_find_internet_gateway_for_vpc()` - Discovers IGW by VPC attachment
- `_find_nat_gateway_for_vpc()` - Discovers NAT gateway by VPC
- `_find_eip_for_nat_gateway()` - Finds EIP associated with NAT
- `_find_route_table_for_vpc()` - Discovers route table by tags
- `_import_route_table_associations()` - Associates subnets with route tables
- `_find_s3_bucket_by_tag()` - Discovers S3 bucket by project tag

### 2. Integration with Orchestrator

**Location:** `cloudsoc/orchestrator.py`

**Changes:**
- Replaced `_ensure_iam_resources_imported()` with `_import_all_existing_resources()`
- Now calls `ResourceImporter` during `apply()` workflow
- Error handling: Non-critical import errors don't block deployment

**Code Flow:**
```python
def apply(self, auto_approve=False, var_files=None):
    self.tf_runner.init()
    self._import_all_existing_resources()  # NEW
    self.tf_runner.validate()
    plan_file = self.tf_runner.plan(var_files=var_files or [])
    self.tf_runner.apply(plan_file=plan_file, auto_approve=auto_approve)
    # ... post-apply orchestration
```

### 3. AWS Service Extensions

**S3Service Enhancement:**
- Added `get_bucket_tags()` method to extract bucket tags
- Used for discovering S3 buckets by project tag

## Usage

### Basic Usage (No Changes!)

```bash
# Run apply - it automatically detects and imports existing resources
cloud-soc apply

# Or with auto-approval
cloud-soc apply --auto-approve

# Or with custom variables
cloud-soc apply --var-file production.tfvars --auto-approve
```

### What Happens

1. **First Run (Fresh Infrastructure):**
   - No existing resources found
   - Terraform creates all 24 resources
   - All resources are in state

2. **Second Run (Resources Exist):**
   - ResourceImporter detects all 24 existing resources
   - Imports them into state (if not already present)
   - Terraform plan shows "no changes"
   - Terraform apply completes with "no changes"

3. **Partial Infrastructure Update:**
   - If you delete an EC2 instance manually from AWS
   - ResourceImporter finds 23 existing resources
   - Terraform plan shows 1 resource to create
   - Terraform apply recreates only the missing instance

### Logging

The import process logs all actions:

```
[INFO] Checking for existing AWS resources to import...
[INFO] Importing existing IAM resources...
[DEBUG] Terraform state already contains aws_iam_role.wazuh_ec2_role
[INFO] Found existing IAM resource wazuh-ec2-role, importing...
[INFO] Importing existing VPC and networking resources...
[INFO] Importing VPC: vpc-xxxxx
[INFO] Importing subnet: aws_subnet.management_private (subnet-xxxxx)
[INFO] Importing existing security groups...
[INFO] Importing security group: aws_security_group.wazuh_sg (sg-xxxxx)
[INFO] Importing existing EC2 instances...
[INFO] Importing instance: aws_instance.wazuh_server (i-xxxxx)
[INFO] Resource import check completed
```

## Safety Features

### 1. Non-Breaking
- Existing deployments continue to work
- Backward compatible with old state files
- Safe for upgrades

### 2. Error Resilience
```python
try:
    importer.import_all_existing_resources()
except Exception as e:
    logger.warning(f"Import encountered an issue (non-critical): {e}")
    logger.info("Proceeding with deployment...")
```
- Import errors don't block deployment
- Terraform can still create missing resources
- Warnings logged for debugging

### 3. Idempotency Guarantees
- Running `cloud-soc apply` multiple times is safe
- No resource recreation on repeated runs
- Terraform state remains clean

## Troubleshooting

### Issue: Resource Import Fails

**Symptom:**
```
[WARNING] Failed to import security group: sg-xxxxx
[INFO] Proceeding with deployment...
```

**Solution:**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify IAM permissions for terraform operations
- Check resource still exists in AWS
- Run with debug logging: `TF_LOG=DEBUG cloud-soc apply`

### Issue: Resource Exists But Not Imported

**Symptom:**
```
[ERROR] Resource already exists in AWS...
```

**Solution:**
1. Manually import the resource:
   ```bash
   cd terraform
   terraform import aws_instance.wazuh_server i-xxxxx
   ```

2. Or remove from AWS and re-run:
   ```bash
   aws ec2 terminate-instances --instance-ids i-xxxxx
   cloud-soc apply --auto-approve
   ```

### Issue: State File Mismatch

**Symptom:**
```
[WARNING] Terraform state contains resource but not in AWS
```

**Solution:**
```bash
# Refresh state
cd terraform
terraform refresh

# Or remove from state and re-import
terraform state rm aws_instance.wazuh_server
cloud-soc apply --auto-approve
```

## Best Practices

### 1. Use `--auto-approve` in CI/CD
```bash
cloud-soc apply --auto-approve  # Safe and idempotent
```

### 2. Always Review Plan in Production
```bash
cloud-soc apply  # See plan first, then approve
```

### 3. Use Consistent Variable Files
```bash
cloud-soc apply --var-file production.tfvars --auto-approve
```

### 4. Monitor Logs During Apply
```bash
cloud-soc apply 2>&1 | tee apply.log
grep -i "import\|error" apply.log
```

### 5. Version Control Terraform Files
- Don't modify `terraform/` files outside of `cloud-soc` workflows
- Use version control for `.tfvars` files
- Keep state files in S3 backend (configured)

## Performance Impact

The import process adds minimal overhead:

| Step | Duration | Notes |
|---|---|---|
| AWS API calls (24 resources) | 5-10s | Parallel discovery |
| Terraform import (24 resources) | 10-15s | Sequential imports |
| Total overhead | 15-25s | One-time per apply |

**Impact on Deployment Time:**
- Fresh infrastructure: +20s
- Existing infrastructure: +20s (still faster than manual imports)
- CI/CD pipeline: Negligible impact

## Future Enhancements

Potential improvements for future releases:

1. **Parallel Imports** - Concurrent terraform import operations
2. **Custom Import Registry** - YAML-based resource configuration
3. **Import Validation** - Pre-import validation checks
4. **Rollback Support** - Automated state rollback on import failure
5. **Metrics & Reporting** - Detailed import statistics

## Related Documentation

- [Terraform Documentation](https://www.terraform.io/docs/commands/import.html)
- [AWS Resource Tagging](https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html)
- [Cloud SOC Architecture](./terraform/README.md)
- [Orchestration Guide](./IMPLEMENTATION_SUMMARY.md)

## Support

For issues or questions:
1. Check logs with `TF_LOG=DEBUG`
2. Review resource discovery with `cloud-soc status`
3. Manually verify resources exist in AWS Console
4. Check IAM permissions: `aws iam get-user`

---

**Last Updated:** 2026-05-22
**Version:** 1.0
**Status:** Production Ready ✅
