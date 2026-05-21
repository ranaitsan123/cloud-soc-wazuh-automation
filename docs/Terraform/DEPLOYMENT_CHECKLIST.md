# Resource Management - Quick Reference & Checklist

## 🎯 Quick Issue Summary

| Issue | Risk | Current | Should Be |
|-------|------|---------|-----------|
| SG names | 🔴 CRITICAL | Hardcoded `name` | Use `name_prefix` |
| S3 bucket | 🔴 CRITICAL | `cloud-soc-wazuh-assets` | `cloud-soc-wazuh-assets-{ACCOUNT_ID}` |
| State lock | 🔴 CRITICAL | Local state only | S3 + DynamoDB |
| IAM role sharing | 🟠 HIGH | Both instances use same | Separate roles |
| Cleanup script | 🟠 HIGH | Incomplete | Enhanced version available |
| S3 encryption | 🟡 MEDIUM | AES256 | ✓ Already good |

---

## ✅ Pre-Deployment Checklist

- [ ] **Terraform state backend configured**
  - [ ] S3 bucket for state created
  - [ ] DynamoDB table for locks created
  - [ ] `backend "s3"` block in `providers.tf`
  - [ ] Reinitialized with `terraform init`

- [ ] **Security groups updated**
  - [ ] Changed `name` to `name_prefix` in all SGs
  - [ ] Added `lifecycle { create_before_destroy = true }`
  - [ ] Verified SG naming strategy

- [ ] **S3 bucket naming fixed**
  - [ ] Updated `variables.tf` with account ID
  - [ ] Updated `s3_bucket_name` variable default
  - [ ] Confirmed global uniqueness

- [ ] **IAM roles separated**
  - [ ] Created new `victim_ec2_role` (minimal permissions)
  - [ ] Kept `wazuh_ec2_role` (full permissions)
  - [ ] Updated `instance.tf` to use correct role for each instance
  - [ ] Restricted resource ARNs in policies

- [ ] **Terraform validated**
  - [ ] Ran `terraform validate` successfully
  - [ ] Ran `terraform fmt` to format code
  - [ ] No errors in `terraform plan`

---

## 🚀 Deployment Steps (Correct Order)

### Step 1: Setup State Backend (One Time Only)
```bash
# Create backend infrastructure
cd terraform
terraform init

# Apply only backend resources
terraform apply -target=aws_s3_bucket.terraform_state \
                 -target=aws_dynamodb_table.terraform_lock

# Get account ID
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Update providers.tf
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" providers.tf

# Migrate state to backend
terraform init  # Choose 'yes' to migrate state
```

### Step 2: Deploy Fixed Infrastructure
```bash
# Validate
terraform validate
terraform fmt -check

# Plan
terraform plan -out=tfplan

# Review plan for any issues
terraform show tfplan

# Apply
terraform apply tfplan
```

### Step 3: Verify Deployment
```bash
# Check Terraform state
terraform state list

# Verify AWS resources
aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=cloud-soc"

aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=cloud-soc"

# Check state locking
aws dynamodb scan --table-name terraform-state-lock --region eu-north-1
```

---

## 🧹 Cleanup Steps (Correct Order)

### Normal Cleanup
```bash
# 1. Use enhanced cleanup script
./scripts/terraform_cleaner_enhanced.sh

# 2. Verify everything destroyed
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=cloud-soc" \
  --query 'Reservations[].Instances[]' | jq 'length'

# Should output: 0
```

### Emergency Cleanup (If Terraform Fails)
```bash
# 1. Manually cleanup AWS resources
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy

# 2. Wait for termination
aws ec2 wait instance-terminated --instance-ids i-xxxxx i-yyyyy

# 3. Clean up other resources
aws ec2 delete-security-group --group-id sg-xxxxx
aws ec2 delete-nat-gateway --nat-gateway-id nat-xxxxx
aws ec2 release-address --allocation-id eipalloc-xxxxx

# 4. Try Terraform destroy again
terraform destroy -auto-approve

# 5. If still failing, remove from state
terraform state rm aws_security_group.wazuh_sg
terraform destroy -auto-approve
```

---

## 🔍 Troubleshooting Common Issues

### Problem: "BucketAlreadyExists"
**Cause**: S3 bucket name collision  
**Fix**: 
```bash
# Verify bucket account ID
terraform plan | grep "cloud-soc-wazuh-assets"

# Update variable or import existing bucket
terraform import aws_s3_bucket.wazuh_assets cloud-soc-wazuh-assets-123456789
```

### Problem: "An error occurred (InvalidParameterValue) when calling the CreateSecurityGroup operation: The security group 'wazuh-sg' already exists"
**Cause**: SG name collision from previous deployment  
**Fix**:
```bash
# Find existing SG
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=wazuh-sg" \
  --query 'SecurityGroups[].GroupId'

# Import into Terraform
terraform import aws_security_group.wazuh_sg sg-xxxxx

# Or delete from AWS and retry
aws ec2 delete-security-group --group-id sg-xxxxx
terraform apply
```

### Problem: "All nodes are in disabled state"
**Cause**: Dependent resources not destroyed in correct order  
**Fix**:
```bash
# Check state
terraform show | grep "aws_" | grep "id"

# Manually delete by type (reverse order of creation)
# 1. EC2 instances
# 2. ENIs
# 3. Security groups
# 4. Route tables
# 5. Subnets
# 6. NAT gateways
# 7. Elastic IPs
# 8. Internet gateways
# 9. VPC

# Then retry destroy
terraform destroy -auto-approve
```

### Problem: "Resource is in use and cannot be deleted"
**Cause**: Dependencies not removed first  
**Fix**:
```bash
# Find what's using the resource
aws ec2 describe-security-group-references --group-id sg-xxxxx

# Detach from instances/resources
aws ec2 modify-instance-attribute --instance-id i-xxxxx \
  --security-groups sg-yyyyy

# Try again
terraform destroy -auto-approve
```

### Problem: "Error: Could not acquire the state lock"
**Cause**: Concurrent operations or stale lock  
**Fix**:
```bash
# Check lock status
aws dynamodb scan --table-name terraform-state-lock

# Force unlock (use with caution!)
terraform force-unlock <LOCK_ID>

# Retry operation
terraform apply
```

---

## 📊 Deployment Validation Checklist

After deployment, verify:

- [ ] **VPC created**
  ```bash
  aws ec2 describe-vpcs --filters "Name=tag:Name,Values=wazuh-vpc"
  ```

- [ ] **Subnets created (3)**
  ```bash
  aws ec2 describe-subnets \
    --filters "Name=tag:Project,Values=cloud-soc" \
    --query 'Subnets[].{Name:Tags[?Key==\`Name\`].Value|[0],CIDR:CidrBlock}'
  ```

- [ ] **Security Groups created (3)**
  ```bash
  aws ec2 describe-security-groups \
    --filters "Name=tag:Project,Values=cloud-soc" \
    --query 'SecurityGroups[].{Name:GroupName,Rules:IpPermissions|length}'
  ```

- [ ] **EC2 Instances created (2)**
  ```bash
  aws ec2 describe-instances \
    --filters "Name=tag:Project,Values=cloud-soc" \
    --query 'Reservations[].Instances[].{ID:InstanceId,Name:Tags[?Key==\`Name\`].Value|[0],State:State.Name}'
  ```

- [ ] **IAM Roles created (2)**
  ```bash
  aws iam list-roles --query \
    'Roles[?RoleName==`wazuh-ec2-role` || RoleName==`victim-ec2-role`].RoleName'
  ```

- [ ] **S3 Bucket created with correct name**
  ```bash
  aws s3api list-buckets \
    --query "Buckets[?contains(Name, 'cloud-soc-wazuh-assets')].Name"
  ```

- [ ] **Terraform state in S3**
  ```bash
  aws s3 ls s3://terraform-state-$(aws sts get-caller-identity --query Account --output text)-eu-north-1/cloud-soc/
  ```

- [ ] **No security group name collisions**
  ```bash
  aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=wazuh-sg,victim-sg,jail-sg" \
    --query 'SecurityGroups[] | length'
  ```

---

## 🔐 Security Best Practices

### Before Production

- [ ] Enable S3 versioning
  ```bash
  aws s3api put-bucket-versioning \
    --bucket cloud-soc-wazuh-assets-ACCOUNT_ID \
    --versioning-configuration Status=Enabled
  ```

- [ ] Enable S3 encryption
  ```bash
  # Already configured in Terraform
  terraform apply -target=aws_s3_bucket_server_side_encryption_configuration.wazuh_assets
  ```

- [ ] Block public access to S3
  ```bash
  # Already configured in Terraform
  terraform apply -target=aws_s3_bucket_public_access_block.wazuh_assets
  ```

- [ ] Review IAM policies
  ```bash
  aws iam get-role-policy --role-name wazuh-ec2-role --policy-name inline-policy
  aws iam list-attached-role-policies --role-name wazuh-ec2-role
  ```

- [ ] Enable CloudTrail logging (manual setup)
  ```bash
  aws cloudtrail create-trail --name cloud-soc-trail \
    --s3-bucket-name cloudtrail-logs-bucket \
    --is-multi-region-trail
  ```

---

## 📝 Team Communication Template

### For Team Members Deploying Infrastructure

```
📋 Deployment Checklist

Before you deploy:
1. [ ] Read RESOURCE_MANAGEMENT_ANALYSIS.md
2. [ ] Pull latest changes with all fixes
3. [ ] Verify Terraform backend is configured
4. [ ] Check that no one else is deploying

Deployment:
1. [ ] Run: terraform plan -out=tfplan
2. [ ] Review plan output carefully
3. [ ] Ask team for approval
4. [ ] Run: terraform apply tfplan

After deployment:
1. [ ] Run validation checklist from README
2. [ ] Notify team of successful deployment
3. [ ] Document any issues in GitHub
```

### For Team Members Destroying Infrastructure

```
⚠️  Destruction Warning

Before you destroy:
1. [ ] Back up any data from instances
2. [ ] Notify team that you're destroying
3. [ ] Get approval from tech lead
4. [ ] No one else can deploy simultaneously

Destruction:
1. [ ] Run: ./scripts/terraform_cleaner_enhanced.sh
2. [ ] Type 'yes' only when absolutely sure
3. [ ] Wait for all resources to be deleted

After destruction:
1. [ ] Verify all resources deleted
2. [ ] Check AWS bill/costs stopped
3. [ ] Document destruction in team Slack
```

---

## 🚨 Emergency Procedures

### Rollback Last Changes
```bash
# If deployment broke production:
git log --oneline terraform/
git checkout HEAD~1 -- terraform/

terraform plan  # Review changes
terraform apply

# Notify team immediately!
```

### Recover from State Corruption
```bash
# If state is corrupted:
# 1. Restore from backup
aws s3 cp s3://terraform-state-bucket/cloud-soc/terraform.tfstate.backup ./

# 2. Restore to local
cp terraform.tfstate.backup terraform.tfstate

# 3. Reinitialize
terraform init

# 4. Reconcile with AWS
terraform refresh

# 5. Plan carefully
terraform plan

# 6. Apply if OK
terraform apply
```

### Force Unlock (Last Resort)
```bash
# If someone's deployment hangs and locks state:
# Get the lock ID
aws dynamodb scan --table-name terraform-state-lock \
  --query 'Items[0].LockID.S' --output text

# Unlock it
terraform force-unlock <LOCK_ID>

# Have the person who started it reconnect
```

---

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Terraform State Management](https://www.terraform.io/language/state)
- [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)

---

## Support

**Issues?** Check these in order:
1. This checklist for similar problems
2. [RESOURCE_MANAGEMENT_ANALYSIS.md](RESOURCE_MANAGEMENT_ANALYSIS.md)
3. [RESOURCE_FIXES_GUIDE.md](RESOURCE_FIXES_GUIDE.md)
4. GitHub issues in this repository
5. Ask team lead or DevOps engineer
