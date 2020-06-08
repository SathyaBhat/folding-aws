from aws_cdk import core
import aws_cdk.aws_ec2 as ec2


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, cidr: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, "vpc",
                           max_azs=2,
                           cidr=cidr,
                           subnet_configuration=[ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name="Public"
                           ), ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.ISOLATED,
                               name="Private"
                           )
                           ],
                           nat_gateways=0,
                           )
        core.CfnOutput(self, "Output",
                       value=self.vpc.vpc_id)