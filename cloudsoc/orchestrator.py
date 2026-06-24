"""Compatibility shim for the legacy orchestration module.

This module re-exports the newer orchestration package classes and helpers.
It preserves the old public API surface while allowing internal refactoring.
"""

from cloudsoc.aws.ecr import ECRService
from cloudsoc.aws.ssm import SSMService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.terraform.imports import ResourceImporter
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.utils.logger import logger
from cloudsoc.utils.shell import ShellCommandError, run_command

from cloudsoc.orchestration import (
    BuildOrchestrator,
    DashboardOrchestrator,
    DeploymentOrchestrator,
    OrchestrationError,
    PlatformOrchestrator,
    SSMDashboardTunnelManager,
    TerraformOrchestrator,
    TunnelSession,
)
import subprocess
import time

__all__ = [
    "BuildOrchestrator",
    "DashboardOrchestrator",
    "DeploymentOrchestrator",
    "OrchestrationError",
    "PlatformOrchestrator",
    "SSMDashboardTunnelManager",
    "TerraformOrchestrator",
    "TunnelSession",
    "ECRService",
    "SSMService",
    "DeploymentService",
    "TerraformRunner",
    "TerraformStateError",
    "ResourceImporter",
    "logger",
    "run_command",
    "ShellCommandError",
    "Settings",
    "get_settings",
]

# Expose commonly-patched modules/objects on this compatibility shim so tests
# that patch names like `cloudsoc.orchestrator.subprocess` or
# `cloudsoc.orchestrator.time.time` work as expected.
subprocess = subprocess
time = time
