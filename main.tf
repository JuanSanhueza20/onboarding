#### provider #####

provider "aws" {
    region = "us-east-1"
}

##### VCP #####


resource "aws_vpc" "main" {
    cidr_block    = "10.1.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true


    tags = {

        Name = "AD_VPC_MAIN"
}
	
}

#### Subnets ####


##### Public Subnet a ######

resource "aws_subnet" "public_a" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.1.10.0/24"
    availability_zone = "us-east-1a"
    map_public_ip_on_launch = true

    tags = {
        Name = "public-a"

}

}


##### Private Subnet a #####

resource "aws_subnet" "private_a" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.1.20.0/24"
    availability_zone = "us-east-1a"

    tags = {
        Name = "private-a"

}

}

##### Private Subnet b #####

resource "aws_subnet" "private_b" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.1.30.0/24"
    availability_zone = "us-east-1b"

    tags = {
        Name = "private-b"

}

}



#### Internet Gateway ####

resource "aws_internet_gateway" "igw" {
    vpc_id     = aws_vpc.main.id

    tags = {
        Name = "public_subnet_igw"

}

}


#### NAT GATEWAY ####

resource "aws_eip" "ip_nat" {
    domain = "vpc"

}

resource "aws_nat_gateway" "nat_gw" {
    allocation_id = aws_eip.ip_nat.id
    subnet_id     = aws_subnet.public_a.id
    
    tags = {
        Name = "NAT_GW"
}

}


#### Route tables ####


##### Public Route Table ####

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "public-rt"
}

}

resource "aws_route" "public_internet" {
   route_table_id  = aws_route_table.public.id
   destination_cidr_block = "0.0.0.0/0"
   gateway_id = aws_internet_gateway.igw.id
}




##### Private Route Table ####

resource "aws_route_table" "private" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "private-rt"
}

}

resource "aws_route" "private_nat" {
   route_table_id  = aws_route_table.private.id
   destination_cidr_block = "0.0.0.0/0"
   nat_gateway_id = aws_nat_gateway.nat_gw.id
   depends_on = [aws_nat_gateway.nat_gw]
}

resource "aws_route" "private_VPN" {
   route_table_id  = aws_route_table.private.id
   destination_cidr_block = "192.168.50.0/24"
   network_interface_id = aws_instance.vpn_bastion.primary_network_interface_id
}

#### Route Tables Associations ####


#### Public Association ####

resource "aws_route_table_association" "public_a" {
    subnet_id        =  aws_subnet.public_a.id
    route_table_id   =  aws_route_table.public.id
}


#### Private Associations ####

resource "aws_route_table_association" "private_a" {
    subnet_id        =  aws_subnet.private_a.id
    route_table_id   =  aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
    subnet_id        =  aws_subnet.private_b.id
    route_table_id   =  aws_route_table.private.id
}


#### Security Groups ####

resource "aws_security_group" "vpn_bastion_sg" {
    name 	             = "vpn-bastion-sg"
    vpc_id 		     = aws_vpc.main.id
  
    ingress {
    description = "Wireguard VPN"
    from_port   = 51820
    to_port     = 51820
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vpn-bastion-sg"
  }
}



### Key Generation ###

resource "aws_key_pair" "bastion_key" {
    key_name           = "bastion-key"
    public_key         = file("claves/wg_key/wireguard-bastion.pub")

}


resource "aws_key_pair" "private_server_key" {
    key_name           = "private_key"
    public_key         = file("claves/private_server_key/server_privado.pub")
}

resource "aws_key_pair" "ad_controller_key"  {
   key_name            = "ad_controller_key"
   public_key          = file("claves/ad_key/ad_controller.pub")
}



##### Instances #####

### Private Server -- Private Subnet ###

resource "aws_instance" "private_server" {
    ami                = "ami-0f3caa1cf4417e51b" ## amazon linux
    instance_type      = "t3.small"
    subnet_id          = aws_subnet.private_b.id
    key_name           = aws_key_pair.private_server_key.key_name
    tags = {
        Name = "Private-server"
}
}


### Private Server --- AD CONTROLLER ###

resource "aws_instance" "ad_controller" {
    ami                = "ami-031283482dcfced88"  ## Windows Server
    instance_type      = "t3.small"
    subnet_id          = aws_subnet.private_a.id
    key_name           = aws_key_pair.ad_controller_key.key_name
   
    tags = {
        Name = "AD_CONTROLLER"
} 

}


### Public Server -- VPN BASTION ###

resource "aws_instance" "vpn_bastion" {
   ami                 = "ami-0f3caa1cf4417e51b" ## amazon linux
   instance_type       = "t3.small"
   subnet_id           = aws_subnet.public_a.id
   source_dest_check   = false
   key_name            = aws_key_pair.bastion_key.key_name
   vpc_security_group_ids = [aws_security_group.vpn_bastion_sg.id]
   user_data           = <<-EOF
			#!/bin/bash
			sysctl -w net.ipv4.ip_forward=1
			echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
			EOF

   tags = {
       Name = "VPN_BASTION"
}
} 



output "bastion_public_ip" { value = aws_instance.vpn_bastion.public_ip}
output "ad_controller_private_ip" { value = aws_instance.ad_controller.private_ip}
output "private_server_ip" {value = aws_instance.private_server.private_ip}




