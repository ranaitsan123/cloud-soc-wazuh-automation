# Ansible Deployment Guide

This guide explains how Ansible is used to configure the Cloud SOC environment after infrastructure is provisioned.

## Contents

- [Deploy Wazuh and Victim Services](deploy-wazuh.md)

## Purpose

This guide is for operators who want to:

- deploy and configure Wazuh Manager
- provision the victim instance
- use AWS SSM for remote execution
- separate infrastructure from configuration

## Overview

Terraform provisions the AWS infrastructure, while Ansible handles runtime configuration and service orchestration.

### Key benefits

- reduced drift through central configuration
- minimal instance bootstrap logic
- secure remote execution via AWS SSM
