# Migration Guide: Bash → Python Infrastructure Platform

## Overview

This document describes the migration from Bash scripts to a Python-based infrastructure orchestration platform. The migration follows a phased approach, maintaining backward compatibility while gradually replacing functionality.

## Architecture

### Before (Bash)
```
Scripts (Bash)
    ↓
Terraform
    ↓
AWS CLI (jq, grep, text parsing)
```

### After (Python)
```
Python CLI (Typer)
    ↓
Terraform Runner
    ↓
Boto3 SDK
    ↓
AWS
```

## Technology Stack

| Component | Tool | Version |
|-----------|------|---------|
| CLI Framework | Typer | 0.9+ |
| AWS SDK | Boto3 | 1.26+ |
| Validation | Pydantic | 2.0+ |
| Console UI | Rich | 13.0+ |
| Configuration | YAML + Environment | - |
| Testing | Pytest | 7.0+ |

## Project Structure

```
cloud-soc/
├── pyproject.toml                 # Project metadata and dependencies
├── .env.example                   # Environment variables template
├── README.md                       # Main documentation
├── MIGRATION_GUIDE.md             # This file
│
├── cloudsoc/                       # Main Python package
│   ├── __init__.py
│   ├── main.py                    # Typer CLI entry point
│   │
│   ├── cli/                       # CLI commands
│   │   ├── apply.py
│   │   ├── destroy.py
│   │   └── ...
│   │
│   ├── terraform/                 # Terraform orchestration
│   │   ├── runner.py              # Terraform wrapper
│   │   ├── state.py               # State management
│   │   └── __init__.py
│   │
│   ├── aws/                       # AWS SDK services
│   │   ├── ec2.py                 # EC2 operations
│   │   ├── iam.py                 # IAM operations
│   │   ├── s3.py                  # S3 operations
│   │   └── __init__.py
│   │
│   ├── ansible/                   # Ansible integration
│   │   ├── deploy.py
│   │   └── __init__.py
│   │
│   ├── cleanup/                   # Cleanup and maintenance
│   │   ├── services.py
│   │   └── __init__.py
│   │
│   ├── config/                    # Configuration management
│   │   ├── settings.py
│   │   ├── resources.yaml
│   │   └── __init__.py
│   │
│   ├── models/                    # Pydantic models
│   │   ├── resources.py
│   │   └── __init__.py
│   │
│   ├── utils/                     # Utility functions
│   │   ├── logger.py
│   │   ├── shell.py
│   │   ├── retry.py
│   │   └── __init__.py
│   │
│   └── tests/                     # Test suite
│       ├── test_ec2_service.py
│       ├── test_terraform_runner.py
│       └── __init__.py
│
└── terraform/                     # Original Terraform configs
    ├── *.tf                       # (Unchanged)
    └── ...
```

## Phase 1: Bootstrap Python Project ✅ COMPLETE

### What Was Done

1. **Updated Dockerfile**
   - Added Python dependencies: typer, rich, boto3, pydantic, pytest
   - Installed `uv` package manager
   - Kept all existing tools (Terraform, AWS CLI, jq)

2. **Created Project Structure**
   - `pyproject.toml` - Project configuration
   - Python package directories
   - Configuration management system

3. **Implemented CLI Foundation**
   - Typer-based CLI entry point (`cloudsoc/main.py`)
   - Commands: `apply`, `destroy`, `status`, `validate`, `version`
   - Rich console output with panels and tables

4. **Created Utilities**
   - Logging system (`utils/logger.py`)
   - Shell command execution (`utils/shell.py`)
   - Retry logic (`utils/retry.py`)

5. **Environment Configuration**
   - `.env.example` template
   - Settings system with Pydantic
   - Support for environment variables

### Running the CLI

```bash
# Install dependencies
pip install -e .

# Or inside Docker
docker-compose run --rm devops bash

# Run commands
python -m cloudsoc.main apply
python -m cloudsoc.main destroy --auto-approve
python -m cloudsoc.main status
python -m cloudsoc.main validate
```

## Phase 2: Terraform Wrapper ✅ COMPLETE

### Implementation

The `TerraformRunner` class (`cloudsoc/terraform/runner.py`) wraps all Terraform operations:

```python
from cloudsoc.terraform.runner import TerraformRunner

# Initialize
runner = TerraformRunner(
    terraform_dir=Path("terraform"),
    auto_approve=False
)

# Operations
runner.init()
runner.validate()
runner.plan(out="tfplan")
runner.apply(plan_file="tfplan")
runner.destroy()
runner.import_resource("aws_vpc.main", "vpc-12345")
runner.output("instance_id")
```

### Features

- **Safe execution** with error handling
- **Logging** of all operations
- **State management** for plan files
- **Import support** for existing resources
- **Output parsing** in JSON

## Phase 3: Replace AWS CLI with Boto3 ✅ COMPLETE

### EC2 Service

```python
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service(region="eu-north-1")

# Find resources
vpc = ec2.find_vpc(project_tag="cloud-soc")
subnets = ec2.find_subnets(vpc_id=vpc.id)
instances = ec2.find_instances(vpc_id=vpc.id)
sgs = ec2.find_security_groups(vpc_id=vpc.id)

# Manage instances
ec2.terminate_instances(instance_ids=["i-123", "i-456"])
```

### IAM Service

```python
from cloudsoc.aws.iam import IAMService

iam = IAMService()

# Role operations
role = iam.get_role("wazuh-manager-role")
roles = iam.list_roles()
```

### Benefits Over AWS CLI

| Aspect | AWS CLI | Boto3 |
|--------|---------|-------|
| Parsing | Text/jq | Native Python objects |
| Error handling | Script-level | Exception-based |
| Type safety | None | Pydantic models |
| Testing | Manual | Moto framework |
| Performance | Subprocess overhead | Direct calls |

## Phase 4: Resource Registry System (PLANNED)

### Concept

Declarative resource configuration instead of hardcoded imports.

**resources.yaml:**
```yaml
resources:
  - terraform: aws_vpc.wazuh_vpc
    finder: vpc
    project_tag: cloud-soc

  - terraform: aws_subnet.management_private
    finder: management_subnet
    vpc_ref: aws_vpc.wazuh_vpc
```

**Engine:**
```python
from cloudsoc.terraform.imports import ResourceRegistry

registry = ResourceRegistry.from_yaml("resources.yaml")
registry.import_all(terraform_runner)
```

## Phase 5: Typed Models ✅ COMPLETE

### Pydantic Models

All resources are strongly typed:

```python
from cloudsoc.models.resources import VPC, EC2Instance, OperationResult

vpc: VPC = ec2.find_vpc(...)

# Type-safe access
print(vpc.id)           # ✓ IDE autocomplete
print(vpc.invalid_key)  # ✗ Validation error
```

### Benefits

- IDE autocomplete
- Runtime validation
- Self-documenting code
- Serialization/deserialization
- JSON schema generation

## Phase 6: Cleanup Services ✅ COMPLETE

### Network Cleanup

```python
from cloudsoc.cleanup.services import NetworkCleanupService

cleanup = NetworkCleanupService(region="eu-north-1")

# Find and delete orphaned ENIs
orphaned_enis = cleanup.find_orphaned_enis(vpc_id=vpc.id)
deleted_count = cleanup.cleanup_orphaned_enis(vpc_id=vpc.id)
```

### VPC Cleanup

```python
from cloudsoc.cleanup.services import VPCCleanupService

vpc_cleanup = VPCCleanupService(region="eu-north-1")

# Clean all resources in VPC
vpc_cleanup.cleanup_vpc_instances(vpc_id=vpc.id)
vpc_cleanup.cleanup_security_groups(vpc_id=vpc.id)
```

## Phase 7: SSM & Ansible Services ✅ COMPLETE

### Ansible Service

```python
from cloudsoc.ansible.deploy import AnsibleService

ansible = AnsibleService(playbooks_dir=Path("ansible/playbooks"))

# Run playbooks
ansible.run_playbook(
    "configure-wazuh.yml",
    inventory="inventory/aws_ec2.yml",
    extra_vars={"wazuh_manager_ip": "10.0.1.10"},
    tags=["deploy"]
)

# Ad-hoc commands
ansible.run_task(
    hosts="all",
    module="ping"
)
```

## Phase 8: Logging & Configuration ✅ COMPLETE

### Structured Logging

```python
from cloudsoc.utils.logger import logger

logger.info("Applying infrastructure...")
logger.warning("This will terminate instances")
logger.error("Operation failed")
logger.debug("Debug information")
```

### Configuration Management

```python
from cloudsoc.config.settings import get_settings

settings = get_settings()

print(settings.project.name)          # "cloud-soc"
print(settings.project.aws.region)    # "eu-north-1"
print(settings.log_level)             # "INFO"
```

## Phase 9: Testing ✅ STARTED

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest cloudsoc/tests/test_ec2_service.py

# With coverage
pytest --cov=cloudsoc

# Watch mode
pytest-watch
```

### Example Tests

```python
def test_find_vpc():
    ec2 = EC2Service()
    vpc = ec2.find_vpc(name="test-vpc")
    assert vpc is not None
    assert vpc.id.startswith("vpc-")
```

## Migration Checklist

### Week 1-2: Foundation
- [x] Update Dockerfile with Python dependencies
- [x] Create project structure
- [x] Build CLI with Typer
- [x] Implement logging and config
- [ ] Document CLI usage

### Week 3-4: AWS Integration
- [x] Implement EC2Service
- [x] Implement IAMService
- [ ] Implement S3Service
- [ ] Implement ECRService
- [ ] Implement SSMService
- [ ] Write integration tests

### Week 5-6: Services & Cleanup
- [x] Create AnsibleService
- [x] Create cleanup services
- [x] Add retry logic
- [ ] Add monitoring/alerting
- [ ] Performance optimization

### Week 7-8: Testing & Documentation
- [x] Add unit tests
- [ ] Add integration tests
- [ ] Complete test coverage
- [ ] Write user documentation
- [ ] Create troubleshooting guide

### Week 9: Production Readiness
- [ ] Performance testing
- [ ] Security audit
- [ ] Load testing
- [ ] Backup/recovery procedures
- [ ] Monitoring setup

## Running the New CLI

### Quick Start

```bash
# Setup
cd /workspaces/cloud-soc-wazuh-automation
cp .env.example .env
# Edit .env with your AWS credentials

# Option 1: Direct Python
pip install -e .
cloud-soc apply

# Option 2: Docker
docker-compose run --rm devops bash
cloud-soc apply
```

### Available Commands

```bash
cloud-soc apply            # Apply infrastructure
cloud-soc destroy          # Destroy infrastructure
cloud-soc status           # Show current status
cloud-soc validate         # Validate configuration
cloud-soc version          # Show version
cloud-soc --help           # Show help
```

### Options

```bash
# Apply with auto-approval
cloud-soc apply --auto-approve

# Apply with variable file
cloud-soc apply --var-file terraform.tfvars

# Destroy with auto-approval
cloud-soc destroy --auto-approve --force

# Validate only
cloud-soc validate
```

## Next Steps

1. **Test the CLI** - Run `cloud-soc status` to verify setup
2. **Review code** - Understand the architecture and patterns
3. **Extend services** - Add S3, ECR, SSM services as needed
4. **Add tests** - Expand test coverage
5. **Optimize** - Performance improvements and refactoring
6. **Document** - Update documentation and runbooks

## Key Design Principles

### 1. Keep Terraform Separate

Python orchestrates Terraform, it doesn't replace it.

❌ Bad: Python creates AWS resources directly
✅ Good: Python → Terraform → AWS

### 2. Type Safety

Use Pydantic models for all data structures.

❌ Bad: `vpc_id = response['Vpcs'][0]['VpcId']`
✅ Good: `vpc = VPC(**vpc_data)`

### 3. Explicit Error Handling

Never silently fail.

❌ Bad: `result = run_command() or handle_error()`
✅ Good: `try: run_command() except CommandError: raise`

### 4. Structured Logging

Always use structured logging with context.

❌ Bad: `print("Error")`
✅ Good: `logger.error(f"Failed to import {resource}: {error}")`

### 5. Testability

Design for testability from the start.

❌ Bad: `boto3.client(...)`
✅ Good: Dependency injection, mocking support

## Troubleshooting

### Python Import Errors

```bash
# Install package in development mode
pip install -e .

# Verify installation
python -c "from cloudsoc.main import app; print('OK')"
```

### Terraform Not Found

```bash
# Verify Terraform is installed
which terraform
terraform version

# Check PATH in Docker
docker-compose run --rm devops which terraform
```

### AWS Credentials

```bash
# Verify credentials are set
echo $AWS_ACCESS_KEY_ID
echo $AWS_DEFAULT_REGION

# Test AWS access
aws sts get-caller-identity
```

### Permission Errors

```bash
# Ensure Docker socket is accessible
ls -la /var/run/docker.sock

# Verify Docker can run on the container
docker-compose exec devops docker ps
```

## References

- [Typer Documentation](https://typer.tiangolo.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

For issues or questions:

1. Check existing documentation
2. Review test examples
3. Check Git history for context
4. Open an issue with reproduction steps
