# terraform_safe_apply.sh Changelog

All changes to `terraform_safe_apply.sh` are recorded here for transparency and progress tracking.

## 2026-03-13 (UTC)
- initial creation: `terraform_safe_apply.sh` script (pre-check + imports for extra resources + plan/apply/destroy actions).
- added resource discovery and import for:
  - VPC (`aws_vpc.wazuh_vpc`)
  - Internet Gateway (`aws_internet_gateway.igw`)
  - Subnet (`aws_subnet.public`)
  - Route table (`aws_route_table.public`)
  - Route table association (`aws_route_table_association.public`)
  - Security groups (`jail-sg`, `victim-sg`, `wazuh-sg`)
  - EC2 instances (`wazuh_server`, `victim_server`)
  - IAM role/policy/profile/attachment

## 2026-03-13 (UTC) - bugfix
- prevent `terraform import ... None` from causing invalid ID errors.
- added guard in `import_if_missing`: skip import when `$aws_id` is empty or "None".

## 2026-03-13 (UTC) - audit log addition
- added runtime history logging to `terraform_safe_apply_history.json`:
  - `started`, `success`, `error` states
  - timestamps in UTC ISO-8601
  - action (`plan|apply|destroy`)
  - message summary
