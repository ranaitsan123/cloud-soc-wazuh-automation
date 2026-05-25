# Deploy Wazuh with Ansible

## Overview

This document describes the Ansible-based deployment workflow used to configure Wazuh Manager and the victim instance after Terraform provisioning.

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
- Ansible

### 3. Post-apply Ansible configuration

The orchestration workflow uses AWS SSM to execute Ansible playbooks remotely.

The following playbooks are applied:

- `ansible/playbooks/bootstrap.yml`
- `ansible/playbooks/wazuh_manager.yml`
- `ansible/playbooks/victim_server.yml`

### 4. What changed in the Ansible roles

- `ansible/roles/wazuh_manager` now downloads Wazuh configuration artifacts from S3 using `amazon.aws.aws_s3`, making the role idempotent and ensuring updated config is reapplied.
- `ansible/roles/victim_server` now uses a proper Wazuh agent manager address update flow and keeps a managed Docker container for the victim image instead of using `tail -f /dev/null`.
- The repository now declares `community.docker` in `ansible/requirements.yml` so container lifecycle and Compose management are handled through Ansible modules rather than shell wrappers.

## Deployment flow

1. Run `cloud-soc apply` to provision infrastructure.
2. Wait for instances to be reachable through SSM.
3. Execute Ansible playbooks via the orchestrator.
4. Wazuh Manager and victim services are configured and started.

The bootstrap playbook installs common host prerequisites before the service-specific roles run.

Remote execution is orchestrated from the Python layer. The orchestrator generates an SSM-based inventory file and runs playbooks against remote host groups (`wazuh` and `victims`) instead of using `localhost` as inventory.

## Deployment flow

1. Run `cloud-soc apply` to provision infrastructure.
2. Wait for instances to be reachable through SSM.
3. Execute Ansible playbooks via the orchestrator.
4. Wazuh Manager and victim services are configured and started.

## Accessing the Wazuh Dashboard

The Wazuh dashboard is private inside the VPC. Use the CLI helper to forward the port:

```bash
cloud-soc dashboard
```

Then open:

```bash
https://127.0.0.1:8443
```

## Atomic Red Team and SSM

The recommended workflow is to run attack simulation tasks through Ansible executed over SSM. This avoids direct SSH access and keeps the deployment secure.

## Notes

- Terraform remains responsible for infrastructure.
- Ansible handles service configuration and runtime deployment.
- SSM enables a secure remote control plane for private instances.
