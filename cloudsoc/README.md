# Cloud SOC - Python Infrastructure Platform

## Overview

A modern, production-ready Python CLI for orchestrating cloud security infrastructure. Built with **Typer**, **Boto3**, and **Terraform**, providing safe infrastructure management with full logging, validation, and error handling.

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your AWS credentials
nano .env
```

Required environment variables:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=eu-north-1
PROJECT_TAG=cloud-soc
```

### 2. Install Package

```bash
# Development mode (includes dev dependencies)
pip install -e .

# Or with minimal dependencies
pip install -e . --no-extras
```

### 3. Run Commands

```bash
# Check infrastructure status
cloud-soc status

# Validate configuration
cloud-soc validate

# Apply infrastructure
cloud-soc apply

# Destroy infrastructure (with confirmation)
cloud-soc destroy

# Get help
cloud-soc --help
cloud-soc apply --help
```

## Core Components

### CLI (`cloudsoc/main.py`)

Typer-based command-line interface with the following commands:

| Command | Purpose |
|---------|---------|
| `apply` | Deploy infrastructure changes |
| `destroy` | Remove infrastructure |
| `status` | Display current infrastructure state |
| `validate` | Validate Terraform configuration |
| `version` | Show version info |

**Options:**
```bash
--auto-approve      # Skip approval prompts
--var-file FILE     # Terraform variable files
--force             # Force operation without confirmation
--debug             # Enable debug logging
```

### Terraform Runner (`cloudsoc/terraform/runner.py`)

Orchestrates all Terraform operations with error handling:

```python
from cloudsoc.terraform.runner import TerraformRunner
from pathlib import Path

runner = TerraformRunner(
    terraform_dir=Path("terraform"),
    auto_approve=False
)

runner.init()
runner.validate()
runner.plan(out="tfplan", var_files=["terraform.tfvars"])
runner.apply(plan_file="tfplan")
```

**Operations:**
- `init()` - Initialize Terraform
- `validate()` - Validate configuration
- `plan()` - Create execution plan
- `apply()` - Apply changes
- `destroy()` - Destroy resources
- `import_resource()` - Import existing resources
- `output()` - Get outputs

### AWS Services

#### EC2Service (`cloudsoc/aws/ec2.py`)

```python
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service(region="eu-north-1")

# Find resources
vpc = ec2.find_vpc(project_tag="cloud-soc")
subnets = ec2.find_subnets(vpc_id=vpc.id)
instances = ec2.find_instances(vpc_id=vpc.id, project_tag="cloud-soc")
sgs = ec2.find_security_groups(vpc_id=vpc.id)

# Get specific resource
instance = ec2.get_instance("i-0123456789abcdef0")

# Manage instances
ec2.terminate_instances(["i-123", "i-456"])
```

#### IAMService (`cloudsoc/aws/iam.py`)

```python
from cloudsoc.aws.iam import IAMService

iam = IAMService()

# Get role
role = iam.get_role("wazuh-manager-role")

# List roles
roles = iam.list_roles(path_prefix="/")

# Create role
new_role = iam.create_role(
    role_name="my-new-role",
    assume_role_policy={...},
    tags={"Project": "cloud-soc"}
)

# Delete role
iam.delete_role("my-new-role")
```

### Cleanup Services (`cloudsoc/cleanup/services.py`)

#### NetworkCleanupService

```python
from cloudsoc.cleanup.services import NetworkCleanupService

cleanup = NetworkCleanupService(region="eu-north-1")

# Find orphaned ENIs
orphaned = cleanup.find_orphaned_enis(vpc_id=vpc.id)

# Delete specific ENI
cleanup.delete_eni("eni-12345")

# Clean all orphaned ENIs
deleted_count = cleanup.cleanup_orphaned_enis(vpc_id=vpc.id)
```

#### VPCCleanupService

```python
from cloudsoc.cleanup.services import VPCCleanupService

vpc_cleanup = VPCCleanupService(region="eu-north-1")

# Terminate instances in VPC
vpc_cleanup.cleanup_vpc_instances(vpc_id=vpc.id)

# Delete security groups (except default)
vpc_cleanup.cleanup_security_groups(vpc_id=vpc.id)
```

### Ansible Service (`cloudsoc/ansible/deploy.py`)

```python
from cloudsoc.ansible.deploy import AnsibleService

ansible = AnsibleService(playbooks_dir=Path("ansible/playbooks"))

# Run playbook
success = ansible.run_playbook(
    "configure-wazuh.yml",
    inventory="inventory.yml",
    extra_vars={"manager_ip": "10.0.1.10"},
    tags=["deploy"],
    check=False
)

# Run ad-hoc task
success = ansible.run_task(
    hosts="all",
    module="ping",
    become=True
)
```

### Configuration (`cloudsoc/config/settings.py`)

```python
from cloudsoc.config.settings import get_settings

settings = get_settings()

# Project config
print(settings.project.name)           # "cloud-soc"
print(settings.project.tag)            # "cloud-soc"
print(settings.project.environment)    # "dev"

# AWS config
print(settings.project.aws.region)     # "eu-north-1"
print(settings.project.aws.profile)    # None or profile name

# Logging
print(settings.log_level)              # "INFO"
print(settings.debug)                  # False
```

### Type-Safe Models (`cloudsoc/models/resources.py`)

All resources use Pydantic models:

```python
from cloudsoc.models.resources import VPC, EC2Instance, SecurityGroup

# Type-safe access with IDE autocomplete
vpc: VPC = ec2.find_vpc(...)
print(vpc.id)              # ✓ Valid
print(vpc.cidr_block)      # ✓ Valid
print(vpc.invalid_key)     # ✗ Raises validation error

# Easy serialization
vpc_dict = vpc.dict()
vpc_json = vpc.json()
```

Available models:
- `VPC` - Virtual Private Cloud
- `Subnet` - Network subnet
- `SecurityGroup` - Security group
- `EC2Instance` - EC2 instance
- `NetworkInterface` - ENI
- `IAMRole` - IAM role
- `S3Bucket` - S3 bucket
- `OperationResult` - Generic operation result

### Utilities

#### Logger (`cloudsoc/utils/logger.py`)

```python
from cloudsoc.utils.logger import logger

logger.info("Starting deployment...")
logger.warning("This is a warning")
logger.error("An error occurred")
logger.debug("Debug information")
```

#### Shell Commands (`cloudsoc/utils/shell.py`)

```python
from cloudsoc.utils.shell import run_command

result = run_command(
    ["terraform", "plan"],
    cwd="terraform",
    capture_output=True
)

print(result.stdout)
print(result.returncode)
```

#### Retry Logic (`cloudsoc/utils/retry.py`)

```python
from cloudsoc.utils.retry import retry

@retry(max_attempts=3, delay=1.0, backoff=2.0)
def unstable_operation():
    # Will retry 3 times with exponential backoff
    return api_call()
```

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific file
pytest cloudsoc/tests/test_ec2_service.py

# With coverage report
pytest --cov=cloudsoc --cov-report=html

# Watch mode (requires pytest-watch)
pytest-watch
```

### Test Examples

```python
def test_find_vpc():
    """Test VPC discovery"""
    ec2 = EC2Service()
    vpc = ec2.find_vpc(project_tag="test")
    assert vpc is not None
    assert vpc.id.startswith("vpc-")

def test_terraform_validation():
    """Test Terraform validation"""
    runner = TerraformRunner(terraform_dir=Path("terraform"))
    runner.validate()  # Should not raise
```

## Docker Usage

### Inside Docker Container

```bash
# Start container with bash
docker-compose run --rm devops bash

# Run Python CLI
cloud-soc status
cloud-soc apply

# Run Python directly
python -m cloudsoc.main status
```

### Without Docker

```bash
# On your local machine
pip install -e .
cloud-soc status
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=eu-north-1
AWS_PROFILE=default

# Project Configuration
PROJECT_NAME=cloud-soc
PROJECT_TAG=cloud-soc
ENVIRONMENT=dev

# Paths
TERRAFORM_DIR=terraform

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Programmatic Configuration

```python
from cloudsoc.config.settings import Settings, ProjectConfig, AWSConfig

custom_settings = Settings(
    project=ProjectConfig(
        name="custom-soc",
        aws=AWSConfig(
            region="us-east-1",
            profile="my-profile"
        )
    ),
    log_level="DEBUG"
)
```

## Architecture Decisions

### Why Python?

1. **Safety** - Type hints, validation with Pydantic
2. **Testability** - Unit testing with Pytest, mocking with Unittest.mock
3. **Maintainability** - Clean code, explicit error handling
4. **Performance** - Direct Boto3 calls vs subprocess overhead
5. **Extensibility** - Easy to add new services and features

### Why Terraform Stays

Terraform remains the source of truth for infrastructure:
- Proven in production
- Excellent state management
- Rich ecosystem of providers
- Python orchestrates, doesn't replace

### Design Patterns

1. **Service Pattern** - Each AWS service gets a dedicated class
2. **Dependency Injection** - Easy to mock and test
3. **Type Safety** - Pydantic models for all data
4. **Error Propagation** - Explicit exceptions, no silent failures
5. **Logging First** - All operations are logged with context

## Troubleshooting

### "ModuleNotFoundError: No module named 'cloudsoc'"

```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "import cloudsoc; print(cloudsoc.__version__)"
```

### "AWS credentials not found"

```bash
# Check environment variables
echo $AWS_ACCESS_KEY_ID

# Or verify .env file
cat .env | grep AWS

# Test AWS access
aws sts get-caller-identity
```

### "Terraform command not found"

```bash
# Verify Terraform is installed
which terraform
terraform version

# In Docker
docker-compose exec devops which terraform
```

### "Permission denied" errors

```bash
# Check Docker socket permissions
ls -la /var/run/docker.sock

# Verify Docker group membership
groups $USER
docker ps
```

## Performance

### Benchmarks

- Terraform init: ~2-3 seconds
- Terraform plan: ~5-10 seconds (depends on resources)
- EC2 discovery: ~500ms-1s
- Status check: ~1-2 seconds

### Optimization Tips

1. **Use cached sessions** - EC2Service keeps connections alive
2. **Parallel operations** - Use threading for independent operations
3. **Minimize Terraform runs** - Plan once, apply once
4. **Filter early** - Use boto3 filters vs client-side filtering

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update docstrings with examples
4. Run `pytest` before committing
5. Keep services focused and testable

## License

See LICENSE file

## Support

For issues:
1. Check MIGRATION_GUIDE.md
2. Review test examples
3. Check logs with `LOG_LEVEL=DEBUG`
4. Open an issue with reproduction steps
