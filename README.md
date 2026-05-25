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

> **Branch-specific README:** This document is oriented to the `refactor/python-orchestrator` branch and describes the Python-based orchestration platform implemented in this branch.

---

## 🚀 Branch Overview

This branch refactors the repository around a **Python orchestration platform** for AWS infrastructure and Wazuh SOC deployment.

Key goals:

- Replace legacy Bash orchestration with a typed Python CLI
- Use **Typer** for CLI command handling
- Wrap Terraform with `cloudsoc/terraform/runner.py`
- Use **Boto3** service wrappers for AWS discovery
- Generate Ansible inventory for **SSM-driven** configuration
- Support safe AWS resource import into Terraform state
- Provide a unified entrypoint: `cloud-soc`

## 📌 What This Branch Contains

- `cloudsoc/main.py` — Typer CLI entrypoint
- `cloudsoc/orchestrator.py` — deployment orchestration and dashboard helpers
- `cloudsoc/terraform/runner.py` — Terraform wrapper and state management
- `cloudsoc/terraform/imports.py` — automatic AWS resource discovery/import
- `cloudsoc/aws/` — wrappers for EC2, IAM, S3, ECR, SSM
- `cloudsoc/ansible/deploy.py` — Ansible orchestration support
- `cloudsoc/cleanup/services.py` — cleanup helpers for VPC and networking
- `cloudsoc/config/settings.py` — `.env` configuration management
- `terraform/` — infrastructure-as-code definitions
- `ansible/` — runtime service configuration playbooks
- `docs/` — branch-aligned documentation

## ✅ Branch Key Features

- **Python CLI Orchestration**: all deploy actions use `cloud-soc`
- **Terraform automation**: init, validate, plan, apply, destroy
- **Safe resource import**: existing AWS resources are detected and imported before apply
- **Infrastructure status**: `cloud-soc status` reports VPC/subnet/instance details
- **SSM dashboard access**: `cloud-soc dashboard`
- **Dynamic Ansible inventory**: generated from EC2 discovery
- **Unified branch docs**: docs are aligned with this refactor branch

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

## 🧪 Use the Python Orchestrator CLI

### CLI entrypoint

```bash
cloud-soc --help
```

### Important commands

```bash
cloud-soc status
cloud-soc validate
cloud-soc apply
cloud-soc destroy
cloud-soc dashboard
cloud-soc import aws_vpc.wazuh_vpc vpc-0123456789abcdef0
cloud-soc version
```

### Apply infrastructure

```bash
cloud-soc apply
```

```bash
cloud-soc apply --auto-approve
```

```bash
cloud-soc apply --var-file prod.tfvars
```

### Destroy infrastructure

```bash
cloud-soc destroy
```

```bash
cloud-soc destroy --auto-approve --force
```

### Dashboard access via SSM

```bash
cloud-soc dashboard
```

Then open:

```bash
https://127.0.0.1:8443
```

### Import an existing AWS resource

```bash
cloud-soc import aws_vpc.wazuh_vpc vpc-0123456789abcdef0
```

## 💡 Branch-Specific Workflow

This branch is intended to be consumed through the Python orchestrator rather than raw Terraform or shell scripts.

### Orchestrator flow

1. `cloud-soc apply`
2. Terraform init + optional AWS resource import
3. Terraform validate + plan + apply
4. Wait for SSM connectivity
5. Generate Ansible inventory from EC2 instances
6. Execute Ansible playbooks against target hosts
7. Print dashboard access instructions

### Platform behavior

- Terraform operations are handled by `TerraformRunner`
- AWS discovery is handled by Boto3 service classes
- Wazuh configuration is deployed via Ansible on private instances
- Dashboard access uses SSM port forwarding via AWS CLI
- Existing resources can be reused safely

## 🧱 Important Branch Files

| Path | Description |
|---|---|
| `cloudsoc/main.py` | CLI command definitions |
| `cloudsoc/orchestrator.py` | Deployment orchestration logic |
| `cloudsoc/terraform/runner.py` | Terraform command wrapper |
| `cloudsoc/terraform/imports.py` | Safe AWS resource import logic |
| `cloudsoc/aws/ec2.py` | EC2 discovery and helpers |
| `cloudsoc/aws/iam.py` | IAM management helpers |
| `cloudsoc/aws/ssm.py` | SSM session and command helpers |
| `cloudsoc/ansible/deploy.py` | Ansible execution support |
| `cloudsoc/config/settings.py` | Environment and settings loader |
| `ansible/playbooks/` | Service deployment playbooks |
| `terraform/` | Infrastructure-as-code definitions |
| `docs/` | Branch-specific documentation |

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
cloud-soc apply
```

## 🔍 Developer Notes

### Package entrypoint

The command is installed from `pyproject.toml`:

```toml
[project.scripts]
cloud-soc = "cloudsoc.main:app"
```

### Dependencies

- `typer>=0.9.0`
- `rich>=13.0.0`
- `boto3>=1.26.0`
- `pydantic>=2.0.0`
- `python-dotenv>=1.0.0`
- `pyyaml>=6.0`
- `ansible-core>=2.14.0`

### Tests

```bash
pytest cloudsoc/tests/
```

## 📘 Branch Documentation

- `docs/README.md` — branch docs hub
- `docs/1-getting-started/02-quick-start.md`
- `docs/2-guides/ansible/deploy-wazuh.md`
- `docs/2-guides/ansible/refactor-plan.md`
- `docs/4-explanation/python-migration-guide.md`
- `QUICKSTART.md`
- `MIGRATION_GUIDE.md`
- `QUICK_REFERENCE.md`

## ⚠️ Notes

- This README is intentionally branch-specific for `refactor/python-orchestrator`.
- Use `cloud-soc` as the primary entrypoint.
- Avoid direct Terraform CLI use unless you understand the branch-specific orchestration model.
- Existing AWS resources are imported into state automatically when possible.

## 📌 Summary

This branch is the Python-first orchestration path for Cloud SOC. The core workflow is:

- `cloud-soc apply` → provision infrastructure and run Ansible
- `cloud-soc status` → inspect deployed AWS resources
- `cloud-soc dashboard` → access Wazuh via SSM
- `cloud-soc destroy` → clean up infrastructure

For branch-specific documentation, use `docs/README.md`.