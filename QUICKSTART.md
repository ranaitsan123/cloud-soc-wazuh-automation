# Quick Start Guide

## 1-Minute Setup

```bash
# Setup
cd /workspaces/cloud-soc-wazuh-automation
cp .env.example .env
# Edit .env with your AWS credentials

# Install
pip install -e .

# Run
cloud-soc status
```

## Common Commands

### Check Infrastructure Status
```bash
cloud-soc status
```

Output shows:
- VPC details (ID, CIDR, state)
- Available subnets with availability zones
- Running EC2 instances with IPs
- Security groups in the VPC

### Apply Infrastructure
```bash
# With approval prompt
cloud-soc apply

# Automatic approval (CI/CD friendly)
cloud-soc apply --auto-approve

# With custom variable file
cloud-soc apply --var-file prod.tfvars
```

### Destroy Infrastructure
```bash
# With confirmation (safe)
cloud-soc destroy

# With automatic approval
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

## Python API Usage

### Quick API Examples

#### 1. Find VPC and Resources

```python
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.config.settings import get_settings

settings = get_settings()
ec2 = EC2Service(region=settings.project.aws.region)

# Find VPC
vpc = ec2.find_vpc(project_tag="cloud-soc")
print(f"VPC: {vpc.name} ({vpc.id})")

# Find resources in VPC
subnets = ec2.find_subnets(vpc.id)
instances = ec2.find_instances(vpc_id=vpc.id)
sgs = ec2.find_security_groups(vpc.id)

for instance in instances:
    print(f"  Instance: {instance.id} ({instance.state})")
```

#### 2. Apply Infrastructure

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

#### 3. Clean Up Resources

```python
from cloudsoc.cleanup.services import NetworkCleanupService, VPCCleanupService
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag="cloud-soc")

# Cleanup ENIs
eni_cleanup = NetworkCleanupService()
deleted = eni_cleanup.cleanup_orphaned_enis(vpc_id=vpc.id)
print(f"Deleted {deleted} orphaned ENIs")

# Cleanup VPC instances
vpc_cleanup = VPCCleanupService()
vpc_cleanup.cleanup_vpc_instances(vpc_id=vpc.id)
```

#### 4. Run Custom YAML Deployment

```python
from cloudsoc.deployment.executor import DeploymentService
from pathlib import Path

deployment = DeploymentService(deployment_dir=Path("deployment"))

success = deployment.run_deployment(
    "wazuh_manager",
    variables={
        "s3_bucket_name": "cloud-soc-wazuh-assets",
        "s3_prefix": "wazuh-docker"
    }
)
```

#### 5. Manage SSM Parameters

```python
from cloudsoc.aws.ssm import SSMService

ssm = SSMService(region="eu-north-1")

# Create parameter
ssm.put_parameter(
    name="/cloud-soc/wazuh/manager-ip",
    value="10.0.1.10",
    param_type="String",
    description="Wazuh Manager IP"
)

# Retrieve parameter
wazuh_ip = ssm.get_parameter("/cloud-soc/wazuh/manager-ip")
print(f"Wazuh Manager: {wazuh_ip}")

# Send command via SSM
cmd_id = ssm.send_command(
    instance_ids=["i-12345"],
    commands=["echo 'Hello from SSM'"]
)
```

#### 6. ECR Repository Management

```python
from cloudsoc.aws.ecr import ECRService

ecr = ECRService(region="eu-north-1")

# List repositories
repos = ecr.list_repositories()
for repo in repos:
    print(f"  {repo['name']}: {repo['uri']}")

# Create repository
repo = ecr.create_repository(
    "wazuh-agent",
    tags={"Project": "cloud-soc"}
)
```

#### 7. S3 Bucket Operations

```python
from cloudsoc.aws.s3 import S3Service

s3 = S3Service(region="eu-north-1")

# List buckets
buckets = s3.list_buckets()
for bucket in buckets:
    print(f"  {bucket.name}")

# Create bucket
bucket = s3.create_bucket(
    "cloud-soc-logs",
    region="eu-north-1",
    tags={"Project": "cloud-soc"}
)

# Delete bucket
s3.delete_bucket("old-bucket", force=True)
```

## Docker Workflow

### Option 1: Interactive Shell

```bash
docker-compose run --rm devops bash

# Inside container
cloud-soc status
cloud-soc apply
```

### Option 2: Single Command

```bash
docker-compose run --rm devops cloud-soc status
docker-compose run --rm devops cloud-soc apply --auto-approve
```

### Option 3: Python Script

```bash
docker-compose run --rm devops python -c "
from cloudsoc.aws.ec2 import EC2Service
ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag='cloud-soc')
print(f'VPC: {vpc.id}' if vpc else 'No VPC found')
"
```

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test
pytest cloudsoc/tests/test_ec2_service.py::test_find_vpc

# With output
pytest -v -s

# With coverage
pytest --cov=cloudsoc --cov-report=html
```

### Write a Test

```python
# cloudsoc/tests/test_my_feature.py
from unittest.mock import patch
from cloudsoc.aws.ec2 import EC2Service

def test_find_vpc():
    with patch("boto3.Session"):
        ec2 = EC2Service()
        # Mock the API response
        ec2.client.describe_vpcs = lambda **kw: {
            "Vpcs": [{"VpcId": "vpc-123", "CidrBlock": "10.0.0.0/16"}]
        }
        
        vpc = ec2.find_vpc(name="test")
        assert vpc.id == "vpc-123"
```

## Debugging

### Enable Debug Logging

```bash
# Via environment variable
export LOG_LEVEL=DEBUG
cloud-soc status

# Via .env file
echo "LOG_LEVEL=DEBUG" >> .env
cloud-soc status
```

### Check AWS Access

```bash
# Verify credentials
aws sts get-caller-identity

# List available resources
aws ec2 describe-vpcs --region eu-north-1

# Or via Python
from cloudsoc.aws.ec2 import EC2Service
ec2 = EC2Service()
vpcs = ec2.client.describe_vpcs()
print(vpcs)
```

### Terraform Debug

```bash
# Validate Terraform
cloud-soc validate

# Show state
cd terraform
terraform show

# Show plan details
terraform plan -json | python -m json.tool
```

## Common Issues

### 1. ImportError: No module named 'cloudsoc'

```bash
# Install in development mode
pip install -e .

# Verify
python -c "from cloudsoc.main import app; print('OK')"
```

### 2. AWS Credentials Not Found

```bash
# Check environment
echo $AWS_ACCESS_KEY_ID

# Or set from .env
set -a
source .env
set +a
aws sts get-caller-identity
```

### 3. Terraform Not Found

```bash
# Check installation
which terraform
terraform version

# In Docker
docker-compose exec devops which terraform
```

### 4. Permission Denied on /var/run/docker.sock

```bash
# Check permissions
ls -la /var/run/docker.sock

# Check Docker access
docker ps
```

## Next Steps

1. **Explore the code** - Check `cloudsoc/` directory structure
2. **Read full docs** - See `cloudsoc/README.md` and `MIGRATION_GUIDE.md`
3. **Run tests** - Execute `pytest` to verify setup
4. **Extend functionality** - Add new services or CLI commands
5. **Deploy** - Use `cloud-soc apply` to deploy infrastructure

## Getting Help

- **CLI help**: `cloud-soc --help` or `cloud-soc <command> --help`
- **Python API**: Check docstrings and type hints
- **Tests**: Look at `cloudsoc/tests/` for examples
- **Issues**: Enable debug logging and check error messages

## Key Files

| File | Purpose |
|------|---------|
| `cloudsoc/main.py` | CLI entry point |
| `cloudsoc/terraform/runner.py` | Terraform orchestration |
| `cloudsoc/aws/ec2.py` | EC2 operations |
| `cloudsoc/aws/iam.py` | IAM operations |
| `cloudsoc/aws/s3.py` | S3 operations |
| `cloudsoc/aws/ecr.py` | ECR operations |
| `cloudsoc/aws/ssm.py` | SSM operations |
| `cloudsoc/config/settings.py` | Configuration management |
| `cloudsoc/cleanup/services.py` | Cleanup operations |

## Tips & Tricks

### Run Multiple Commands Sequentially

```bash
cloud-soc validate && \
cloud-soc apply --auto-approve && \
cloud-soc status
```

### Get JSON Output

```python
from cloudsoc.aws.ec2 import EC2Service
import json

ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag="cloud-soc")
print(json.dumps(vpc.dict(), indent=2))
```

### Parallel Execution

```python
from concurrent.futures import ThreadPoolExecutor
from cloudsoc.aws.ec2 import EC2Service

ec2 = EC2Service()
vpc = ec2.find_vpc(project_tag="cloud-soc")

# Parallel resource discovery
with ThreadPoolExecutor(max_workers=3) as executor:
    subnets_future = executor.submit(ec2.find_subnets, vpc.id)
    instances_future = executor.submit(ec2.find_instances, vpc_id=vpc.id)
    sgs_future = executor.submit(ec2.find_security_groups, vpc.id)
    
    subnets = subnets_future.result()
    instances = instances_future.result()
    sgs = sgs_future.result()
```

## Performance Tips

1. **Cache EC2Service instances** - Create once, reuse
2. **Use filters** - EC2 API filters are faster than client-side
3. **Batch operations** - Process multiple resources together
4. **Parallel discovery** - Use threading for independent calls

---

**Ready to start?** Run: `cloud-soc status`
