from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_autoscaling as autoscaling
from botocore import client
import boto3
import sys
from datetime import datetime
from datetime import timedelta
import yaml

bid_raise: float = 0.02


class FoldingAsgStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 region: str,
                 vpc: str,
                 ec2_instance_type: str,
                 ami_id: str,
                 ssh_key: str,
                 max_spot_price: str,
                 ssh_allow_ip_range: str,
                 asg_size: str,
                 force_spot_price: bool,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if not force_spot_price:
            max_current_spot_price = float(self.get_current_spot_price(region=region,
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
                print(f"Are you willing to pay {proposed_max_spot_price} US Dollars / hour for each instance?"
                      f"Note: You have requested for {asg_size} instances of type {ec2_instance_type}.")
                user_consent = input("y/N: ")
                if not (user_consent.lower() == "y" or user_consent.lower == "yes"):
                    sys.exit(1)
                # The yaml file as well as ASG require the spot price to be a string
                max_spot_price = str(proposed_max_spot_price)
                # Update max_spot_price in config file
                print("Attempting to update config file with the chosen spot price")
                try:
                    # We read the config file again because the current config hash is created by
                    # merging the default hash with the user config hash
                    with open('config.yaml', 'w') as f:
                        user_config = yaml.safe_load(f)
                        user_config['aws']['max_spot_price'] = max_spot_price
                        yaml.dump(user_config, f)
                except OSError as exc:
                    print("Updating config file failed, proceeding to set up ASG ", exc)

        self.asg = autoscaling.AutoScalingGroup(self,
                                                "folding-asg",
                                                instance_type=ec2.InstanceType(ec2_instance_type),
                                                machine_image=ec2.MachineImage.generic_linux(ami_map={region: ami_id}
                                                                                             ),
                                                vpc=vpc,
                                                key_name=ssh_key,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                                allow_all_outbound=True,
                                                associate_public_ip_address=True,
                                                min_capacity=asg_size,
                                                max_capacity=asg_size,
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

    def get_all_azs(self, region: str, client: client.BaseClient) -> list:
        all_azs_info = client.describe_availability_zones(Filters=[{'Name': 'region-name', 'Values': [region]}])
        all_azs = [az['ZoneName'] for az in all_azs_info['AvailabilityZones']]
        if len(all_azs) == 0:
            print(f"Could not find any Availability Zone in region {region}. \
        Please check AWS configuration and whether this region is enabled for you")
            sys.exit(1)
        return all_azs

    def get_current_spot_price(self, region: str, ec2_instance_type: str) -> float:
        ec2 = boto3.client('ec2')
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        spot_prices_by_az = {}
        for az in self.get_all_azs(region, ec2):
            curr_az_price_history = ec2.describe_spot_price_history(AvailabilityZone=az,
                                                                    InstanceTypes=[ec2_instance_type],
                                                                    ProductDescriptions=['Linux/UNIX'],
                                                                    StartTime=yesterday, EndTime=now)[
                'SpotPriceHistory']
            spot_price_history = [x['SpotPrice'] for x in curr_az_price_history]
            spot_price_history.sort(reverse=True)
            spot_prices_by_az[az] = spot_price_history[0]
        return max(spot_prices_by_az.values())
