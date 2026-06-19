# Operational Scenarios

## Overview

This document describes operational workflows and data flows for deployment, runtime operations, incident response, and rollback.

## Initial Deployment Flow

- Terraform plans and applies infrastructure changes.
- Assets are uploaded to S3.
- ECR repositories are configured.
- Wazuh Manager pulls configuration and images.
- Docker images are launched.

## Runtime Operations

- Wazuh Manager collects logs from victim instances.
- Audit logs and metrics are stored in S3.
- Search indices are persisted.
- The dashboard provides real-time monitoring.

## Incident Response Flow

- Wazuh detects a threat.
- An active response script runs.
- IAM permissions validate the action.
- A compromised VM can be isolated.

## Version Rollback Flow

- S3 versioning retains historical configuration files.
- Previous configuration versions can be restored.
- The system can be redeployed to a known good state.

## ECR CI/CD Scenario

- Developers build and push container images to ECR.
- Lifecycle policies prune old images.
- EC2 instances pull the latest images for deployment.
