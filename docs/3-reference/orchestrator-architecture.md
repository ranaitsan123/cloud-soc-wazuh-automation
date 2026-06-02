# Orchestrator Architecture

## Overview

The Cloud SOC orchestration layer is designed with **separation of concerns** in mind. Three focused classes handle distinct responsibilities:

1. **TerraformOrchestrator** - Infrastructure provisioning
2. **DeploymentOrchestrator** - Service deployment and validation
3. **DashboardOrchestrator** - Dashboard access and tunneling

This architecture provides clear failure attribution, independent operations, and flexibility for future scaling.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Commands                             │
├─────────────────────────────────────────────────────────────┤
│  cloud-soc apply  │  cloud-soc deploy  │  cloud-soc dashboard │
└────────────┬─────────────────┬─────────────────────────┬────┘
             │                 │                         │
             v                 v                         v
         ┌────────────┐   ┌──────────────┐   ┌─────────────────┐
         │ Terraform  │   │ Deployment   │   │ Dashboard       │
         │ Orchestrator│  │ Orchestrator │   │ Orchestrator    │
         └────────────┘   └──────────────┘   └─────────────────┘
             │                 │                         │
             ├─AWS Terraform   ├─AWS SSM                ├─AWS SSM
             ├─AWS EC2         ├─Deployment Service    └─Port Tunnel
             ├─AWS IAM         ├─Deployment YAML
             └─AWS S3          └─Validation
```

## TerraformOrchestrator

**Purpose:** Manages the Terraform infrastructure lifecycle

**Responsibilities:**
- Initialize Terraform
- Import existing resources
- Validate configuration
- Generate and apply plans
- Destroy infrastructure
- Retrieve outputs

**Usage:** `cloud-soc apply` command

### Methods

#### `init() -> None`
Initializes Terraform with backend configuration.

```python
tf_orchestrator = TerraformOrchestrator()
tf_orchestrator.init()
```

#### `import_all_existing_resources() -> None`
Imports existing AWS resources to prevent recreation.

```python
tf_orchestrator.import_all_existing_resources()
```

#### `validate() -> None`
Validates Terraform configuration without making changes.

```python
tf_orchestrator.validate()
```

#### `plan(var_files: Optional[List[str]]) -> str`
Generates a Terraform plan.

Returns: Path to the plan file

```python
plan_file = tf_orchestrator.plan(var_files=["prod.tfvars"])
```

#### `apply(plan_file: str, auto_approve: bool) -> None`
Applies the Terraform plan to create/modify infrastructure.

```python
tf_orchestrator.apply(plan_file=plan_file, auto_approve=True)
```

#### `destroy(auto_approve: bool) -> None`
Destroys all infrastructure managed by Terraform.

```python
tf_orchestrator.destroy(auto_approve=False)
```

#### `output() -> Dict`
Retrieves Terraform outputs.

Returns: Dictionary of all outputs

```python
outputs = tf_orchestrator.output()
wazuh_id = outputs["wazuh_instance_id"]["value"]
```

### Example: Infrastructure Lifecycle

```python
from cloudsoc.orchestrator import TerraformOrchestrator

# Create orchestrator
tf = TerraformOrchestrator()

# Initialize
tf.init()

# Validate and plan
tf.validate()
plan = tf.plan(var_files=["prod.tfvars"])

# Apply
tf.apply(plan_file=plan, auto_approve=False)

# Get outputs for deployment
outputs = tf.output()

# Later: destroy
tf.destroy(auto_approve=True)
```

## DeploymentOrchestrator

**Purpose:** Manages service deployment to running instances

**Responsibilities:**
- Wait for SSM agent readiness
- Execute deployments to target instances
- Validate deployment completion
- Support target-based deployment

**Usage:** `cloud-soc deploy [targets]` command

### Methods

#### `wait_for_ssm_ready(instance_ids: List[str], timeout: int, poll_interval: int) -> None`
Waits for SSM agent to be ready on specified instances.

Parameters:
- `instance_ids`: List of EC2 instance IDs
- `timeout`: Maximum wait time in seconds (default: 600)
- `poll_interval`: Check interval in seconds (default: 15)

Raises: `OrchestrationError` if SSM is not ready

```python
deployment = DeploymentOrchestrator()
deployment.wait_for_ssm_ready(
    ["i-123456", "i-789abc"],
    timeout=600,
    poll_interval=15
)
```

#### `deploy_targets(terraform_outputs: Dict, targets: Optional[List[str]], skip_validation: bool) -> None`
Deploys services to specified targets.

Parameters:
- `terraform_outputs`: Dictionary from `TerraformOrchestrator.output()`
- `targets`: List of targets to deploy
  - `None` or `[]`: Deploy all configured targets
  - `["wazuh"]`: Deploy only Wazuh
  - `["victim"]`: Deploy only victim
  - `["wazuh", "victim"]`: Deploy multiple
  - Custom targets from `deployment/` directory
- `skip_validation`: Whether to skip validation (default: False)

```python
deployment.deploy_targets(
    terraform_outputs,
    targets=["wazuh"],
    skip_validation=False
)
```

#### `validate_deployment(terraform_outputs: Dict) -> None`
Validates that deployment is healthy.

```python
deployment.validate_deployment(terraform_outputs)
```

### Example: Full Deployment Workflow

```python
from cloudsoc.orchestrator import TerraformOrchestrator, DeploymentOrchestrator

# Get infrastructure outputs
tf = TerraformOrchestrator()
outputs = tf.output()

# Initialize deployment
deployment = DeploymentOrchestrator()

# Wait for instances
wazuh_id = outputs["wazuh_instance_id"]["value"]
victim_id = outputs["victim_instance_id"]["value"]
deployment.wait_for_ssm_ready([wazuh_id, victim_id])

# Deploy Wazuh only
deployment.deploy_targets(outputs, targets=["wazuh"])

# Deploy victim
deployment.deploy_targets(outputs, targets=["victim"])

# Validate
deployment.validate_deployment(outputs)
```

### Target Mapping

The orchestrator supports user-friendly target names:

| User Input | Deployment Name | Instance |
|-----------|-----------------|----------|
| `wazuh` | `wazuh_manager` | Wazuh manager instance |
| `wazuh_manager` | `wazuh_manager` | Wazuh manager instance |
| `victim` | `victim_server` | Victim server instance |
| `victim_server` | `victim_server` | Victim server instance |
| Custom | Custom | Any deployment in `deployment/` directory |

### Variable Injection

When deploying, the orchestrator automatically injects variables based on target:

**For `wazuh_manager`:**
```python
{
    "s3_bucket_name": "...",      # From Terraform output
    "s3_prefix": "wazuh-docker"   # From Terraform output
}
```

**For `victim_server`:**
```python
{
    "wazuh_manager_ip": "10.0.1.10",     # From Terraform output
    "aws_region": "eu-north-1",          # From settings
    "ecr_victim_repository_url": "..."   # From Terraform output
}
```

**For custom targets:**
All Terraform outputs are passed as variables.

## DashboardOrchestrator

**Purpose:** Manages Wazuh dashboard access via SSM port forwarding

**Responsibilities:**
- Verify SSM connectivity
- Monitor dashboard service health
- Open port-forwarding tunnel
- Provide tunnel status information

**Usage:** `cloud-soc dashboard` command

### Methods

#### `open_tunnel(terraform_outputs: Dict, local_port: int, remote_port: int) -> None`
Opens an SSM port-forwarding tunnel to the Wazuh dashboard.

Parameters:
- `terraform_outputs`: Dictionary from `TerraformOrchestrator.output()`
- `local_port`: Local port for port forwarding (default: 8443)
- `remote_port`: Remote dashboard port (default: 443)

```python
dashboard = DashboardOrchestrator()
dashboard.open_tunnel(
    terraform_outputs,
    local_port=8443,
    remote_port=443
)
```

### Example: Access Dashboard

```python
from cloudsoc.orchestrator import TerraformOrchestrator, DashboardOrchestrator

# Get infrastructure outputs
tf = TerraformOrchestrator()
outputs = tf.output()

# Open tunnel
dashboard = DashboardOrchestrator()
dashboard.open_tunnel(outputs, local_port=8443)

# User opens: https://127.0.0.1:8443 in browser
```

## CLI Command Mapping

### `cloud-soc apply`
Maps to: `TerraformOrchestrator`
```
apply() -> {
    init()
    import_all_existing_resources()
    validate()
    plan()
    apply()
}
```

### `cloud-soc deploy [targets]`
Maps to: `DeploymentOrchestrator`
```
deploy(targets) -> {
    wait_for_ssm_ready()
    deploy_targets(targets)
    validate_deployment()
}
```

### `cloud-soc dashboard`
Maps to: `DashboardOrchestrator`
```
dashboard() -> {
    open_tunnel()
}
```

## Workflow Examples

### Example 1: Simple Deployment

```bash
# Infrastructure
cloud-soc apply --auto-approve

# Deploy all services
cloud-soc deploy

# Access dashboard
cloud-soc dashboard
```

### Example 2: Partial Deployment

Deploy only Wazuh manager (e.g., for testing):

```bash
# Infrastructure
cloud-soc apply --auto-approve

# Deploy only Wazuh
cloud-soc deploy wazuh

# Skip victim deployment
```

### Example 3: Programmatic Control

```python
from cloudsoc.orchestrator import (
    TerraformOrchestrator,
    DeploymentOrchestrator
)

tf = TerraformOrchestrator()
deployment = DeploymentOrchestrator()

# 1. Provision infrastructure
tf.init()
tf.validate()
plan = tf.plan()
tf.apply(plan_file=plan, auto_approve=True)

# 2. Get outputs
outputs = tf.output()

# 3. Wait for instances
instances = [
    outputs["wazuh_instance_id"]["value"],
    outputs["victim_instance_id"]["value"]
]
deployment.wait_for_ssm_ready(instances, timeout=300)

# 4. Deploy Wazuh first
deployment.deploy_targets(outputs, targets=["wazuh"])

# 5. Deploy victim
deployment.deploy_targets(outputs, targets=["victim"])

# 6. Validate
deployment.validate_deployment(outputs)
```

### Example 4: Retry Failed Deployment

If deployment fails, retry without reprovisioning:

```bash
# First attempt (fails)
cloud-soc deploy

# Check logs, fix issues...

# Retry (infrastructure already exists!)
cloud-soc deploy wazuh  # Retry just Wazuh
```

## Future Scalability

### Adding New Deployment Targets

To add a new deployment target (e.g., `grafana`):

1. Create deployment YAML: `deployment/grafana/install.yml`
2. Use CLI: `cloud-soc deploy grafana`

No CLI code changes needed!

```bash
# New targets automatically discovered from deployment/ directory
cloud-soc deploy soc-api
cloud-soc deploy elasticsearch
cloud-soc deploy attacker
cloud-soc deploy windows-victim
```

### Adding New Orchestrators

To add new orchestrators for other tasks:

```python
class MonitoringOrchestrator:
    """Manages monitoring setup"""
    def setup_prometheus(self):
        pass
    def setup_grafana(self):
        pass

class BackupOrchestrator:
    """Manages backup operations"""
    def backup_to_s3(self):
        pass
```

Then map to CLI:
```bash
cloud-soc monitoring setup
cloud-soc backup create
```

## Error Handling

### Failure Attribution

**Before (Monolithic):**
```
cloud-soc apply FAILED
❌ Infrastructure or deployment failed (unclear!)
```

**After (Split Architecture):**
```
cloud-soc apply FAILED
❌ Terraform apply failed (clear!)

OR

cloud-soc deploy FAILED
❌ Deployment failed (clear!)
```

### Recovery Strategies

| Failure | Recovery |
|---------|----------|
| `apply` fails at validate | Fix config, retry `apply` |
| `apply` fails at plan | Fix config, retry `apply` |
| `deploy` fails at SSM | Wait for instances, retry `deploy` |
| `deploy` fails at wazuh deployment | Fix deployment YAML, retry `deploy wazuh` |
| `deploy` fails at victim deployment | Fix deployment YAML, retry `deploy victim` |

## Integration Points

### External Services

```
TerraformOrchestrator
  ├─ TerraformRunner (Terraform CLI wrapper)
  ├─ ResourceImporter (AWS resource import)
  └─ Settings (configuration)

DeploymentOrchestrator
  ├─ SSMService (AWS Systems Manager)
  ├─ DeploymentService (YAML execution)
  └─ Settings (configuration)

DashboardOrchestrator
  ├─ SSMService (AWS Systems Manager)
  └─ Settings (configuration)
```

### Configuration

All orchestrators use `cloudsoc.config.settings.get_settings()`:

```python
from cloudsoc.config.settings import get_settings

settings = get_settings()

# Configure region, profile, credentials
settings.project.aws.region
settings.project.aws.profile
settings.project.terraform.dir
```

## Testing

### Unit Tests

```python
from unittest.mock import Mock, patch
from cloudsoc.orchestrator import TerraformOrchestrator

def test_terraform_apply():
    with patch('cloudsoc.orchestrator.TerraformRunner') as mock_tf:
        tf = TerraformOrchestrator()
        tf.apply(plan_file="test.plan", auto_approve=True)
        mock_tf.apply.assert_called_once()
```

### Integration Tests

```python
def test_full_deployment():
    tf = TerraformOrchestrator()
    deployment = DeploymentOrchestrator()
    
    # This will make real AWS calls
    outputs = tf.output()
    assert "wazuh_instance_id" in outputs
```

## Performance Considerations

### Timeouts

- SSM readiness check: 600s default (10 minutes)
- Dashboard service check: 90s default
- Terraform apply: No timeout (runs to completion)

### Parallelization

Currently, operations are sequential:
```
terraform init
terraform validate
terraform plan
terraform apply
  ↓
wait for SSM (both instances in parallel internally)
  ↓
deploy wazuh
deploy victim (sequential, could be parallel in future)
```

### Caching

Terraform outputs are cached locally in `.terraform/` directory.

## Best Practices

1. **Always validate before applying:**
   ```bash
   cloud-soc validate
   ```

2. **Use auto-approve carefully:**
   ```bash
   # Only in CI/CD with approval gates
   cloud-soc apply --auto-approve
   ```

3. **Check status before deployment:**
   ```bash
   cloud-soc status
   ```

4. **Deploy incrementally:**
   ```bash
   cloud-soc deploy wazuh     # Deploy Wazuh first
   cloud-soc status           # Verify
   cloud-soc deploy victim    # Then victim
   ```

5. **Keep orchestrators independent:**
   - Don't combine orchestrator operations
   - Each command should succeed independently

## Troubleshooting

### Terraform Apply Fails

```bash
cloud-soc apply

# Check error output
# Fix Terraform configuration
# Retry
cloud-soc apply --auto-approve
```

### Deployment Fails

```bash
cloud-soc deploy

# Check SSM agent logs on instance
# Fix deployment YAML
# Retry specific target
cloud-soc deploy wazuh
```

### Dashboard Fails to Open

```bash
# Check instance is running
cloud-soc status

# Check SSM connectivity
cloud-soc deploy --skip-validation

# Try dashboard again
cloud-soc dashboard
```

See [Troubleshooting Guide](../troubleshooting/README.md) for more details.
