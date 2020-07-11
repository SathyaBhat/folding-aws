#!/usr/bin/env python3

from aws_cdk import core

from aws_stack.vpc_stack import VpcStack
from aws_stack.asg_stack import AsgStack
import sys
import os
import yaml
import argparse


def configure(stack_name: str):
  defaults = {   
                stack_name: {
                  "region": "us-east-1",
                  "ec2_instance_type": "c5n.large",
                  "asg_size": 2,
                  "max_spot_price": "",
                }
             }

  try:
      with open("config.yaml") as f:
          user_config = yaml.safe_load(f)
  except yaml.YAMLError as exc:
      print("Failed parsing the configuration file, exiting", exc)
      sys.exit(1)
  except OSError as exc:
      print("Unable to read configuration file, exiting", exc)
      sys.exit(1)
    # Deep merging should be done better. The moment we need more
    # parameters, this will need to be fixed
  config = { stack_name : {
                            **defaults[stack_name], 
                            **user_config[stack_name],
                          }
          }
  return config[stack_name]

def cdk_init(stack_name: str, force_spot_price: bool):
  config = configure(stack_name)
  tags = config.get('tags')
  vpc_stack = VpcStack(app, 
                      f"{stack_name}-vpc",
                      cidr=config['cidr'],
                      env=core.Environment(region=config['region'],
                      )
                    )
  asg_stack = AsgStack(app, 
                    f"{stack_name}-asg", 
                    stack_name=stack_name,
                    region=config['region'], 
                    vpc=vpc_stack.vpc, 
                    ec2_instance_type=config['ec2_instance_type'], 
                    ami_id=config['ami_id'],
                    ssh_key=config['ssh_key'], 
                    max_spot_price=config['max_spot_price'],
                    ssh_allow_ip_range=config['ssh_allow_ip_range'],
                    asg_size=config['asg_size'],
                    force_spot_price=force_spot_price,
                    env=core.Environment(region=config['region'])
                  )
  
  for tag in tags:
    core.Tag.add(asg_stack, tag.get('name'), tag.get('value'))  
    core.Tag.add(vpc_stack, tag.get('name'), tag.get('value'))

  app.synth()


if __name__ == "__main__":
  app = core.App()
  stack_name = app.node.try_get_context("stack_name")
  
  if stack_name is None:
    print("Please pass a stack name using -c <stack name>")
    sys.exit(1)
  
  force_spot_price = app.node.try_get_context("force_spot")
  if force_spot_price:
    print("Force Spot price flag is set, will auto fetch spot price")

  cdk_init(stack_name, force_spot_price)
