# Ansible Refactor Plan

## Purpose

This document captures the Ansible refactor plan for the Cloud SOC project. It defines the problems, goals, and a concrete set of changes required to stabilize the Ansible orchestration layer.

## Problem statement

The current Ansible workflow is brittle because it mixes three separate concerns:

- infrastructure provisioning
- runtime bootstrap of EC2 hosts
- service configuration via Ansible

The result is a fragile deployment path that can fail when:

- an inventory is not explicit
- Ansible collections are missing or installed silently
- remote hosts are not bootstrapped consistently
- playbooks rely on host prerequisites that may not exist
- inventory and variable outputs are not aligned

## Goals

1. Make Ansible orchestration explicit and deterministic.
2. Separate EC2 bootstrap from application configuration.
3. Use generated remote inventory consistently.
4. Fail fast when Ansible dependencies are missing.
5. Document the new deployment flow clearly for operators.

## Proposed structure

### File layout

- `ansible/ansible.cfg`
  - central root configuration
  - explicit roles path
  - no default `inventory = localhost`

- `ansible/playbooks/bootstrap.yml`
  - install OS prerequisites, Docker, AWS CLI, and SSM requirements
  - validate remote host readiness

- `ansible/playbooks/wazuh_manager.yml`
  - target `hosts: wazuh`
  - configure Wazuh Manager runtime services

- `ansible/playbooks/victim_server.yml`
  - target `hosts: victims`
  - configure the victim workload and ECR image pull

- `ansible/roles/` remains the role repository for service tasks.

- `docs/2-guides/ansible/refactor-plan.md`
  - this plan and implementation checklist

### Orchestration updates

- `cloudsoc/ansible/deploy.py`
  - install required collections and fail if installation fails
  - honor `ANSIBLE_CONFIG` and `ANSIBLE_ROLES_PATH`
  - run playbooks with explicit inventory `-i` only

- `cloudsoc/orchestrator.py`
  - generate `inventory/generated_hosts.ini`
  - wait for SSM readiness before running playbooks
  - keep `wazuh_manager.yml` and `victim_server.yml` as separate targeted steps

### Inventory and connection model

- generated inventory should use host groups:
  - `[wazuh]`
  - `[victims]`
- each host entry should include:
  - `ansible_connection=amazon.aws.aws_ssm`
  - `ansible_python_interpreter=/usr/bin/python3`
- add an optional bootstrap phase to validate the connection plugin.

## Key changes required

### 1. Make `ansible.cfg` explicit

- remove or replace `inventory = localhost`
- include `roles_path = ./roles:../roles:/etc/ansible/roles`
- optionally enforce `retry_files_enabled = False`

### 2. Add a bootstrap playbook

A new bootstrap playbook should ensure:

- AWS CLI is installed
- Docker engine and compose plugin are installed
- Python 3 and required pip packages are present
- SSM agent is running and reachable

This will reduce the chance that `wazuh_manager.yml` or `victim_server.yml` fail later due to missing runtime prerequisites.

### 3. Target remote host groups in playbooks

Update the playbooks to clearly express their target groups:

- `wazuh_manager.yml` → `hosts: wazuh`
- `victim_server.yml` → `hosts: victims`

That removes any ambiguity from the playbooks and aligns them with generated inventory.

### 4. Enforce collection installation

Update the Python Ansible wrapper to:

- run `ansible-galaxy collection install -r ansible/requirements.yml`
- stop execution and raise an error if install fails
- avoid continuing with missing collection plugins

### 5. Align Terraform outputs and role variables

Ensure outputs and roles match exactly:

- `s3_prefix` should be explicit and documented
- `wazuh_manager_ip` should be derived from Terraform output
- `ecr_victim_repository_url` should be available and passed into the victim playbook

## Documentation changes

The following documentation should be updated to reflect the new Ansible flow:

- `docs/2-guides/ansible/README.md`
- `docs/2-guides/ansible/deploy-wazuh.md`
- `README.md`
- any branch-specific doc references for Ansible architecture

## Recommended implementation checklist

1. Add `docs/2-guides/ansible/refactor-plan.md` (this file).
2. Update `docs/2-guides/ansible/README.md` to link the plan.
3. Correct `docs/2-guides/ansible/deploy-wazuh.md` to document generated inventory and remote host groups.
4. Change `ansible.cfg` to remove `localhost` default inventory.
5. Add `ansible/playbooks/bootstrap.yml`.
6. Update playbooks to target `wazuh` and `victims` explicitly.
7. Update `cloudsoc/ansible/deploy.py` to fail on missing collections.
8. Validate Terraform outputs and Ansible extra vars alignment.
9. Add a short “Ansible refactor” summary to the project docs index.

## Expected outcome

After the refactor, the Ansible layer should be:

- easier to reason about
- safer to run from the orchestrator
- easier to document for new operators
- better aligned with the project’s SSM-driven architecture
- less prone to failures caused by missing host prerequisites
