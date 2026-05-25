data "aws_caller_identity" "current" {}

locals {
  asset_bucket_name = var.s3_bucket_name != "" ? var.s3_bucket_name : "cloud-soc-wazuh-assets-${data.aws_caller_identity.current.account_id}-${random_id.bucket_suffix.hex}"
}
