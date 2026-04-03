output "vpc_id" {
  value = aws_vpc.wazuh_vpc.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "wazuh_instance_id" {
  value = aws_instance.wazuh_server.id
}

output "wazuh_instance_public_ip" {
  value = aws_instance.wazuh_server.public_ip
}

output "victim_instance_id" {
  value = aws_instance.victim_server.id
}

output "victim_instance_ip" {
  value = aws_instance.victim_server.public_ip
}

output "s3_bucket_name" {
  value = aws_s3_bucket.wazuh_assets.id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.wazuh_repo.repository_url
}
