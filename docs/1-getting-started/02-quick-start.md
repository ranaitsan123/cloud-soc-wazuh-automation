# 02 Quick Start

## Overview

This guide covers the first commands to verify the project is installed and to deploy infrastructure.

## Common Commands

### Check Infrastructure Status

```bash
cloud-soc status
```

This command displays:
- VPC details
- subnet information
- running EC2 instances
- security groups

### Apply Infrastructure

```bash
cloud-soc apply
```

For CI/CD or automated deployment:

```bash
cloud-soc apply --auto-approve
```

With a custom Terraform variable file:

```bash
cloud-soc apply --var-file prod.tfvars
```

### Destroy Infrastructure

```bash
cloud-soc destroy
```

Automatic confirmation:

```bash
cloud-soc destroy --auto-approve --force
```

### Open the Wazuh Dashboard

```bash
cloud-soc dashboard
```

Then open:

```bash
https://127.0.0.1:8443
```

### Validate Configuration

```bash
cloud-soc validate
```

## Python API Examples

### Find VPC and Resources

```python
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.config.settings import get_settings

settings = get_settings()
ec2 = EC2Service(region=settings.project.aws.region)

vpc = ec2.find_vpc(project_tag="cloud-soc")
print(f"VPC: {vpc.name} ({vpc.id})")
```

### Apply Infrastructure Programmatically

```python
from cloudsoc.terraform.runner import TerraformRunner
from cloudsoc.config.settings import get_settings

settings = get_settings()
runner = TerraformRunner(
    terraform_dir=settings.project.terraform.dir,
    auto_approve=False
)

runner.init()
runner.validate()
runner.plan()
runner.apply()
```

### Clean Up Resources

```python
from cloudsoc.cleanup.services import NetworkCleanupService, VPCCleanupService
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag="cloud-soc")
```

## Next Steps

- [Ansible Deployment Guide](../2-guides/ansible/README.md)
- [Python Migration Guide](../4-explanation/python-migration-guide.md)
