#!/usr/bin/env python3

from aws_cdk import core

from folding_aws.folding_aws_stack import FoldingAwsStack


app = core.App()
FoldingAwsStack(app, "folding-aws")

app.synth()
