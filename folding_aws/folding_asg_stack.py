from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_autoscaling as autoscaling

ec2_instance_type = "c5n.large"
key_name = "sathya_folding_ssh"
ami = ec2.MachineImage.generic_linux(ami_map = {
                                            'eu-west-1':'ami-0a8341e7c0a146e7f'
                                            }
                                    )

class FoldingAsgStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.asg = autoscaling.AutoScalingGroup(self,
                                                "folding-asg",
                                                instance_type=ec2.InstanceType(ec2_instance_type),
                                                machine_image = ami,
                                                vpc=vpc,
                                                key_name=key_name,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                                allow_all_outbound=True,
                                                associate_public_ip_address=True,
                                                min_capacity=2,
                                                max_capacity=2,
                                                spot_price="0.045"
                                                )
        sg_ssh_in = ec2.SecurityGroup(self, 
                                    "allow-ssh",
                                    vpc=vpc,
                                    allow_all_outbound=True)
        sg_ssh_in.add_ingress_rule(ec2.Peer.ipv4("188.26.173.155/32"),
                                    ec2.Port.tcp(22)
                                )

        self.asg.add_security_group(sg_ssh_in)