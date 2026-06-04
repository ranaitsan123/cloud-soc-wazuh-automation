# ☁️ Cloud SOC – Wazuh Threat Detection & Python Orchestrator

<div align="center">

![GitHub License](https://img.shields.io/github/license/ranaitsan123/cloud-soc-wazuh-automation?style=flat-square)
![GitHub Stars](https://img.shields.io/github/stars/ranaitsan123/cloud-soc-wazuh-automation?style=flat-square)
![Terraform](https://img.shields.io/badge/Terraform-%3E%3D1.0-blueviolet?style=flat-square&logo=terraform)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker)
![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-Enabled-orange?style=flat-square&logo=amazonaws)
![Status](https://img.shields.io/github/workflow/status/ranaitsan123/cloud-soc-wazuh-automation/refactor/python-orchestrator?style=flat-square)

</div>

> **Branch-specific README:** This document describes the `refactor/python-orchestrator-v2` branch with a **two-stage orchestration platform** for AWS infrastructure and Wazuh SOC deployment.

---

## 🚀 Branch Overview

This branch implements a **Python-first orchestration platform** with clear separation between infrastructure provisioning and service deployment.

### Key Architecture

- **Stage 1 - Infrastructure** (`cloud-soc apply`): Terraform-based AWS provisioning only
- **Stage 2 - Deployment** (`cloud-soc deploy`): Service configuration via SSM and custom YAML

### Goals

- Replace legacy monolithic orchestration with focused Python orchestrators
- Use **Typer** for CLI command handling
- Wrap Terraform with `cloudsoc/terraform/runner.py`
- Use **Boto3** service wrappers for AWS discovery
- Custom YAML-based deployment orchestration via **SSM**
- Support safe AWS resource import into Terraform state
- Provide unified entrypoint: `cloud-soc`
- **Clear failure attribution**: Know exactly what failed
- **Independent operations**: Retry stages without reprovisioning
- **Future scalability**: Easy to add new deployment targets

## 📌 What This Branch Contains

### Orchestration System

- `cloudsoc/main.py` — Typer CLI entrypoint with command definitions
- `cloudsoc/orchestrator.py` — **Three focused orchestrator classes:**
  - `TerraformOrchestrator` — Infrastructure lifecycle (init, validate, plan, apply, destroy)
  - `DeploymentOrchestrator` — Service deployment and SSM management
  - `DashboardOrchestrator` — Dashboard access via SSM tunneling

### Infrastructure & AWS Integration

- `cloudsoc/terraform/runner.py` — Terraform wrapper and state management
- `cloudsoc/terraform/imports.py` — automatic AWS resource discovery/import
- `cloudsoc/aws/` — Boto3 service wrappers (EC2, IAM, S3, ECR, SSM)
- `cloudsoc/deployment/executor.py` — Custom YAML deployment service
- `cloudsoc/cleanup/services.py` — VPC and networking cleanup helpers
- `cloudsoc/config/settings.py` — `.env` configuration management

### Infrastructure & Deployment

- `terraform/` — infrastructure-as-code definitions
- `deployment/` — custom YAML deployment configurations
- `docs/` — comprehensive branch-aligned documentation

## ✅ Branch Key Features

### Two-Stage Workflow

```bash
# Stage 1: Infrastructure only (Terraform)
cloud-soc apply --auto-approve

# Stage 2: Services only (SSM + Deployments)
cloud-soc deploy

# Access dashboard
cloud-soc dashboard
```

### Core Features

- **Python CLI Orchestration**: All deploy actions use `cloud-soc` command
- **Terraform automation**: init, validate, plan, apply, destroy
- **Safe resource import**: Existing AWS resources detected and imported
- **Infrastructure status**: `cloud-soc status` reports VPC/subnet/instance details
- **SSM dashboard access**: `cloud-soc dashboard` with port forwarding
- **Target-based deployments**: Deploy individual services independently
  - `cloud-soc deploy` — Deploy all services
  - `cloud-soc deploy wazuh` — Deploy only Wazuh
  - `cloud-soc deploy victim` — Deploy only victim
- **Custom YAML deployments**: Lightweight configuration without Ansible
- **Independent retry**: Redeploy services without infrastructure changes
- **Future-ready**: Easy to add new deployment targets

## 🔧 Installation

```bash
cd /workspaces/cloud-soc-wazuh-automation
cp .env.example .env
# Edit .env with AWS credentials and region

pip install -e .
```

### Environment variables in `.env`

Required variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `PROJECT_TAG=cloud-soc`

## 🧪 Quick Start

### CLI entrypoint

```bash
cloud-soc --help
```

### Common Commands

#### Infrastructure & Status

```bash
# Check current state
cloud-soc status

# Validate configuration
cloud-soc validate

# Provision infrastructure (Terraform only)
cloud-soc apply --auto-approve

# Destroy infrastructure
cloud-soc destroy --auto-approve --force
```

#### Deployment

```bash
# Deploy all services
cloud-soc deploy

# Deploy specific services
cloud-soc deploy wazuh
cloud-soc deploy victim
cloud-soc deploy wazuh victim

# Skip validation
cloud-soc deploy --skip-validation
```

#### Access & Management

```bash
# Open Wazuh dashboard via SSM tunnel
cloud-soc dashboard

# Check deployment progress
cloud-soc deployment status

# List active SSM sessions and agent health
cloud-soc ssm sessions

# Import existing AWS resource
cloud-soc import aws_vpc.wazuh_vpc vpc-0123456789abcdef0

# Show version
cloud-soc version
```

## 💡 Typical Workflow

### Step-by-step deployment

```bash
# 1. Provision infrastructure (15-20 minutes)
cloud-soc apply --auto-approve

# 2. Wait for instances to boot
sleep 30

# 3. Deploy services (10-15 minutes)
cloud-soc deploy

# 4. Check deployment status
cloud-soc deployment status

# 5. (Optional) Inspect active SSM sessions
cloud-soc ssm sessions

# 6. Access dashboard
cloud-soc dashboard

# Open in browser: https://127.0.0.1:8443

# 6. Cleanup when done
cloud-soc destroy --auto-approve --force
```

### Deployment with individual targets

```bash
# Deploy infrastructure
cloud-soc apply --auto-approve

# Deploy Wazuh first
cloud-soc deploy wazuh

# Verify and then deploy victim
cloud-soc deploy victim
```

### Fix and retry (without reprovisioning)

```bash
# Initial deployment fails
cloud-soc deploy

# Fix deployment YAML or check logs...

# Retry only the failed service
cloud-soc deploy wazuh  # Infrastructure still exists!
```

## 🏗️ Architecture

### Three-Tier Orchestration

```
┌──────────────────────────────────┐
│      CLI Commands (Typer)        │
│  apply | deploy | dashboard      │
└───────┬──────────────┬───────────┘
        │              │
        v              v
    ┌─────────────────────────────────┐
    │    Orchestrators                 │
    │  (cloudsoc/orchestrator.py)      │
    ├─ TerraformOrchestrator          │
    ├─ DeploymentOrchestrator         │
    └─ DashboardOrchestrator          │
        │
        v
    ┌─────────────────────────────────┐
    │    AWS Services                  │
    │  (cloudsoc/aws/)                 │
    ├─ TerraformRunner                │
    ├─ SSMService                     │
    ├─ DeploymentService              │
    └─ EC2Service                     │
        │
        v
    ┌─────────────────────────────────┐
    │    AWS Resources                 │
    │  (EC2, SSM, S3, IAM, etc.)      │
    └─────────────────────────────────┘
```

### Command Mapping

| Command | Orchestrator | Purpose |
|---------|--------------|---------|
| `cloud-soc apply` | TerraformOrchestrator | Provision AWS infrastructure |
| `cloud-soc deploy [targets]` | DeploymentOrchestrator | Deploy services via SSM |
| `cloud-soc dashboard` | DashboardOrchestrator | Access Wazuh dashboard |
| `cloud-soc deployment status` | DeploymentOrchestrator | Show latest deployment status |
| `cloud-soc ssm sessions` | SSMService | List active SSM sessions |
| `cloud-soc status` | EC2Service | Show infrastructure status |
| `cloud-soc validate` | TerraformRunner | Validate configuration |
| `cloud-soc destroy` | TerraformRunner | Destroy infrastructure |

## 🧱 Important Branch Files

| Path | Description |
|---|---|
| `cloudsoc/main.py` | CLI command definitions (Typer) |
| `cloudsoc/orchestrator.py` | **Three orchestrator classes** (refactored) |
| `cloudsoc/terraform/runner.py` | Terraform command wrapper |
| `cloudsoc/terraform/imports.py` | Safe AWS resource import logic |
| `cloudsoc/aws/ec2.py` | EC2 discovery and helpers |
| `cloudsoc/aws/iam.py` | IAM management helpers |
| `cloudsoc/aws/ssm.py` | SSM session and command helpers |
| `cloudsoc/deployment/executor.py` | Custom YAML deployment service |
| `cloudsoc/config/settings.py` | Environment and settings loader |
| `deployment/` | Custom YAML deployment configurations |
| `terraform/` | Infrastructure-as-code definitions |
| `docs/` | Comprehensive branch documentation |

## 📚 Documentation

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute setup
- **[docs/1-getting-started/02-quick-start.md](docs/1-getting-started/02-quick-start.md)** — Detailed quick start

### Guides

- **[docs/2-guides/deployment/deploy-wazuh.md](docs/2-guides/deployment/deploy-wazuh.md)** — Complete deployment guide
- **[docs/2-guides/deployment/README.md](docs/2-guides/deployment/README.md)** — Deployment overview

### Reference

- **[docs/3-reference/orchestrator-architecture.md](docs/3-reference/orchestrator-architecture.md)** — Technical architecture and API reference
- **[docs/3-reference/README.md](docs/3-reference/README.md)** — Reference documentation hub
- **[docs/3-reference/iam-permissions.md](docs/3-reference/iam-permissions.md)** — IAM security model

### Other

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** — Migrating from old branches
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Quick command reference
- **[docs/README.md](docs/README.md)** — Documentation hub

## 🧰 Recommended Local Workflow

### Using Docker Compose

```bash
docker-compose up -d devops
docker-compose exec devops bash
cloud-soc status
```

### Direct host usage

```bash
pip install -e .
cloud-soc validate
cloud-soc apply --auto-approve
cloud-soc deploy
cloud-soc status
```

## 💻 Python API

### Infrastructure Provisioning

```python
from cloudsoc.orchestrator import TerraformOrchestrator

tf = TerraformOrchestrator()
tf.init()
tf.validate()
plan = tf.plan()
tf.apply(plan_file=plan, auto_approve=True)
outputs = tf.output()
```

### Service Deployment

```python
from cloudsoc.orchestrator import DeploymentOrchestrator

deployment = DeploymentOrchestrator()

# Wait for instances
deployment.wait_for_ssm_ready([instance_id])

# Deploy services
deployment.deploy_targets(outputs, targets=["wazuh"])

# Validate
deployment.validate_deployment(outputs)
```

### Dashboard Access

```python
from cloudsoc.orchestrator import DashboardOrchestrator

dashboard = DashboardOrchestrator()
dashboard.open_tunnel(outputs, local_port=8443)
```

See [Orchestrator Architecture](docs/3-reference/orchestrator-architecture.md) for complete API reference.

## 🔍 Developer Notes

### Package entrypoint

The command is installed from `pyproject.toml`:

```toml
[project.scripts]
cloud-soc = "cloudsoc.main:app"
```

### Dependencies

- `typer>=0.9.0` — CLI framework
- `rich>=13.0.0` — Terminal formatting
- `boto3>=1.26.0` — AWS SDK
- `pydantic>=2.0.0` — Configuration validation
- `python-dotenv>=1.0.0` — Environment management
- `pyyaml>=6.0` — YAML deployment parsing

### Tests

```bash
pytest cloudsoc/tests/
```

## ⚠️ Key Points

### Why Two Stages?

The `apply` and `deploy` split provides:

- ✅ **Clear failure attribution** — Know exactly what failed
- ✅ **Independent operations** — Retry failed stages without reprovisioning
- ✅ **Better diagnostics** — Focused logging for each stage
- ✅ **Flexible deployments** — Deploy services independently
- ✅ **Future scalability** — Easy to add new deployment targets

### Design Principles

1. **Separation of Concerns** — Each orchestrator has a single responsibility
2. **Target-Based** — Deploy any service independently
3. **SSM-Focused** — Secure remote execution without SSH
4. **Terraform-Wrapped** — Never use raw Terraform CLI directly
5. **Composable** — Orchestrators work independently

### Important Notes

- This README is intentionally branch-specific for `refactor/python-orchestrator-v2`
- Use `cloud-soc` as the primary entrypoint
- Avoid direct Terraform CLI use unless you understand the orchestration model
- Existing AWS resources are imported into state automatically when possible
- All deployment operations use custom YAML (no Ansible required)

## 📌 Summary

This branch is the **Python-first, two-stage orchestration** path for Cloud SOC.

### Core Workflow

```bash
cloud-soc apply      # → Infrastructure provisioning (Terraform)
cloud-soc deploy     # → Service configuration (SSM + YAML)
cloud-soc dashboard  # → Dashboard access (SSM tunnel)
cloud-soc destroy    # → Infrastructure cleanup
```

### Key Advantages

- **Monolithic → Modular**: Three focused orchestrator classes
- **Unclear states → Clear states**: Infrastructure vs deployment failures are distinct
- **All-or-nothing → Flexible**: Deploy individual services independently
- **Hard to debug → Easy to debug**: Isolated failure points
- **Hard to scale → Easy to scale**: Add new targets without code changes

For comprehensive documentation, start with [QUICKSTART.md](QUICKSTART.md) or [docs/README.md](docs/README.md).