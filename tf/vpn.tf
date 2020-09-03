# https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway/tree/v1.2.0
# https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/2.5.0
# https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/2.48.0

# https://github.com/terraform-aws-modules/terraform-aws-vpn-gateway/blob/master/examples/complete-vpn-gateway/main.tf
provider "aws" {
  region = "us-west-1"
}

variable "vpc_private_subnets" {
  type    = list(string)
  default = ["10.10.11.0/24", "10.10.12.0/24", "10.10.13.0/24"]
}

module "vpn_gateway" {
  source  = "terraform-aws-modules/vpn-gateway/aws"
  version = "~> 2.0"

  vpn_gateway_id      = module.vpc.vgw_id
  customer_gateway_id = aws_customer_gateway.main.id

  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_route_table_ids   = module.vpc.private_route_table_ids
  vpc_subnet_route_table_count = length(var.vpc_private_subnets)
}

resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "172.83.124.10"
  type       = "ipsec.1"

  tags = {
    Name = "complete-vpn-gateway"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 2.0"

  name = "complete-vpn-gateway"

  cidr = "10.10.0.0/16"

  azs             = ["us-west-1a", "us-west-1b", "us-west-1c"]
  public_subnets  = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  private_subnets = var.vpc_private_subnets

  enable_nat_gateway = false

  enable_vpn_gateway = true

  tags = {
    Owner       = "user"
    Environment = "staging"
    Name        = "complete"
  }
}