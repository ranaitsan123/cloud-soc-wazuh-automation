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

output "wazuh_manager_ui_url" {
  value = "https://${aws_instance.wazuh_server.private_ip}"
  description = "Private HTTPS URL for the Wazuh Manager UI. Use with VPN/SSM port forwarding if outside the VPC."
}

output "wazuh_manager_ssm_port_forward_command" {
  value = "aws ssm start-session --target ${aws_instance.wazuh_server.id} --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters '{\"host\":[\"127.0.0.1\"],\"portNumber\":[\"443\"],\"localPortNumber\":[\"8443\"]}'"
  description = "Local command to forward the Wazuh Manager UI over SSM to https://127.0.0.1:8443."
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
