variable "s3_bucket_name" {
  type        = string
  description = "S3 bucket name for SOC assets. If empty, a unique bucket name is generated using the AWS account ID."
  default     = ""
}

resource "aws_s3_bucket" "wazuh_assets" {
  bucket = local.asset_bucket_name
  force_destroy = true

  tags = {
    Name      = local.asset_bucket_name
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "wazuh_assets" {
  bucket = aws_s3_bucket.wazuh_assets.id
  versioning_configuration {
    status = "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "wazuh_assets" {
  bucket = aws_s3_bucket.wazuh_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "wazuh_assets" {
  bucket = aws_s3_bucket.wazuh_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 object uploads are managed by cloudsoc after the bucket is created.
# Terraform provisions bucket resources only.




