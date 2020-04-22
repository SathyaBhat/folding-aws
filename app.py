#!/usr/bin/env python3

from aws_cdk import core

from folding_aws.folding_aws_stack import FoldingVpcStack


app = core.App()
FoldingVpcStack(app, "folding-vpc", env=core.Environment(region="eu-west-1"))

app.synth()
