terraform {
  backend "s3" {}
}

# Configure the backend at init-time with one of:
# terraform init -backend-config="bucket=YOUR_BUCKET" \
#   -backend-config="key=cloud-soc/terraform.tfstate" \
#   -backend-config="region=eu-north-1" \
#   -backend-config="dynamodb_table=YOUR_LOCK_TABLE"
