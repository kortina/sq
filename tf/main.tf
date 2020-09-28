# basically created with
# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/tutorial-efs-volumes.html
# BUT used regular ECS  (not Fargate)

# aws_s3_bucket.cyberpunk202x:
resource "aws_s3_bucket" "cyberpunk202x" {
    bucket                      = "cyberpunk202x"
    # region                      = "us-west-1"
    request_payer               = "BucketOwner"
    tags                        = {}

    versioning {
        enabled    = false
        mfa_delete = false
    }
}

# ##########
# # alb.tf
# ##########



# ##########
# # asg.tf
# ##########
resource "aws_autoscaling_group" "EC2ContainerService-sq-EcsInstanceAsg-18YFD43EPILLE" {
    desired_capacity          = 1
    health_check_grace_period = 0
    health_check_type         = "EC2"
    launch_configuration      = "EC2ContainerService-sq-EcsInstanceLc-1CM7WE9CWHJCC"
    max_size                  = 1
    min_size                  = 0
    name                      = "EC2ContainerService-sq-EcsInstanceAsg-18YFD43EPILLE"
    vpc_zone_identifier       = ["subnet-082e323ce59d549e3", "subnet-01c1d06ee4451e7ff"]

    tag {
        key   = "Description"
        value = "This instance is the part of the Auto Scaling group which was created through ECS Console"
        propagate_at_launch = true
    }

    tag {
        key   = "Name"
        value = "ECS Instance - EC2ContainerService-sq"
        propagate_at_launch = true
    }

    tag {
        key   = "aws:cloudformation:logical-id"
        value = "EcsInstanceAsg"
        propagate_at_launch = true
    }

    tag {
        key   = "aws:cloudformation:stack-id"
        value = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
        propagate_at_launch = true
    }

    tag {
        key   = "aws:cloudformation:stack-name"
        value = "EC2ContainerService-sq"
        propagate_at_launch = true
    }

}



##########
# cwa.tf
##########



##########
# dbpg.tf
##########



##########
# dbsg.tf
##########



##########
# dbsn.tf
##########



##########
# ddb.tf
##########



##########
# ec2.tf
##########
resource "aws_instance" "ECS-Instance---EC2ContainerService-sq" {
    ami                         = "ami-0b95d46a7f7393cfa"
    availability_zone           = "us-west-1a"
    ebs_optimized               = false
    instance_type               = "t2.micro"
    monitoring                  = true
    key_name                    = "sq_aws"
    subnet_id                   = "subnet-01c1d06ee4451e7ff"
    vpc_security_group_ids      = ["sg-0176e8021bec0c6b4"]
    associate_public_ip_address = true
    private_ip                  = "10.0.0.68"
    source_dest_check           = true

    root_block_device {
        volume_type           = "gp2"
        volume_size           = 30
        delete_on_termination = true
    }

    tags = {
        "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
        "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
        "Name" = "ECS Instance - EC2ContainerService-sq"
        "aws:autoscaling:groupName" = "EC2ContainerService-sq-EcsInstanceAsg-18YFD43EPILLE"
        "aws:cloudformation:logical-id" = "EcsInstanceAsg"
    }
}



##########
# ecc.tf
##########



##########
# ecsn.tf
##########



##########
# efs.tf
##########
resource "aws_efs_file_system" "fs-e7507afe" {
    creation_token = "console-2505e608-8baa-4da0-82e3-e0963895d0c5"
    # file_system_id = "fs-e7507afe"
    performance_mode = "generalPurpose"
    tags = {
        Name = "efs-for-ecs"
    }
}


##########
# eip.tf
##########



##########
# elb.tf
##########



##########
# iamg.tf
##########



##########
# iamgm.tf
##########



##########
# iamgp.tf
##########



##########
# iamip.tf
##########
resource "aws_iam_instance_profile" "ecsInstanceRole" {
    name = "ecsInstanceRole"
    path = "/"
    role = "ecsInstanceRole"
}



##########
# iamp.tf
##########



##########
# iampa.tf
##########
resource "aws_iam_role_policy_attachment" "AutoScalingServiceRolePolicy-policy-attachment" {
    # name       = "AutoScalingServiceRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AutoScalingServiceRolePolicy"
    role       = "AWSServiceRoleForAutoScaling"
}

resource "aws_iam_role_policy_attachment" "AmazonECSServiceRolePolicy-policy-attachment" {
    # name       = "AmazonECSServiceRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AmazonECSServiceRolePolicy"
    role       = "AWSServiceRoleForECS"
}

resource "aws_iam_role_policy_attachment" "AWSSupportServiceRolePolicy-policy-attachment" {
    # name       = "AWSSupportServiceRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSSupportServiceRolePolicy"
    role       = "AWSServiceRoleForSupport"
}

resource "aws_iam_role_policy_attachment" "AmazonECSTaskExecutionRolePolicy-policy-attachment" {
    # name       = "AmazonECSTaskExecutionRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
    role       = "ecsTaskExecutionRole"
}

resource "aws_iam_role_policy_attachment" "AWSTrustedAdvisorServiceRolePolicy-policy-attachment" {
    # name       = "AWSTrustedAdvisorServiceRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSTrustedAdvisorServiceRolePolicy"
    role       = "AWSServiceRoleForTrustedAdvisor"
}

resource "aws_iam_role_policy_attachment" "AmazonEC2ContainerServiceforEC2Role-policy-attachment" {
    # name       = "AmazonEC2ContainerServiceforEC2Role-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
    role       = "ecsInstanceRole"
}

resource "aws_iam_role_policy_attachment" "AmazonElasticFileSystemServiceRolePolicy-policy-attachment" {
    # name       = "AmazonElasticFileSystemServiceRolePolicy-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AmazonElasticFileSystemServiceRolePolicy"
    role      = "AWSServiceRoleForAmazonElasticFileSystem"
}

resource "aws_iam_role_policy_attachment" "AWSBackupServiceLinkedRolePolicyForBackup-policy-attachment" {
    # name       = "AWSBackupServiceLinkedRolePolicyForBackup-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSBackupServiceLinkedRolePolicyForBackup"
    role       = "AWSServiceRoleForBackup"
}

resource "aws_iam_user_policy_attachment" "AdministratorAccess-policy-attachment" {
    # name       = "AdministratorAccess-policy-attachment"
    policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
    user       = "sqdev"
}


##########
# iamr.tf
##########
resource "aws_iam_role" "AWSServiceRoleForAmazonElasticFileSystem" {
    name               = "AWSServiceRoleForAmazonElasticFileSystem"
    path               = "/aws-service-role/elasticfilesystem.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "elasticfilesystem.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "AWSServiceRoleForAutoScaling" {
    description        = "Default Service-Linked Role enables access to AWS Services and Resources used or managed by Auto Scaling"
    name               = "AWSServiceRoleForAutoScaling"
    path               = "/aws-service-role/autoscaling.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "autoscaling.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "AWSServiceRoleForBackup" {
    name               = "AWSServiceRoleForBackup"
    path               = "/aws-service-role/backup.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "backup.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "AWSServiceRoleForECS" {
    description        = "Role to enable Amazon ECS to manage your cluster."
    name               = "AWSServiceRoleForECS"
    path               = "/aws-service-role/ecs.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "AWSServiceRoleForSupport" {
    description        = "Enables resource access for AWS to provide billing, administrative and support services"
    name               = "AWSServiceRoleForSupport"
    path               = "/aws-service-role/support.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "support.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "AWSServiceRoleForTrustedAdvisor" {
    description        = "Access for the AWS Trusted Advisor Service to help reduce cost, increase performance, and improve security of your AWS environment." 

    name               = "AWSServiceRoleForTrustedAdvisor"
    path               = "/aws-service-role/trustedadvisor.amazonaws.com/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "trustedadvisor.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "ecsInstanceRole" {
    name               = "ecsInstanceRole"
    path               = "/"
    assume_role_policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role" "ecsTaskExecutionRole" {
    name               = "ecsTaskExecutionRole"
    path               = "/"
    assume_role_policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}



##########
# iamrp.tf
##########



##########
# iamu.tf
##########
resource "aws_iam_user" "sqdev" {
    name = "sqdev"
    path = "/"
}



##########
# iamup.tf
##########



##########
# igw.tf
##########
resource "aws_internet_gateway" "igw-0803f93bfcb0b3158" {
    vpc_id = "vpc-08ecdd9d68981bee5"

    # tags = {
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    #     "aws:cloudformation:logical-id" = "InternetGateway"
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    # }
}



##########
# kmsa.tf
##########



##########
# kmsk.tf
##########



##########
# lc.tf
##########
resource "aws_launch_configuration" "EC2ContainerService-sq-EcsInstanceLc-1CM7WE9CWHJCC" {
    name                        = "EC2ContainerService-sq-EcsInstanceLc-1CM7WE9CWHJCC"
    image_id                    = "ami-0b95d46a7f7393cfa"
    instance_type               = "t2.micro"
    iam_instance_profile        = "arn:aws:iam::965006678408:instance-profile/ecsInstanceRole"
    key_name                    = "sq_aws"
    security_groups             = ["sg-0176e8021bec0c6b4"]
    user_data                   = "IyEvYmluL2Jhc2gKZWNobyBFQ1NfQ0xVU1RFUj1zcSA+PiAvZXRjL2Vjcy9lY3MuY29uZmlnO2VjaG8gRUNTX0JBQ0tFTkRfSE9TVD0gPj4gL2V0Yy9lY3MvZWNzLmNvbmZpZzs="
    enable_monitoring           = true
    ebs_optimized               = false

    root_block_device {
        volume_type           = "gp2"
        volume_size           = 30
        delete_on_termination = false
    }

}



##########
# nacl.tf
##########
resource "aws_network_acl" "acl-0194a803dc01eddf3" {
    vpc_id     = "vpc-08ecdd9d68981bee5"
    subnet_ids = ["subnet-01c1d06ee4451e7ff", "subnet-082e323ce59d549e3"]

    ingress {
        from_port  = 0
        to_port    = 0
        rule_no    = 100
        action     = "allow"
        protocol   = "-1"
        cidr_block = "0.0.0.0/0"
    }

    egress {
        from_port  = 0
        to_port    = 0
        rule_no    = 100
        action     = "allow"
        protocol   = "-1"
        cidr_block = "0.0.0.0/0"
    }

    # tags {
    # }
}

resource "aws_network_acl" "acl-870693e1" {
    vpc_id     = "vpc-c043bba6"
    subnet_ids = []

    ingress {
        from_port  = 0
        to_port    = 0
        rule_no    = 100
        action     = "allow"
        protocol   = "-1"
        cidr_block = "0.0.0.0/0"
    }

    egress {
        from_port  = 0
        to_port    = 0
        rule_no    = 100
        action     = "allow"
        protocol   = "-1"
        cidr_block = "0.0.0.0/0"
    }

    # tags {
    # }
}



##########
# nat.tf
##########



##########
# nif.tf
##########
resource "aws_network_interface" "eni-06d89663249a7b5e8" {
    description       = "EFS mount target for fs-e7507afe (fsmt-4d56ee54)"
    subnet_id         = "subnet-01c1d06ee4451e7ff"
    private_ips       = ["10.0.0.5"]
    security_groups   = ["sg-054dc2a574201ef5b", "sg-0a69a1c70b137ad76"]
    source_dest_check = true
}

resource "aws_network_interface" "eni-03210a5b91597fdde" {
    subnet_id         = "subnet-01c1d06ee4451e7ff"
    private_ips       = ["10.0.0.68"]
    security_groups   = ["sg-0176e8021bec0c6b4"]
    source_dest_check = true
    attachment {
        instance     = "i-08418fe9cb5bae602"
        device_index = 0
    }
}

resource "aws_network_interface" "eni-031f0f3bda55b5b13" {
    description       = "EFS mount target for fs-e7507afe (fsmt-4b56ee52)"
    subnet_id         = "subnet-082e323ce59d549e3"
    private_ips       = ["10.0.1.164"]
    security_groups   = ["sg-054dc2a574201ef5b", "sg-0a69a1c70b137ad76"]
    source_dest_check = true
}



##########
# r53r.tf
##########



##########
# r53z.tf
##########



##########
# rds.tf
##########



##########
# rs.tf
##########



##########
# rt.tf
##########
resource "aws_route_table" "rtb-0d11efd69a6f5bd54" {
    vpc_id     = "vpc-08ecdd9d68981bee5"

    # tags {
    # }
}

resource "aws_route_table" "rtb-b685f2d0" {
    vpc_id     = "vpc-c043bba6"

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "igw-9024ddf7"
    }

    # tags {
    # }
}

resource "aws_route_table" "rtb-006b1040443ad832a" {
    vpc_id     = "vpc-08ecdd9d68981bee5"

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "igw-0803f93bfcb0b3158"
    }

    # tags = {
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    #     "aws:cloudformation:logical-id" = "RouteViaIgw"
    # }
}



##########
# rta.tf
##########
resource "aws_route_table_association" "rtb-006b1040443ad832a-rtbassoc-0a62f9adf8b403ba4" {
    route_table_id = "rtb-006b1040443ad832a"
    subnet_id = "subnet-082e323ce59d549e3"
}

resource "aws_route_table_association" "rtb-006b1040443ad832a-rtbassoc-0d04cc4a2a47010da" {
    route_table_id = "rtb-006b1040443ad832a"
    subnet_id = "subnet-01c1d06ee4451e7ff"
}



##########
# s3.tf
##########



##########
# sg.tf
##########
resource "aws_security_group" "vpc-08ecdd9d68981bee5-EC2ContainerService-sq-EcsSecurityGroup-OD5N1VR8ZDSA" {
    name        = "EC2ContainerService-sq-EcsSecurityGroup-OD5N1VR8ZDSA"
    description = "ECS Allowed Ports"
    vpc_id      = "vpc-08ecdd9d68981bee5"

    ingress {
        from_port       = 22
        to_port         = 22
        protocol        = "tcp"
        cidr_blocks     = ["0.0.0.0/0"]
    }


    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

    # tags = {
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    #     "aws:cloudformation:logical-id" = "EcsSecurityGroup"
    # }
}

resource "aws_security_group" "vpc-c043bba6-default" {
    name        = "default"
    description = "default VPC security group"
    vpc_id      = "vpc-c043bba6"

    ingress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        security_groups = []
        self            = true
    }


    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

}

resource "aws_security_group" "vpc-08ecdd9d68981bee5-default" {
    name        = "default"
    description = "default VPC security group"
    vpc_id      = "vpc-08ecdd9d68981bee5"

    ingress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        security_groups = []
        self            = true
    }


    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

}

resource "aws_security_group" "vpc-08ecdd9d68981bee5-ecs-sq-6214" {
    name        = "ecs-sq-6214"
    description = "2020-09-27T18:22:11.391Z"
    vpc_id      = "vpc-08ecdd9d68981bee5"

    ingress {
        from_port       = 80
        to_port         = 80
        protocol        = "tcp"
        cidr_blocks     = ["0.0.0.0/0"]
    }


    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

}

resource "aws_security_group" "vpc-08ecdd9d68981bee5-EFS-access-for-sg-0176e8021bec0c6b4" {
    name        = "EFS-access-for-sg-0176e8021bec0c6b4"
    description = "Allow EFS access for ECS"
    vpc_id      = "vpc-08ecdd9d68981bee5"

    ingress {
        from_port       = 2049
        to_port         = 2049
        protocol        = "tcp"
        security_groups = ["sg-0176e8021bec0c6b4"]
        self            = false
        description     = "Allow EFS access for ECS"
    }


    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

}



##########
# sn.tf
##########
resource "aws_subnet" "subnet-082e323ce59d549e3-subnet-082e323ce59d549e3" {
    vpc_id                  = "vpc-08ecdd9d68981bee5"
    cidr_block              = "10.0.1.0/24"
    availability_zone       = "us-west-1b"
    map_public_ip_on_launch = true

    # tags = {
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    #     "aws:cloudformation:logical-id" = "PubSubnetAz2"
    # }
}

resource "aws_subnet" "subnet-01c1d06ee4451e7ff-subnet-01c1d06ee4451e7ff" {
    vpc_id                  = "vpc-08ecdd9d68981bee5"
    cidr_block              = "10.0.0.0/24"
    availability_zone       = "us-west-1a"
    map_public_ip_on_launch = true

    # tags = {
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    #     "aws:cloudformation:logical-id" = "PubSubnetAz1"
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    # }
}



##########
# snss.tf
##########



##########
# snst.tf
##########



##########
# sqs.tf
##########


##########
# vgw.tf
##########



##########
# vpc.tf
##########
resource "aws_vpc" "vpc-c043bba6" {
    cidr_block           = "172.31.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
    instance_tenancy     = "default"

    # tags = {
    # }
}

resource "aws_vpc" "vpc-08ecdd9d68981bee5" {
    cidr_block           = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
    instance_tenancy     = "default"

    # tags = {
    #     "aws:cloudformation:stack-name" = "EC2ContainerService-sq"
    #     "aws:cloudformation:stack-id" = "arn:aws:cloudformation:us-west-1:965006678408:stack/EC2ContainerService-sq/d3aade70-00ea-11eb-be79-06621dc34151"
    #     "aws:cloudformation:logical-id" = "Vpc"
    # }
}

# resource "aws_cloudformation_stack" "EC2ContainerService-sq" {
#     disable_rollback = false
#     id               = "EC2ContainerService-sq"
#     name             = "EC2ContainerService-sq"
#     outputs          = {
#         "EcsInstanceAsgName"     = "EC2ContainerService-sq-EcsInstanceAsg-18YFD43EPILLE"
#         "TemplateVersion"        = "2.0.0"
#         "UsedByECSCreateCluster" = "true"
#     }
#     parameters       = {}
#     tags             = {}
#     template_body    = <<EOT
#         AWSTemplateFormatVersion: '2010-09-09'
#         Description: >
#           AWS CloudFormation template to create a new VPC
#           or use an existing VPC for ECS deployment
#           in Create Cluster Wizard. Requires exactly 1
#           Instance Types for a Spot Request.
#         Parameters:
#           EcsClusterName:
#             Type: String
#             Description: >
#               Specifies the ECS Cluster Name with which the resources would be
#               associated
#             Default: default
#           EcsAmiId:
#             Type: String
#             Description: Specifies the AMI ID for your container instances.
#           EcsInstanceType:
#             Type: CommaDelimitedList
#             Description: >
#               Specifies the EC2 instance type for your container instances.
#               Defaults to m4.large
#             Default: m4.large
#             ConstraintDescription: must be a valid EC2 instance type.
#           KeyName:
#             Type: String
#             Description: >
#               Optional - Specifies the name of an existing Amazon EC2 key pair
#               to enable SSH access to the EC2 instances in your cluster.
#             Default: ''
#           VpcId:
#             Type: String
#             Description: >
#               Optional - Specifies the ID of an existing VPC in which to launch
#               your container instances. If you specify a VPC ID, you must specify a list of
#               existing subnets in that VPC. If you do not specify a VPC ID, a new VPC is created
#               with atleast 1 subnet.
#             Default: ''
#             ConstraintDescription: >
#               VPC Id must begin with 'vpc-' or leave blank to have a
#               new VPC created
#           SubnetIds:
#             Type: CommaDelimitedList
#             Description: >
#               Optional - Specifies the Comma separated list of existing VPC Subnet
#               Ids where ECS instances will run
#             Default: ''
#           SecurityGroupId:
#             Type: String
#             Description: >
#               Optional - Specifies the Security Group Id of an existing Security
#               Group. Leave blank to have a new Security Group created
#             Default: ''
#           VpcCidr:
#             Type: String
#             Description: Optional - Specifies the CIDR Block of VPC
#             Default: ''
#           SubnetCidr1:
#             Type: String
#             Description: Specifies the CIDR Block of Subnet 1
#             Default: ''
#           SubnetCidr2:
#             Type: String
#             Description: Specifies the CIDR Block of Subnet 2
#             Default: ''
#           SubnetCidr3:
#             Type: String
#             Description: Specifies the CIDR Block of Subnet 3
#             Default: ''
#           AsgMaxSize:
#             Type: Number
#             Description: >
#               Specifies the number of instances to launch and register to the cluster.
#               Defaults to 1.
#             Default: '1'
#           IamRoleInstanceProfile:
#             Type: String
#             Description: >
#               Specifies the Name or the Amazon Resource Name (ARN) of the instance
#               profile associated with the IAM role for the instance
#           SecurityIngressFromPort:
#             Type: Number
#             Description: >
#               Optional - Specifies the Start of Security Group port to open on
#               ECS instances - defaults to port 0
#             Default: '0'
#           SecurityIngressToPort:
#             Type: Number
#             Description: >
#               Optional - Specifies the End of Security Group port to open on ECS
#               instances - defaults to port 65535
#             Default: '65535'
#           SecurityIngressCidrIp:
#             Type: String
#             Description: >
#               Optional - Specifies the CIDR/IP range for Security Ports - defaults
#               to 0.0.0.0/0
#             Default: 0.0.0.0/0
#           EcsEndpoint:
#             Type: String
#             Description: >
#               Optional - Specifies the ECS Endpoint for the ECS Agent to connect to
#             Default: ''
#           VpcAvailabilityZones:
#             Type: CommaDelimitedList
#             Description: >
#               Specifies a comma-separated list of 3 VPC Availability Zones for
#               the creation of new subnets. These zones must have the available status.
#             Default: ''
#           RootEbsVolumeSize:
#             Type: Number
#             Description: >
#               Optional - Specifies the Size in GBs of the root EBS volume
#             Default: 30
#           EbsVolumeSize:
#             Type: Number
#             Description: >
#               Optional - Specifies the Size in GBs of the data storage EBS volume used by the Docker in the AL1 ECS-optimized AMI
#             Default: 22
#           EbsVolumeType:
#             Type: String
#             Description: Optional - Specifies the Type of (Amazon EBS) volume
#             Default: ''
#             AllowedValues:
#               - ''
#               - standard
#               - io1
#               - gp2
#               - sc1
#               - st1
#             ConstraintDescription: Must be a valid EC2 volume type.
#           RootDeviceName:
#             Type: String
#             Description: Optional - Specifies the device mapping for the root EBS volume.
#             Default: /dev/xvda
#           DeviceName:
#             Type: String
#             Description: Optional - Specifies the device mapping for the EBS volume used for data storage. Only applicable to AL1.
#           UseSpot:
#             Type: String
#             Default: 'false'
#           IamSpotFleetRoleArn:
#             Type: String
#             Default: ''
#           SpotPrice:
#             Type: String
#             Default: ''
#           SpotAllocationStrategy:
#             Type: String
#             Default: 'diversified'
#             AllowedValues:
#               - 'lowestPrice'
#               - 'diversified'
#           UserData:
#             Type: String
#           IsWindows:
#             Type: String
#             Default: 'false'
#           ConfigureRootVolume:
#             Type: String
#             Description: Optional - Specifies if there should be customization of the root volume
#             Default: 'false'
#           ConfigureDataVolume:
#             Type: String
#             Description: Optional - Specifies if there should be customization of the data volume
#             Default: 'true'
#           AutoAssignPublicIp:
#             Type: String
#             Default: 'INHERIT'
#         Conditions:
#           CreateEC2LCWithKeyPair:
#             !Not [!Equals [!Ref KeyName, '']]
#           SetEndpointToECSAgent:
#             !Not [!Equals [!Ref EcsEndpoint, '']]
#           CreateNewSecurityGroup:
#             !Equals [!Ref SecurityGroupId, '']
#           CreateNewVpc:
#             !Equals [!Ref VpcId, '']
#           CreateSubnet1: !And
#             - !Not [!Equals [!Ref SubnetCidr1, '']]
#             - !Condition CreateNewVpc
#           CreateSubnet2: !And
#             - !Not [!Equals [!Ref SubnetCidr2, '']]
#             - !Condition CreateSubnet1
#           CreateSubnet3: !And
#             - !Not [!Equals [!Ref SubnetCidr3, '']]
#             - !Condition CreateSubnet2
#           CreateWithSpot: !Equals [!Ref UseSpot, 'true']
#           CreateWithASG: !Not [!Condition CreateWithSpot]
#           CreateWithSpotPrice: !Not [!Equals [!Ref SpotPrice, '']]
#           IsConfiguringRootVolume: !Equals [!Ref ConfigureRootVolume, 'true']
#           IsConfiguringDataVolume: !Equals [!Ref ConfigureDataVolume, 'true']
#           IsInheritPublicIp: !Equals [!Ref AutoAssignPublicIp, 'INHERIT']
#         Resources:
#           Vpc:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::VPC
#             Properties:
#               CidrBlock: !Ref VpcCidr
#               EnableDnsSupport: true
#               EnableDnsHostnames: true
#           PubSubnetAz1:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::Subnet
#             Properties:
#               VpcId: !Ref Vpc
#               CidrBlock: !Ref SubnetCidr1
#               AvailabilityZone: !Select [ 0, !Ref VpcAvailabilityZones ]
#               MapPublicIpOnLaunch: true
#           PubSubnetAz2:
#             Condition: CreateSubnet2
#             Type: AWS::EC2::Subnet
#             Properties:
#               VpcId: !Ref Vpc
#               CidrBlock: !Ref SubnetCidr2
#               AvailabilityZone: !Select [ 1, !Ref VpcAvailabilityZones ]
#               MapPublicIpOnLaunch: true
#           PubSubnetAz3:
#             Condition: CreateSubnet3
#             Type: AWS::EC2::Subnet
#             Properties:
#               VpcId: !Ref Vpc
#               CidrBlock: !Ref SubnetCidr3
#               AvailabilityZone: !Select [ 2, !Ref VpcAvailabilityZones ]
#               MapPublicIpOnLaunch: true
#           InternetGateway:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::InternetGateway
#           AttachGateway:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::VPCGatewayAttachment
#             Properties:
#               VpcId: !Ref Vpc
#               InternetGatewayId: !Ref InternetGateway
#           RouteViaIgw:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::RouteTable
#             Properties:
#               VpcId: !Ref Vpc
#           PublicRouteViaIgw:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::Route
#             DependsOn: AttachGateway
#             Properties:
#               RouteTableId: !Ref RouteViaIgw
#               DestinationCidrBlock: 0.0.0.0/0
#               GatewayId: !Ref InternetGateway
#           PubSubnet1RouteTableAssociation:
#             Condition: CreateSubnet1
#             Type: AWS::EC2::SubnetRouteTableAssociation
#             Properties:
#               SubnetId: !Ref PubSubnetAz1
#               RouteTableId: !Ref RouteViaIgw
#           PubSubnet2RouteTableAssociation:
#             Condition: CreateSubnet2
#             Type: AWS::EC2::SubnetRouteTableAssociation
#             Properties:
#               SubnetId: !Ref PubSubnetAz2
#               RouteTableId: !Ref RouteViaIgw
#           PubSubnet3RouteTableAssociation:
#             Condition: CreateSubnet3
#             Type: AWS::EC2::SubnetRouteTableAssociation
#             Properties:
#               SubnetId: !Ref PubSubnetAz3
#               RouteTableId: !Ref RouteViaIgw
#           EcsSecurityGroup:
#             Condition: CreateNewSecurityGroup
#             Type: AWS::EC2::SecurityGroup
#             Properties:
#               GroupDescription: ECS Allowed Ports
#               VpcId: !If [ CreateSubnet1, !Ref Vpc, !Ref VpcId ]
#               SecurityGroupIngress:
#                 IpProtocol: tcp
#                 FromPort: !Ref SecurityIngressFromPort
#                 ToPort: !Ref SecurityIngressToPort
#                 CidrIp: !Ref SecurityIngressCidrIp
#           EcsInstanceLc:
#             Type: AWS::AutoScaling::LaunchConfiguration
#             Condition: CreateWithASG
#             Properties:
#               ImageId: !Ref EcsAmiId
#               InstanceType: !Select [ 0, !Ref EcsInstanceType ]
#               AssociatePublicIpAddress: !If [ IsInheritPublicIp, !Ref "AWS::NoValue", !Ref AutoAssignPublicIp ]
#               IamInstanceProfile: !Ref IamRoleInstanceProfile
#               KeyName: !If [ CreateEC2LCWithKeyPair, !Ref KeyName, !Ref "AWS::NoValue" ]
#               SecurityGroups: [ !If [ CreateNewSecurityGroup, !Ref EcsSecurityGroup, !Ref SecurityGroupId ] ]
#               BlockDeviceMappings:
#                 - !If
#                   - IsConfiguringRootVolume
#                   - DeviceName: !Ref RootDeviceName
#                     Ebs:
#                       VolumeSize: !Ref RootEbsVolumeSize
#                       VolumeType: !Ref EbsVolumeType
#                   - !Ref AWS::NoValue
#                 - !If
#                   - IsConfiguringDataVolume
#                   - DeviceName: !Ref DeviceName
#                     Ebs:
#                       VolumeSize: !Ref EbsVolumeSize
#                       VolumeType: !Ref EbsVolumeType
#                   - !Ref AWS::NoValue
#               UserData:
#                 Fn::Base64: !Ref UserData
#           EcsInstanceAsg:
#             Type: AWS::AutoScaling::AutoScalingGroup
#             Condition: CreateWithASG
#             Properties:
#               VPCZoneIdentifier: !If
#                 - CreateSubnet1
#                 - !If
#                   - CreateSubnet2
#                   - !If
#                     - CreateSubnet3
#                     - [ !Sub "\${PubSubnetAz1}, ${PubSubnetAz2}, ${PubSubnetAz3}" ]
#                     - [ !Sub "${PubSubnetAz1}, ${PubSubnetAz2}" ]
#                   - [ !Sub "${PubSubnetAz1}" ]
#                 - !Ref SubnetIds
#               LaunchConfigurationName: !Ref EcsInstanceLc
#               MinSize: '0'
#               MaxSize: !Ref AsgMaxSize
#               DesiredCapacity: !Ref AsgMaxSize
#               Tags:
#                 -
#                   Key: Name
#                   Value: !Sub "ECS Instance - $${AWS::StackName}"
#                   PropagateAtLaunch: true
#                 -
#                   Key: Description
#                   Value: "This instance is the part of the Auto Scaling group which was created through ECS Console"
#                   PropagateAtLaunch: true
#           EcsSpotFleet:
#             Condition: CreateWithSpot
#             Type: AWS::EC2::SpotFleet
#             Properties:
#               SpotFleetRequestConfigData:
#                 AllocationStrategy: !Ref SpotAllocationStrategy
#                 IamFleetRole: !Ref IamSpotFleetRoleArn
#                 TargetCapacity: !Ref AsgMaxSize
#                 SpotPrice: !If [ CreateWithSpotPrice, !Ref SpotPrice, !Ref 'AWS::NoValue' ]
#                 TerminateInstancesWithExpiration: true
#                 LaunchSpecifications: 
#                     -
#                       IamInstanceProfile:
#                         Arn: !Ref IamRoleInstanceProfile
#                       ImageId: !Ref EcsAmiId
#                       InstanceType: !Select [ 0, !Ref EcsInstanceType ]
#                       KeyName: !If [ CreateEC2LCWithKeyPair, !Ref KeyName, !Ref "AWS::NoValue" ]
#                       Monitoring:
#                         Enabled: true
#                       SecurityGroups:
#                         - GroupId: !If [ CreateNewSecurityGroup, !Ref EcsSecurityGroup, !Ref SecurityGroupId ]
#                       SubnetId: !If
#                               - CreateSubnet1
#                               - !If
#                                 - CreateSubnet2
#                                 - !If
#                                   - CreateSubnet3
#                                   - !Join [ "," , [ !Ref PubSubnetAz1, !Ref PubSubnetAz2, !Ref PubSubnetAz3 ] ]
#                                   - !Join [ "," , [ !Ref PubSubnetAz1, !Ref PubSubnetAz2 ] ]
#                                 - !Ref PubSubnetAz1
#                               - !Join [ "," , !Ref SubnetIds ]
#                       BlockDeviceMappings:
#                             - DeviceName: !Ref DeviceName
#                               Ebs:
#                                VolumeSize: !Ref EbsVolumeSize
#                                VolumeType: !Ref EbsVolumeType
#                       UserData:
#                             Fn::Base64: !Ref UserData
#         Outputs:
#           EcsInstanceAsgName:
#             Condition: CreateWithASG
#             Description: Auto Scaling Group Name for ECS Instances
#             Value: !Ref EcsInstanceAsg
#           EcsSpotFleetRequestId:
#               Condition: CreateWithSpot
#               Description: Spot Fleet Request for ECS Instances
#               Value: !Ref EcsSpotFleet
#           UsedByECSCreateCluster:
#             Description: Flag used by ECS Create Cluster Wizard
#             Value: 'true'
#           TemplateVersion:
#             Description: The version of the template used by Create Cluster Wizard
#             Value: '2.0.0'
# EOT

#     # timeouts {}
# }
