#!/usr/bin/env python3

from aws_cdk import core

from folding_aws.folding_vpc_stack import FoldingVpcStack
from folding_aws.folding_asg_stack import FoldingAsgStack
import sys
import yaml
import argparse


def configure():
    defaults = {"aws": {
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
    config = {"aws": {**defaults['aws'], **user_config['aws']}}
    return config


def cdk_init(config: dict, force_spot_price: bool):
    app = core.App()
    vpc_stack = FoldingVpcStack(app, "folding-vpc", env=core.Environment(region=config['aws']['region']))
    asg_stack = FoldingAsgStack(app, "folding-asg",
                                region=config['aws']['region'],
                                vpc=vpc_stack.vpc,
                                ec2_instance_type=config['aws']['ec2_instance_type'],
                                ami_id=config['aws']['ami_id'],
                                ssh_key=config['aws']['ssh_key'],
                                max_spot_price=config['aws']['max_spot_price'],
                                ssh_allow_ip_range=config['aws']['ssh_allow_ip_range'],
                                asg_size=config['aws']['asg_size'],
                                force_spot_price=force_spot_price,
                                env=core.Environment(region=config['aws']['region']))
    app.synth()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage a Folding@Home EC2 stack")
    parser.add_argument('--force', action="store_true",
                        help="Use the spot price specified in config file, do not query AWS for current spot prices")
    args = parser.parse_args()
    cdk_init(configure(), args['force'])
