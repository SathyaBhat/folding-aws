from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_autoscaling as autoscaling

ec2_instance_type = "c5n.large"

class FoldingAsgStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, region: str, vpc: str, ami_id: str, ssh_key: str, max_spot_price: str, ssh_allow_ip_range: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.asg = autoscaling.AutoScalingGroup(self,
                                                "folding-asg",
                                                instance_type=ec2.InstanceType(ec2_instance_type),
                                                machine_image=ec2.MachineImage.generic_linux( ami_map = {region: ami_id}
                                                ),
                                                vpc=vpc,
                                                key_name=ssh_key,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                                allow_all_outbound=True,
                                                associate_public_ip_address=True,
                                                min_capacity=2,
                                                max_capacity=2,
                                                spot_price=max_spot_price
                                                )
        sg_ssh_in = ec2.SecurityGroup(self, 
                                    "allow-ssh",
                                    vpc=vpc,
                                    allow_all_outbound=True)
        sg_ssh_in.add_ingress_rule(ec2.Peer.ipv4(ssh_allow_ip_range),
                                    ec2.Port.tcp(22)
                                )

        self.asg.add_security_group(sg_ssh_in)
