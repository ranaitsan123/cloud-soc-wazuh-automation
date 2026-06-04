# Guides

This section contains step-by-step guides for key workflows in the project.

## Contents

- [Custom YAML Deployment Guide](deployment/README.md) - Deploy services to instances using custom YAML

## Purpose

Use this section to:

- Deploy infrastructure with `cloud-soc apply`
- Deploy services with `cloud-soc deploy`
- Configure custom YAML deployments
- Follow step-by-step instructions
- Implement operational tasks

## Quick Reference

### Two-Stage Deployment Workflow

```bash
# Stage 1: Infrastructure (Terraform only)
cloud-soc apply --auto-approve

# Wait for instances to boot
sleep 30

# Stage 2: Deployment (SSM + YAML playbooks)
cloud-soc deploy

# Check deployment progress
cloud-soc deployment status

# Inspect active SSM sessions
cloud-soc ssm sessions

# Access dashboard
cloud-soc dashboard
```

### Deploy Individual Services

```bash
# Deploy only Wazuh manager
cloud-soc deploy wazuh

# Deploy only victim server
cloud-soc deploy victim

# Deploy multiple targets
cloud-soc deploy wazuh victim
```

## Recommended Workflow

1. **Read Getting Started** - [Quick Start Guide](../1-getting-started/02-quick-start.md)
2. **Deploy Infrastructure** - `cloud-soc apply`
3. **Deploy Services** - `cloud-soc deploy`
4. **Use Deployment Guide** - [Custom YAML Deployment](deployment/deploy-wazuh.md)
5. **Reference Architecture** - [Orchestrator Architecture](../3-reference/orchestrator-architecture.md)
6. **Troubleshoot Issues** - [Troubleshooting Guide](../troubleshooting/README.md)

## Why Two Commands?

The separation of `apply` and `deploy` provides several benefits:

- **Clear failure attribution** - Know exactly what failed (infrastructure vs deployment)
- **Independent operations** - Retry failed stages without reprovisioning
- **Better diagnostics** - Each stage has focused output and logging
- **Flexible deployments** - Deploy individual services independently
- **Scalable architecture** - Easy to add new deployment targets

See [Orchestrator Architecture](../3-reference/orchestrator-architecture.md) for technical details.
