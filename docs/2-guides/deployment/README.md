# Custom YAML Deployment Guide

This guide explains how the Cloud SOC project uses custom YAML-based deployments to configure the Wazuh Manager and victim instance after infrastructure is provisioned.

## Contents

- [Deploy Wazuh and Victim Services](deploy-wazuh.md)

## Purpose

This guide is for operators who want to:

- deploy and configure Wazuh Manager
- provision the victim instance
- use AWS SSM for remote execution
- separate infrastructure from configuration

## Overview

Terraform provisions the AWS infrastructure, while custom YAML-based deployments handle runtime configuration and service orchestration without the overhead of Ansible.

### Key benefits

- reduced drift through centralized configuration
- minimal instance bootstrap logic
- secure remote execution via AWS SSM
- lightweight alternative to Ansible with custom YAML schemas
