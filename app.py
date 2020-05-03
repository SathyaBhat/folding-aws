#!/usr/bin/env python3

from aws_cdk import core

from folding_aws.folding_vpc_stack import FoldingVpcStack
from folding_aws.folding_asg_stack import FoldingAsgStack
import sys
import yaml

try:
  with open("config.yaml") as f:
    config = yaml.safe_load(f)
except yaml.YAMLError as exc:
  print("Failed parsing the configuration file, exiting", exc)
  sys.exit(1)
except OSError as exc:
  print("Unable to read configuration file, exiting", exc)
  sys.exit(1)

app = core.App()
vpc_stack = FoldingVpcStack(app, "folding-vpc", env=core.Environment(region=config['aws']['region']))
asg_stack = FoldingAsgStack(app, "folding-asg", region=config['aws']['region'], vpc=vpc_stack.vpc, 
                              ec2_instance_type=config['aws']['ec2_instance_type'], ami_id=config['aws']['ami_id'],
                              ssh_key=config['aws']['ssh_key'], max_spot_price=config['aws']['max_spot_price'],
                              ssh_allow_ip_range=config['aws']['ssh_allow_ip_range'],
                              env=core.Environment(region=config['aws']['region']))
app.synth()
