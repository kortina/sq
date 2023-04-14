variable "aws_region" {
  default = "us-east-1"
}

variable "aws_account_id" {
  # studioquixote
  default = "965006678408"
}

variable "aws_availability_zones" {
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "access_key" {} # get from env TF_VAR_access_key
variable "secret_key" {} # get from env TF_VAR_secret_key

variable "cert_dir" {
  default = "vpn_certs"
}

# variable "subnet_id" {
#   default = "subnet-0227113cb55893eae" # davinci public subnet
# }


# variable "domain" {
#   default = "vpn.studioquixote.com"
# }

