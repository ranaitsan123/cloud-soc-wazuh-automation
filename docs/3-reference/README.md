# Reference

This section contains technical reference material for the Cloud SOC project.

## Contents

- [Orchestrator Architecture](orchestrator-architecture.md) - Technical details of the orchestration layer
- [Terraform Reference](terraform/README.md) - Terraform configuration and state management
- [IAM Permissions](iam-permissions.md) - Security and permission models

## Purpose

Use this section to:

- understand the orchestrator architecture and class design
- look up infrastructure and deployment details
- review security and permission models
- understand project-specific Terraform workflows
- reference API documentation for orchestrators

## Key Documents

### Orchestrator Architecture

Explains the three-tier orchestration system:

- **TerraformOrchestrator** - Infrastructure lifecycle (init, validate, plan, apply, destroy)
- **DeploymentOrchestrator** - Service deployment (SSM, YAML, validation)
- **DashboardOrchestrator** - Dashboard access (SSM tunneling)

See [Orchestrator Architecture](orchestrator-architecture.md) for:
- Class APIs and methods
- Workflow examples
- Integration points
- Error handling strategies
- Future scalability patterns

### Terraform Reference

Infrastructure as Code documentation including:
- Resource definitions
- State management
- Import procedures
- Deployment checklists

### IAM Permissions

Security model including:
- Role-based access control
- Service permissions
- Policy documents
- Best practices

## CLI Command Mapping

| Command | Component | Purpose |
|---------|-----------|---------|
| `cloud-soc apply` | TerraformOrchestrator | Provision infrastructure (Terraform only) |
| `cloud-soc deploy` | DeploymentOrchestrator | Deploy services (SSM + YAML) |
| `cloud-soc dashboard` | DashboardOrchestrator | Open dashboard tunnel |
| `cloud-soc status` | EC2Service | Check infrastructure status |
| `cloud-soc validate` | TerraformRunner | Validate configuration |
| `cloud-soc destroy` | TerraformRunner | Destroy infrastructure |

## Architecture Overview

```
┌──────────────────────────────────┐
│      CLI Commands                │
│  (main.py - Typer CLI)           │
└───────┬──────────────┬───────────┘
        │              │
        v              v
    ┌─────────────────────────────────┐
    │    Orchestrators                 │
    │  (orchestrator.py)               │
    ├─ TerraformOrchestrator          │
    ├─ DeploymentOrchestrator         │
    └─ DashboardOrchestrator          │
        │
        v
    ┌─────────────────────────────────┐
    │    AWS Services                  │
    │  (aws/ directory)                │
    ├─ TerraformRunner (terraform/)   │
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

## Getting Started with References

1. **New to orchestrators?** Start with [Quick Start Guide](../1-getting-started/02-quick-start.md)
2. **Need API details?** See [Orchestrator Architecture](orchestrator-architecture.md)
3. **Deployment questions?** Check [Deployment Guide](../2-guides/deployment/deploy-wazuh.md)
4. **Infrastructure setup?** Review [Terraform Reference](terraform/README.md)
5. **Security concerns?** Consult [IAM Permissions](iam-permissions.md)
