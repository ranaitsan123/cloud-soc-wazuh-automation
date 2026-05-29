# Deploy Wazuh with Custom YAML

## Overview

This document describes the custom YAML-based deployment workflow used to configure Wazuh Manager and the victim instance after Terraform provisioning.

## How it works

### 1. Terraform provisions infrastructure

Terraform deploys:

- VPC and private subnets
- NAT gateway
- EC2 instances with IAM instance profiles
- S3 bucket for assets
- ECR repositories for container images

### 2. Bootstrap on EC2 instances

Each instance is bootstrapped with:

- `amazon-ssm-agent`
- Python 3 and `pip`
- Docker and Docker Compose
- AWS CLI

### 3. Post-apply Custom YAML Deployment

The orchestration workflow executes custom YAML deployment files to configure services on remote instances via AWS SSM.

The following deployment plans are applied:

- `deployment/wazuh_manager.yml` - Wazuh Manager configuration
- `deployment/victim_server.yml` - Victim server configuration

Each YAML file defines a series of tasks that are executed sequentially on the target instance.

## Deployment flow

1. Run `cloud-soc apply` to provision infrastructure.
2. Wait for instances to be reachable through SSM.
3. Execute custom YAML deployments via the orchestrator.
4. Wazuh Manager and victim services are configured and started.

## Understanding Deployment YAML Files

### Task Types

The custom YAML deployment system supports the following task types:

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

Example task:

```yaml
- name: Install prerequisites
  type: package
  packages:
    - apt-transport-https
    - ca-certificates
    - curl
```

### Variable Substitution

Deployment files support variable substitution using the `{{ variable_name }}` syntax:

```yaml
- name: Configure Wazuh agent
  type: shell
  cmd: |
    sudo sed -i 's/MANAGER_IP/{{ wazuh_manager_ip }}/g' /etc/wazuh/agent.conf
```

Variables are passed from the orchestrator based on Terraform outputs.

## Wazuh Manager Deployment

The `deployment/wazuh_manager.yml` file handles:

1. Install Docker and prerequisites
2. Create Wazuh configuration directories
3. Download Wazuh configuration files from S3
4. Generate SSL certificates if needed
5. Start Wazuh services with Docker Compose

## Victim Server Deployment

The `deployment/victim_server.yml` file handles:

1. Install Docker and prerequisites
2. Install Wazuh agent
3. Configure Wazuh agent to connect to the manager
4. Login to ECR and pull the victim container image
5. Run the victim container

## Accessing the Wazuh Dashboard

The Wazuh dashboard is private inside the VPC. Use the CLI helper to forward the port:

```bash
cloud-soc dashboard
```

Then open:

```bash
https://127.0.0.1:8443
```

## Running Tasks via SSM

The recommended workflow is to use the custom YAML deployment system which handles task execution transparently via AWS SSM. This provides:

- secure remote execution without SSH access
- consistent task definitions across environments
- easy task composition and ordering
- built-in error handling and logging

## Notes

- Terraform remains responsible for infrastructure.
- Custom YAML deployments handle service configuration and runtime deployment.
- SSM enables a secure remote control plane for private instances.
- Unlike Ansible, this lightweight system has no external dependencies on target systems.
