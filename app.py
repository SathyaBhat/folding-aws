#!/usr/bin/env python3

from aws_cdk import core

from folding_aws.folding_vpc_stack import FoldingVpcStack
from folding_aws.folding_asg_stack import FoldingAsgStack


app = core.App()
vpc_stack = FoldingVpcStack(app, "folding-vpc", env=core.Environment(region="eu-west-1"))
asg_stack = FoldingAsgStack(app, "folding-asg", vpc=vpc_stack.vpc, env=core.Environment(region="eu-west-1"))
app.synth()
