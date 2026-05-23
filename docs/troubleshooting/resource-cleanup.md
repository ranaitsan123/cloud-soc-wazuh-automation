# Resource Cleanup

## Overview

This document describes cleanup steps for sensitive or stateful files and resources.

## Recommended cleanup actions

1. Remove Terraform state and backup files from Git tracking:

```bash
git rm --cached terraform/terraform.tfstate terraform/terraform.tfstate.backup
```

2. Remove local artifacts and build outputs:

```bash
git rm --cached -r cloud_soc.egg-info/ .venv/ __pycache__/
```

3. Update `.gitignore` to ignore runtime and secret files.

4. Keep secrets out of the repository by using environment variables or a secrets manager.

## Notes

- Do not commit `.env` with real credentials.
- Use `.env.example` to share configuration structure without secrets.
- If secrets were committed, use history rewriting tools such as `git-filter-repo` or `bfg` cautiously.

## Next steps

- [Documentation Hub](../README.md)
- [Getting Started](../1-getting-started/README.md)
