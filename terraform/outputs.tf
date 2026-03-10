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
