# Deploy Wazuh with Custom YAML

## Overview

This document describes the custom YAML-based deployment workflow used to configure Wazuh Manager and the victim instance after Terraform provisioning.

## Quick Start

```bash
# Step 1: Provision infrastructure (Terraform)
cloud-soc apply --auto-approve

# Step 2: Deploy services (SSM + YAML playbooks)
cloud-soc deploy

# Step 3: Access dashboard
cloud-soc dashboard
```

## New Deployment Workflow (Recommended)

The Cloud SOC project now uses a **two-stage deployment model** for clarity and flexibility:

### Stage 1: Infrastructure (`cloud-soc apply`)

Provisions AWS infrastructure:
```bash
cloud-soc apply --auto-approve
```

Deploys:
- VPC and private subnets
- NAT gateway
- EC2 instances (Wazuh manager, victim server)
- IAM roles and instance profiles
- S3 bucket for assets
- ECR repositories

**Duration:** 15-20 minutes

### Stage 2: Deployment (`cloud-soc deploy`)

Configures services on running instances via AWS SSM:
```bash
# Deploy all services (default)
cloud-soc deploy

# Deploy only Wazuh manager
cloud-soc deploy wazuh

# Deploy only victim server
cloud-soc deploy victim

# Deploy multiple specific targets
cloud-soc deploy wazuh victim
```

**What happens:**
1. Waits for SSM agent readiness on instances
2. Executes custom YAML deployment files
3. Validates deployment completion

**Duration:** 10-15 minutes

## Target-Based Deployments

The orchestrator supports flexible target-based deployments. Deploy individual services independently:

### Deploy All Services (Default)

```bash
cloud-soc deploy
# Deploys both wazuh_manager and victim_server
```

### Deploy Only Wazuh Manager

```bash
cloud-soc deploy wazuh
# OR
cloud-soc deploy wazuh_manager
```

Uses: `deployment/wazuh_manager.yml`

### Deploy Only Victim Server

```bash
cloud-soc deploy victim
# OR
cloud-soc deploy victim_server
```

Uses: `deployment/victim_server.yml`

### Deploy Multiple Targets

```bash
cloud-soc deploy wazuh victim
```

Deploys in order: wazuh, then victim

### Skip Validation

For debugging:
```bash
cloud-soc deploy --skip-validation
```

## Understanding Deployment YAML Files

### File Structure

```
deployment/
├── wazuh_manager.yml       # Wazuh manager configuration
├── wazuh_manager/
│   ├── files/             # Configuration files
│   └── scripts/           # Installation scripts
├── victim_server.yml       # Victim server configuration
└── victim_server/
    ├── files/
    └── scripts/
```

### Task Types

The custom YAML deployment system supports:

- **shell**: Execute arbitrary shell commands
- **command**: Execute commands without shell interpretation
- **package**: Install packages using apt-get
- **directory**: Create directories with specified permissions
- **download**: Download files from S3 or HTTP
- **file**: Create, delete, or append to files
- **service**: Manage systemd services
- **docker**: Execute Docker operations (compose up, compose run, etc.)

### Task Structure

Each task has:

- **name**: Human-readable task description
- **type**: The task type to execute
- **Configuration**: Type-specific parameters

Example:

```yaml
tasks:
  - name: Install prerequisites
    type: package
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
      - docker.io

  - name: Create config directory
    type: directory
    path: /etc/wazuh
    mode: "0755"

  - name: Download configuration
    type: download
    url: s3://bucket/wazuh/config.tar.gz
    dest: /tmp/config.tar.gz

  - name: Extract and install
    type: shell
    cmd: |
      cd /etc/wazuh
      tar -xzf /tmp/config.tar.gz
```

### Variable Substitution

Deployment files support variable substitution with `{{ variable_name }}`:

```yaml
tasks:
  - name: Configure Wazuh agent
    type: shell
    cmd: |
      sudo sed -i 's/MANAGER_IP/{{ wazuh_manager_ip }}/g' /etc/wazuh/agent.conf
    env:
      AWS_REGION: "{{ aws_region }}"
```

Variables are automatically injected by the orchestrator based on Terraform outputs.

## Wazuh Manager Deployment Details

The `deployment/wazuh_manager.yml` file handles:

1. **Install prerequisites**
   - Docker and Docker Compose
   - Git, curl, wget
   - SSL utilities

2. **Create configuration directories**
   - `/etc/wazuh/` - Main config
   - `/var/lib/wazuh/` - Data storage
   - `/var/log/wazuh/` - Log files

3. **Download configuration from S3**
   - Wazuh configuration files
   - SSL certificates
   - Deployment scripts

   Variables used:
   - `s3_bucket_name` - Bucket containing configs
   - `s3_prefix` - Prefix in bucket (default: `wazuh-docker`)

4. **Generate SSL certificates** (if needed)
   - Self-signed certificates for dashboard
   - Certificate authority (CA)

5. **Start Wazuh services**
   - Wazuh manager
   - Wazuh dashboard (if included)
   - Wazuh indexer (if included)

### Injected Variables

The orchestrator automatically injects:

```python
{
    "s3_bucket_name": "cloud-soc-wazuh-assets",
    "s3_prefix": "wazuh-docker"
}
```

## Victim Server Deployment Details

The `deployment/victim_server.yml` file handles:

1. **Install prerequisites**
   - Docker and Docker Compose
   - AWS CLI
   - SSM agent (pre-installed)

2. **Install Wazuh agent**
   - Pull agent from Wazuh repository
   - Install and configure

3. **Configure Wazuh agent**
   - Set manager IP from Terraform output
   - Configure agent-to-manager communication
   - Set agent name and group

   Variables used:
   - `wazuh_manager_ip` - Private IP of Wazuh manager
   - `aws_region` - AWS region for services

4. **Login to ECR**
   - Authenticate with Elastic Container Registry
   - Pull victim container image

   Variables used:
   - `ecr_victim_repository_url` - ECR repository URL

5. **Run victim container**
   - Start attack simulation container
   - Configure volume mounts
   - Set environment variables

### Injected Variables

The orchestrator automatically injects:

```python
{
    "wazuh_manager_ip": "10.0.1.10",
    "aws_region": "eu-north-1",
    "ecr_victim_repository_url": "123456789.dkr.ecr.eu-north-1.amazonaws.com/cloud-soc-victim"
}
```

## Accessing the Wazuh Dashboard

The Wazuh dashboard is private inside the VPC. Use the CLI to open a secure tunnel:

```bash
cloud-soc dashboard
```

Then open in your browser:
```
https://127.0.0.1:8443
```

### Port Forwarding Details

The tunnel:
- Uses AWS Systems Manager (SSM) Session Manager
- Requires no SSH keys
- Works with private instances in VPC
- Closes when you press Ctrl+C

### Custom Ports

Forward to a different local port:
```bash
cloud-soc dashboard --local-port 9443
```

Or connect to a different remote port:
```bash
cloud-soc dashboard --remote-port 8443
```

## Deployment Workflow Examples

### Example 1: Full Deployment

```bash
# 1. Provision infrastructure
cloud-soc apply --auto-approve

# 2. Wait for instances to boot
sleep 30

# 3. Deploy all services
cloud-soc deploy

# 4. Check status
cloud-soc status

# 5. Access dashboard
cloud-soc dashboard
```

### Example 2: Wazuh Only (Testing)

```bash
# Deploy infrastructure
cloud-soc apply --auto-approve

# Wait for instances
sleep 30

# Deploy only Wazuh manager
cloud-soc deploy wazuh

# Test Wazuh
cloud-soc dashboard
```

### Example 3: Retry Failed Deployment

```bash
# Initial deployment (some tasks fail)
cloud-soc deploy

# Check logs, fix issues in YAML file...

# Retry only the failed target (infrastructure untouched!)
cloud-soc deploy wazuh

# Continue with victim
cloud-soc deploy victim
```

### Example 4: CI/CD Pipeline

```bash
#!/bin/bash
set -e

# Setup
export AWS_PROFILE=cloud-soc

# 1. Infrastructure (20 min)
echo "=== Provisioning infrastructure ==="
cloud-soc apply --auto-approve

# 2. Wait for boot
echo "=== Waiting for instances to boot ==="
sleep 60

# 3. Deployment (15 min)
echo "=== Deploying services ==="
cloud-soc deploy

# 4. Verify
echo "=== Verifying deployment ==="
cloud-soc status

# 5. Report
echo "=== Deployment Complete ==="
echo "Dashboard: https://127.0.0.1:8443"
```

## Running Tasks via SSM

The recommended workflow is to use the custom YAML deployment system which handles task execution via AWS SSM. This provides:

- **Secure remote execution** - No SSH keys needed
- **Consistent definitions** - YAML-based, version-controlled
- **Error handling** - Task failures are caught and reported
- **Logging** - Full execution logs in CloudWatch
- **No external dependencies** - Unlike Ansible

## Advanced: Custom Deployment Targets

To add a new deployment target (e.g., Grafana, Elasticsearch):

1. **Create deployment YAML**:
   ```
   deployment/grafana.yml
   ```

2. **Define tasks in YAML**:
   ```yaml
   tasks:
     - name: Install Grafana
       type: package
       packages:
         - grafana
     
     - name: Start Grafana
       type: service
       name: grafana-server
       state: started
   ```

3. **Use the CLI**:
   ```bash
   cloud-soc deploy grafana
   ```

No code changes needed! The orchestrator discovers targets from the `deployment/` directory.

## Notes

- **Two-stage workflow** provides clear separation between infrastructure and deployment
- **Terraform** remains responsible for infrastructure provisioning
- **Custom YAML** handles service configuration and runtime deployment
- **SSM** enables secure remote control for private instances
- **No external dependencies** - Lightweight alternative to Ansible
- **Target-based deployments** provide flexibility for partial updates
- **Independent retry** - Redeploy individual services without reprovisioning

## See Also

- [Quick Start Guide](../../1-getting-started/02-quick-start.md) - Getting started
- [Orchestrator Architecture](../../3-reference/orchestrator-architecture.md) - Technical details
- [Troubleshooting](../../troubleshooting/README.md) - Common issues
