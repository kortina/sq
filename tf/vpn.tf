# https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
# https://medium.com/@craig.beardy.digital/setup-managed-client-vpn-in-aws-using-terraform-342584d4f1e3
# see also:
# https://dannynunez.com/blog/aws-client-vpn-with-terraform/#:~:text=CD%20in%20your%20terraform%2Fvpc,%2Dvpn%2Dendpoint.tf.&text=Open%20the%20client%2Dvpn%2Dendpoint,the%20AWS%20Client%20VPN%20Endpoint.&text=Now%20that%20is%20added%2C%20save,following%20command%20in%20your%20terminal.
# associations.tf
resource aws_ec2_client_vpn_network_association private {
   client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
   subnet_id              = local.private_subnet_1
 }
# dns.tf
resource aws_route53_resolver_endpoint vpn_dns {
   name = "vpn-dns-access"
   direction = "INBOUND"
   security_group_ids = [aws_security_group.vpn_dns.id]
   ip_address {
     subnet_id = local.private_subnet_1
   }
   ip_address {
     subnet_id = local.private_subnet_2
   }
 }
# locals.tf
locals {
   private_subnet_1 = "subnet-xxxxxxxxxxxxxxxxx"
   private_subnet_2 = "subnet-xxxxxxxxxxxxxxxxx"
}
# providers.tf
provider aws {
   region = "eu-west-2"
 }
# routes.tf
resource null_resource client_vpn_ingress {
   depends_on = [aws_ec2_client_vpn_endpoint.vpn]
   provisioner "local-exec" {
     when    = create
     command = "aws ec2 authorize-client-vpn-ingress --client-vpn-endpoint-id ${aws_ec2_client_vpn_endpoint.vpn.id} --target-network-cidr 0.0.0.0/0 --authorize-all-groups"
   }
   lifecycle {
     create_before_destroy = true
   }
 }
 
 resource null_resource client_vpn_route_table {
   depends_on = [aws_ec2_client_vpn_endpoint.vpn]
   provisioner "local-exec" {
     when = create
     command = "aws ec2 create-client-vpn-route --client-vpn-endpoint-id ${aws_ec2_client_vpn_endpoint.vpn.id} --destination-cidr-block 0.0.0.0/0  --target-vpc-subnet-id ${local.private_subnet_1}"
   }
   lifecycle {
     create_before_destroy = true
   }
 }
 
 resource null_resource client_vpn_security_group {
   depends_on = [aws_ec2_client_vpn_endpoint.vpn]
   provisioner "local-exec" {
     when = create
     command = "aws ec2 apply-security-groups-to-client-vpn-target-network --client-vpn-endpoint-id ${aws_ec2_client_vpn_endpoint.vpn.id} --vpc-id ${aws_security_group.vpn_access.vpc_id} --security-group-ids ${aws_security_group.vpn_access.id}"
   }
   lifecycle {
     create_before_destroy = true
   }
 }
# security-groups.tf
resource aws_security_group vpn_access {
   name = "shared-vpn-access"
   vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
   ingress {
     from_port = 0
     protocol = "-1"
     to_port = 0
     cidr_blocks = ["0.0.0.0/0"]
   }
   egress {
     from_port = 0
     protocol = "-1"
     to_port = 0
     cidr_blocks = ["0.0.0.0/0"]
   }
 }
 
 resource aws_security_group vpn_dns {
   name = "vpn_dns"
   vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
   ingress {
     from_port = 0
     protocol = "-1"
     to_port = 0
     security_groups = [aws_security_group.vpn_access.id]
   }
   egress {
     from_port = 0
     protocol = "-1"
     to_port = 0
     cidr_blocks = ["0.0.0.0/0"]
   }
 }
# vpn.tf
resource aws_ec2_client_vpn_endpoint vpn {
   client_cidr_block      = "10.10.0.0/21"
   split_tunnel           = false
   server_certificate_arn = "arn:aws:acm:eu-west-2:xxxxxxxx:certificate/xxxxx"
   dns_servers = [
     aws_route53_resolver_endpoint.vpn_dns.ip_address.*.ip[0], 
     aws_route53_resolver_endpoint.vpn_dns.ip_address.*.ip[1]
   ]
   
   authentication_options {
     type                       = "certificate-authentication"
     root_certificate_chain_arn = "arn:aws:acm:eu-west-2:xxxxxxxxx:certificate/xxxxx"
   }
   
   connection_log_options {
     enabled = false
   }   
 }