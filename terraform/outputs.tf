output "vpc_id" {
  value = aws_vpc.wazuh_vpc.id
}

output "management_private_subnet_id" {
  value = aws_subnet.management_private.id
}

output "production_private_subnet_id" {
  value = aws_subnet.production_private.id
}

output "nat_public_subnet_id" {
  value = aws_subnet.nat_public.id
}

output "wazuh_instance_id" {
  value = aws_instance.wazuh_server.id
}

output "wazuh_instance_private_ip" {
  value = aws_instance.wazuh_server.private_ip
}

output "victim_instance_id" {
  value = aws_instance.victim_server.id
}

output "victim_instance_private_ip" {
  value = aws_instance.victim_server.private_ip
}

output "s3_bucket_name" {
  value = aws_s3_bucket.wazuh_assets.id
}

output "ecr_victim_repository_url" {
  value = aws_ecr_repository.victim_repo.repository_url
}

output "ecr_manager_repository_url" {
  value = aws_ecr_repository.manager_repo.repository_url
}

# ECR output commented out as ECR is disabled for now
# output "ecr_repository_url" {
#   value = aws_ecr_repository.wazuh_repo.repository_url
# }
