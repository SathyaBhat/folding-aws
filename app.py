#!/usr/bin/env python3

from aws_cdk import core

from aws_stack.vpc_stack import VpcStack
from aws_stack.asg_stack import AsgStack
import yaml
from botocore import client
import boto3
import sys
from datetime import datetime
from datetime import timedelta
import logging

feature_query_spot_prices_disabled = True


def configure(stack_name: str):
    logging.debug("Processing the configuration file")
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
        logging.error("Failed parsing the configuration file, exiting", exc)
        sys.exit(1)
    except OSError as exc:
        logging.error("Unable to read configuration file, exiting", exc)
        sys.exit(1)
    # Deep merging should be done better. The moment we need more
    # parameters, this will need to be fixed
    logging.debug("Read configuration file, merging with defaults")
    config = {stack_name: {
        **defaults[stack_name],
        **user_config[stack_name],
    }
    }
    return config[stack_name]


def get_all_azs(region: str, client: client.BaseClient) -> list:
    logging.debug(f"Getting a list of all Availability Zones in current region {region}")
    all_azs_info = client.describe_availability_zones(Filters=[{'Name': 'region-name', 'Values': [region]}])
    all_azs = [az['ZoneName'] for az in all_azs_info['AvailabilityZones']]
    if len(all_azs) == 0:
        logging.error(f"Could not find any Availability Zone in region {region}. \
    Please check AWS configuration and whether this region is enabled for you")
        sys.exit(1)
    return all_azs


def get_current_spot_price_from_api(region: str, ec2_instance_type: str) -> float:
    logging.debug(f"Getting the current spot prices for all AZs in {region} for {ec2_instance_type}")
    ec2 = boto3.client('ec2', region_name=region)
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    spot_prices_by_az = {}
    for az in get_all_azs(region, ec2):
        curr_az_price_history = ec2.describe_spot_price_history(AvailabilityZone=az,
                                                                InstanceTypes=[ec2_instance_type],
                                                                ProductDescriptions=['Linux/UNIX'],
                                                                StartTime=yesterday, EndTime=now)[
            'SpotPriceHistory']
        logging.debug(f"Retrieved spot price for {ec2_instance_type} in {region} since {yesterday}")
        spot_price_history = [x['SpotPrice'] for x in curr_az_price_history]
        spot_price_history.sort(reverse=True)
        spot_prices_by_az[az] = spot_price_history[0]
    logging.info(f"Got spot price: {max(spot_prices_by_az.values())}")
    return max(spot_prices_by_az.values())


def process_spot_pricing(max_spot_price: str,
                         region: str,
                         ec2_instance_type: str,
                         asg_size: str) -> str:
    logging.debug("force_spot_price is not set, fetching current spot prices and asking the user for consent")
    bid_raise: float = 0.02

    max_current_spot_price = float(get_current_spot_price_from_api(region=region,
                                                                   ec2_instance_type=ec2_instance_type))
    proposed_max_spot_price = max_current_spot_price
    if max_spot_price == "" or proposed_max_spot_price > float(max_spot_price):
        proposed_max_spot_price = max_current_spot_price + bid_raise
        if max_spot_price == "":
            print("You have not specified a maximum price to pay for the Spot Instances.")
        else:
            print(
                f"Your current specified maximum price ({max_spot_price}) is "
                f"lower than the current spot price {str(max_current_spot_price)}")
        print(f"Are you willing to pay {proposed_max_spot_price} US Dollars / hour for each instance? "
              f"Note: You have requested for {asg_size} instances of type {ec2_instance_type}.")
        try:
            user_consent = input("y/N: ")
            logging.debug(f"Received user input {user_consent}")
        except EOFError as exc:
            logging.error(f"Ran into error, ", exc)
            sys.exit(1)
        if not (user_consent.lower() == "y" or user_consent.lower == "yes"):
            print("Exiting because the proposed spot price is not acceptable.")
            sys.exit(1)
        # The yaml file as well as ASG require the spot price to be a string
        max_spot_price = str(proposed_max_spot_price)
        # Update max_spot_price in config file
        logging.info("Attempting to update config file with the chosen spot price")
        try:
            # We read the config file again because the current config hash is created by
            # merging the default hash with the user config hash
            with open('config.yaml', 'w') as f:
                user_config = yaml.safe_load(f)
                user_config['aws']['max_spot_price'] = max_spot_price
                yaml.dump(user_config, f)
            logging.debug("Updated config file")
        except OSError as exc:
            print("Updating config file failed, proceeding to set up ASG ", exc)
    logging.info(f"Using spot price {max_spot_price}")
    return max_spot_price


def cdk_init(stack_name: str, force_spot_price: bool):
    config = configure(stack_name)
    if (not force_spot_price) or (feature_query_spot_prices_disabled):
        config['max_spot_price'] = process_spot_pricing(max_spot_price=config['max_spot_price'],
                                                        region=config['region'],
                                                        ec2_instance_type=config['ec2_instance_type'],
                                                        asg_size=config['asg_size'])
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
                         env=core.Environment(region=config['region'])
                         )

    for tag in tags:
        core.Tag.add(asg_stack, tag.get('name'), tag.get('value'))
        core.Tag.add(vpc_stack, tag.get('name'), tag.get('value'))

    app.synth()


if __name__ == "__main__":
    logging.debug("In __main__")
    app = core.App()
    stack_name = app.node.try_get_context("stack_name")

    if stack_name is None:
        logging.error("Please pass a stack name using -c <stack name>")
        sys.exit(1)

    force_spot_price = app.node.try_get_context("force_spot")
    if force_spot_price:
        logging.error("Force Spot price flag is set, will auto fetch spot price")

    logging.debug("Parsed all command line parameters")
    cdk_init(stack_name, force_spot_price)
