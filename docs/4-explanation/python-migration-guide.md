# Python Migration Guide

## Overview

This document describes the migration from Bash scripts to a Python-based infrastructure orchestration platform.

The migration follows a phased approach that preserves compatibility while replacing Bash logic with a typed Python workflow.

## Architecture

### Before (Bash)

```text
Scripts (Bash)
    ↓
Terraform
    ↓
AWS CLI (jq, grep, text parsing)
```

### After (Python)

```text
Python CLI (Typer)
    ↓
Terraform Runner
    ↓
Boto3 SDK
    ↓
AWS
```

## Technology Stack

| Component | Tool | Version |
|-----------|------|---------|
| CLI Framework | Typer | 0.9+ |
| AWS SDK | Boto3 | 1.26+ |
| Validation | Pydantic | 2.0+ |
| Console UI | Rich | 13.0+ |
| Configuration | YAML + Environment | - |
| Testing | Pytest | 7.0+ |

## Project Structure

The Python orchestration project is organized around a package structure that separates CLI, Terraform orchestration, AWS services, Ansible integration, cleanup code, and configuration.

### Key components

- `cloudsoc/main.py` — Typer CLI entry point
- `cloudsoc/terraform/runner.py` — Terraform wrapper
- `cloudsoc/aws` — AWS service modules
- `cloudsoc/ansible` — Ansible integration
- `cloudsoc/cleanup` — cleanup and maintenance workflows
- `cloudsoc/config/settings.py` — configuration management

## Migration Goals

- eliminate brittle Bash and CLI parsing
- provide safer typed models for AWS resources
- unify workflow in Python with better error handling
- keep infrastructure stable while moving configuration logic to Ansible

## Notes

This guide is intended to help developers and operators understand the migration path and the current Python-native orchestration design.
