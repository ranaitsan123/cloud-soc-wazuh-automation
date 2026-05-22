# Terraform uses the local backend by default.
# If backend runtime values are supplied via environment variables,
# the orchestrator can initialize an S3 backend automatically.
#
# Set the following environment variables to enable S3 state storage:
#   TERRAFORM_BACKEND_BUCKET
#   TERRAFORM_BACKEND_KEY
#   TERRAFORM_BACKEND_REGION
# Optional:
#   TERRAFORM_BACKEND_DYNAMODB_TABLE
