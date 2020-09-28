#creating security group
resource "aws_security_group" "docker-host-ssh" {
  name        = "docker-host-ssh"
  description = "allow ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}


#creating aws instance
resource "aws_instance" "docker-host" {
  ami               = data.aws_ami.ubuntu.id
  instance_type     = "t2.micro"
  availability_zone = "us-west-1a"
  security_groups   = ["${aws_security_group.docker-host-ssh.name}"]
  key_name          = "sq_aws"
  user_data = <<-EOF
#! /bin/bash
sudo apt-get -y update
sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get -y update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io
u=`whoami`
sudo usermod -aG docker "$u"
EOF

  tags = {
        Name = "docker-host"
  }

}

# creating and attaching ebs volume

resource "aws_ebs_volume" "docker-host-data-vol" {
 availability_zone = "us-west-1a"
 size = 20
 tags = {
        Name = "docker-host"
 }

}
#
resource "aws_volume_attachment" "docker-host-vol" {
 device_name = "/dev/xvdf"
 volume_id = aws_ebs_volume.docker-host-data-vol.id
 instance_id = aws_instance.docker-host.id
}