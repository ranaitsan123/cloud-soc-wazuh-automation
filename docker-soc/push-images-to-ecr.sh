#!/usr/bin/env bash
set -euo pipefail

ECR_REPOSITORY_URL="${ECR_REPOSITORY_URL:-}"
AWS_REGION="${AWS_REGION:-eu-north-1}"
IMAGE_VERSION="${IMAGE_VERSION:-4.14.4}"

if [[ -z "$ECR_REPOSITORY_URL" ]]; then
  echo "ERROR: ECR_REPOSITORY_URL environment variable is required."
  echo "Example: export ECR_REPOSITORY_URL=123456789012.dkr.ecr.eu-north-1.amazonaws.com/cloud-soc-wazuh-repo"
  exit 1
fi

images=(
  "wazuh/wazuh-indexer:$IMAGE_VERSION"
  "wazuh/wazuh-manager:$IMAGE_VERSION"
  "wazuh/wazuh-dashboard:$IMAGE_VERSION"
)

aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REPOSITORY_URL"

for image in "${images[@]}"; do
  image_name="${image##*/}"
  tag="${image_name%%:*}"
  target_tag="$ECR_REPOSITORY_URL:${tag}-$IMAGE_VERSION"

  echo "Pulling $image"
  docker pull "$image"

  echo "Tagging $image -> $target_tag"
  docker tag "$image" "$target_tag"

  echo "Pushing $target_tag"
  docker push "$target_tag"
  echo "---"
done

echo "All Wazuh images pushed to ECR repository: $ECR_REPOSITORY_URL"
