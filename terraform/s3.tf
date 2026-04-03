variable "s3_bucket_name" {
  type        = string
  description = "S3 bucket name for SOC assets. Must be globally unique."
  default     = "cloud-soc-wazuh-assets"
}

variable "prevent_destroy_s3" {
  type        = bool
  description = "Protect S3 bucket from accidental destroy when true."
  default     = true
}

resource "aws_s3_bucket" "wazuh_assets" {
  bucket = var.s3_bucket_name

  tags = {
    Name      = "cloud-soc-wazuh-assets"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle {
    prevent_destroy = var.prevent_destroy_s3
  }
}

resource "aws_s3_bucket_public_access_block" "wazuh_assets" {
  bucket = aws_s3_bucket.wazuh_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}