# 02 Quick Start

## Overview

This guide covers the commands to deploy infrastructure and services.

The workflow is split into two independent stages for clarity:

1. **Infrastructure** (`cloud-soc apply`): Provisions AWS resources using Terraform
2. **Deployment** (`cloud-soc deploy`): Configures services using SSM and custom YAML

This separation makes failures immediately obvious and allows independent retry.

## Typical Workflow

```bash
# Step 1: Provision infrastructure (Terraform only)
cloud-soc apply --auto-approve

# Step 2: Deploy services (SSM + Playbooks)
cloud-soc deploy

# Step 3: Access the dashboard
cloud-soc dashboard

# Step 4: Cleanup when done
cloud-soc destroy --auto-approve --force
```

## Common Commands

### 1. Infrastructure - Apply (Terraform Only)

Provisions AWS infrastructure without any deployment or SSM operations.

```bash
# With approval prompt
cloud-soc apply

# Automatic approval (CI/CD friendly)
cloud-soc apply --auto-approve

# With custom Terraform variable file
cloud-soc apply --var-file prod.tfvars
```

**Output:**
```
[INIT] Terraform initialized
[IMPORT] Resources imported
[VALIDATE] Configuration valid
[PLAN] 12 resources to create
[APPLY] Creating infrastructure...
[APPLY] Complete

✓ Infrastructure provisioning complete!

Next step: run cloud-soc deploy to deploy services.
Or run cloud-soc status to check infrastructure status.
```

**What gets created:**
- VPC and subnets
- EC2 instances (Wazuh manager, victim server)
- IAM roles and instance profiles
- Security groups
- S3 buckets
- ECR repositories

**Next step:** `cloud-soc deploy`

### 2. Deployment - Deploy Services (SSM + Playbooks)

Deploys services to running instances via SSM. Waits for instance readiness and runs deployment playbooks.

```bash
# Deploy all services (default: wazuh + victim)
cloud-soc deploy

# Deploy only Wazuh manager
cloud-soc deploy wazuh

# Deploy only victim server
cloud-soc deploy victim

# Deploy multiple specific targets
cloud-soc deploy wazuh victim

# Skip deployment validation
cloud-soc deploy --skip-validation
```

**Output:**
```
[SSM] Waiting for i-123...
[SSM] Connected

[DEPLOY] wazuh_manager
[DEPLOY] Uploading files
[DEPLOY] Running install.sh
[DEPLOY] Success

[DEPLOY] victim_server
[DEPLOY] Running deployment
[DEPLOY] Success

✓ Service deployment complete!

Next step: run cloud-soc dashboard to access the Wazuh dashboard.
```

**Supported targets:**
- `wazuh` or `wazuh_manager` - Deploy Wazuh manager
- `victim` or `victim_server` - Deploy victim server
- Custom targets from `deployment/` directory

**Requirements:**
- Infrastructure must already exist (`cloud-soc apply`)
- Instances must be running and reachable via SSM

**Next step:** `cloud-soc dashboard`

### 3. Check Infrastructure Status

Displays current state of VPC, subnets, and instances.

```bash
cloud-soc status
```

**Output:**
```
VPC: cloud-soc-vpc (vpc-0abc123)
  CIDR: 10.0.0.0/16
  State: available

Subnets (2):
  ┌─────────────────────┬──────────────┬─────────────┬──────────┐
  │ Name                │ ID           │ CIDR        │ AZ       │
  ├─────────────────────┼──────────────┼─────────────┼──────────┤
  │ private-subnet-1a   │ subnet-123   │ 10.0.1.0/24 │ eu-1a    │
  │ private-subnet-1b   │ subnet-456   │ 10.0.2.0/24 │ eu-1b    │
  └─────────────────────┴──────────────┴─────────────┴──────────┘

Instances (2):
  ┌──────────────────┬──────────────┬──────────┬──────────┬────────────────┐
  │ Name             │ ID           │ Type     │ State    │ IP             │
  ├──────────────────┼──────────────┼──────────┼──────────┼────────────────┤
  │ wazuh-manager    │ i-abc123     │ t3.large │ running  │ 10.0.1.10      │
  │ victim-server    │ i-def456     │ t3.xlarge│ running  │ 10.0.2.10      │
  └──────────────────┴──────────────┴──────────┴──────────┴────────────────┘
```

### 4. Open Wazuh Dashboard

Opens an SSM port-forwarding tunnel to the Wazuh dashboard on localhost.

```bash
# Default ports: 8443 (local) -> 443 (remote)
cloud-soc dashboard

# Custom local port
cloud-soc dashboard --local-port 9443

# Custom remote port (if dashboard on different port)
cloud-soc dashboard --remote-port 8443
```

**Next steps:**
1. Open `https://127.0.0.1:8443` in your browser
2. Accept the self-signed certificate warning
3. Login with Wazuh credentials
4. Press `Ctrl+C` in the terminal to close the tunnel when done

### 5. Destroy Infrastructure

Removes all provisioned AWS resources.

```bash
# With confirmation prompt (safe, default)
cloud-soc destroy

# Automatic approval (be careful!)
cloud-soc destroy --auto-approve --force
```

**Caution:** This will delete:
- EC2 instances
- VPC and subnets
- All associated resources
- (Data in S3 may be retained)

### 6. Validate Configuration

Validates Terraform configuration without making changes.

```bash
cloud-soc validate
```

## Why Split Apply and Deploy?

### Before (Single Command)
```bash
cloud-soc apply
# Does: Terraform + SSM wait + Deployment + Validation
# If deployment fails: Terraform state = SUCCESS, Deployment = FAILED
# User confusion: "Did it work or not?"
```

### After (Two Commands)
```bash
cloud-soc apply      # Terraform only - Either SUCCESS or FAILED (clear!)
cloud-soc deploy     # Deployment only - Either SUCCESS or FAILED (clear!)
```

**Benefits:**
- ✓ **Clear failure attribution** - Know exactly what failed
- ✓ **Independent operations** - Retry failed stage without reprovisioning
- ✓ **Better diagnostics** - Each stage has focused logging
- ✓ **Flexible deployments** - Deploy individual services independently
- ✓ **Future scalability** - Easy to add new targets (grafana, elasticsearch, etc.)

## Complete Example: CI/CD Pipeline

```bash
#!/bin/bash
set -e

# 1. Setup
export AWS_PROFILE=cloud-soc
cd /workspaces/cloud-soc-wazuh-automation

# 2. Provision infrastructure (15-20 minutes)
echo "=== Provisioning infrastructure ==="
cloud-soc apply --auto-approve

# 3. Wait for instances to fully boot
echo "=== Waiting for instances ==="
sleep 60

# 4. Deploy services (10-15 minutes)
echo "=== Deploying services ==="
cloud-soc deploy

# 5. Validate and report
echo "=== Validating deployment ==="
cloud-soc status

echo "=== Deployment Complete ==="
echo "Dashboard: https://127.0.0.1:8443"
```

## Next Steps

- [Deployment Guide](../2-guides/deployment/README.md) - Custom YAML deployments
- [Orchestrator Architecture](../3-reference/orchestrator-architecture.md) - Technical details
- [Troubleshooting](../troubleshooting/README.md) - Common issues and solutions

### Clean Up Resources

```python
from cloudsoc.cleanup.services import NetworkCleanupService, VPCCleanupService
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag="cloud-soc")
```

## Next Steps

- [Deployment Guide](../2-guides/deployment/README.md)
- [Python Migration Guide](../4-explanation/python-migration-guide.md)
