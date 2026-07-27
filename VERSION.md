# Version Tracking for Cloud SOC Orchestration Branches

This document records the branch versions, responsibilities, and historical context for the Python-based orchestration architecture used by this repository.

## Current Backup Definition

- **Branch:** `refactor/python-orchestrator-v2`
- **Role:** Backup reference for the current `main` branch
- **Purpose:** Preserves the current Python platform orchestration architecture as a stable reference for the mainline implementation
- **Represents:** The Python-first orchestration model with Typer CLI entrypoints, Terraform orchestration, deployment orchestration, and dashboard access workflows
- **Last confirmed snapshot:** 2026-07-26
- **Reference commit:** `6ec0df1` (same state as the current `main` branch at the time of documentation)

## Branch Responsibility Matrix

| Branch | Last updated | Responsibility / purpose |
| --- | --- | --- |
| `main` | 2026-07-04 | Primary reference branch for the repository baseline and the latest mainline state. |
| `refactor/python-orchestrator-v2` | 2026-07-26 | Backup branch for `main`, preserving the current Python orchestration architecture as the canonical reference implementation. |
| `refactor/python-orchestrator-v3` | 2026-07-04 | Follow-on refactor branch aligned with the same latest state as `main` for continued iteration. |
| `refactor/python-orchestrator` | 2026-05-25 | Early branch for the Python orchestrator concept and branch-specific documentation. |
| `refactor/python-orchestrator-no-ansible` | 2026-06-01 | Variant focused on Terraform-based deployment scripting without relying on Ansible. |
| `feature/art-soc-baseline` | 2026-06-30 | Branch for SOC baseline deployment work, including AWS resource import logic and baseline environment setup. |
| `feature/art-soc-baseline-ansible` | 2026-05-25 | Ansible-based variant of the ART/SOC baseline work. |
| `feature/build-deployment-workflow` | 2026-06-13 | Branch for improving deployment workflow reliability, detailed error logging, and task-state tracking. |
| `feature/ngrok` | 2026-06-23 | Branch for Ngrok integration, authentication handling, and Docker-based setup. |
| `feature/ssm-dashboard-connection` | 2026-06-16 | Branch for dashboard access through SSM with host-network mode support. |
| `presentation` | 2026-07-01 | Presentation-oriented branch focused on orchestrator health checks and dashboard diagnostics. |
| `v1-single-vpc` | 2026-04-21 | Legacy reference branch for the earlier single-VPC deployment model and supporting documentation. |

## Notes

- `main` should remain the current production/reference baseline.
- `refactor/python-orchestrator-v2` is the backup branch that preserves the current Python orchestration architecture for recovery, comparison, or future reference.
- New feature branches should document their purpose here when they become important enough to be tracked as part of the platform evolution.
