# 01 Installation

## Overview

Install the Cloud SOC Wazuh Automation environment and prepare your local workspace.

## Prerequisites

- Python 3.8 or newer
- AWS account with valid credentials
- `pip` installed
- Access to the project repository

## Setup Steps

1. Clone the repository:

```bash
git clone https://github.com/ranaitsan123/cloud-soc-wazuh-automation.git
cd cloud-soc-wazuh-automation
```

2. Copy the environment template:

```bash
cp .env.example .env
```

3. Update `.env` with your AWS credentials and AWS region.

4. Install the Python package in editable mode:

```bash
pip install -e .
```

5. Confirm the CLI is available:

```bash
cloud-soc --help
```

## Next Steps

After installation, continue to the quick start guide:

- [Quick Start](02-quick-start.md)
