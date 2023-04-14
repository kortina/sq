module "ec2_docker_instance" {
    source = "./modules/ec2_docker"   
}

resource "aws_s3_bucket" "cyberpunk202x" {
    bucket                      = "cyberpunk202x"
    # region                      = "us-east-1"
    request_payer               = "BucketOwner"
    tags                        = {}

    versioning {
        enabled    = false
        mfa_delete = false
    }
}

resource "aws_iam_user_policy_attachment" "AdministratorAccess-policy-attachment" {
    # name       = "AdministratorAccess-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
    user       = "sqdev"
}

resource "aws_iam_user" "sqdev" {
    name = "sqdev"
    path = "/"
}