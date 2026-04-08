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

# Upload wazuh-docker files to S3
resource "aws_s3_object" "wazuh_docker_compose" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/docker-compose.yml"
  source = "${path.module}/../wazuh-docker/docker-compose.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/docker-compose.yml")

  tags = {
    Name      = "wazuh-docker-compose"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_certs_generator" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/generate-indexer-certs.yml"
  source = "${path.module}/../wazuh-docker/generate-indexer-certs.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/generate-indexer-certs.yml")

  tags = {
    Name      = "wazuh-certs-generator"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

# Upload config files
resource "aws_s3_object" "wazuh_config_certs" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/certs.yml"
  source = "${path.module}/../wazuh-docker/config/certs.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/config/certs.yml")

  tags = {
    Name      = "wazuh-config-certs"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_manager_conf" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/wazuh_cluster/wazuh_manager.conf"
  source = "${path.module}/../wazuh-docker/config/wazuh_cluster/wazuh_manager.conf"
  etag   = filemd5("${path.module}/../wazuh-docker/config/wazuh_cluster/wazuh_manager.conf")

  tags = {
    Name      = "wazuh-manager-conf"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_indexer_config" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml"
  source = "${path.module}/../wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml")

  tags = {
    Name      = "wazuh-indexer-config"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_indexer_users" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/wazuh_indexer/internal_users.yml"
  source = "${path.module}/../wazuh-docker/config/wazuh_indexer/internal_users.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/config/wazuh_indexer/internal_users.yml")

  tags = {
    Name      = "wazuh-indexer-users"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_dashboard_config" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml"
  source = "${path.module}/../wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml")

  tags = {
    Name      = "wazuh-dashboard-config"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_object" "wazuh_dashboard_wazuh_yml" {
  bucket = aws_s3_bucket.wazuh_assets.id
  key    = "wazuh-docker/config/wazuh_dashboard/wazuh.yml"
  source = "${path.module}/../wazuh-docker/config/wazuh_dashboard/wazuh.yml"
  etag   = filemd5("${path.module}/../wazuh-docker/config/wazuh_dashboard/wazuh.yml")

  tags = {
    Name      = "wazuh-dashboard-wazuh-config"
    Project   = "cloud-soc"
    ManagedBy = "terraform"
  }
}