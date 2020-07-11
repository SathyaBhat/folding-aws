
# Folding on AWS

This is a CDK project which configures a multi-instance ASG. As an example, there are two sets of configs predefined: the first config creates a two-node ASG pointed to an AMI which is pre-configured to run [Folding@Home](https://foldingathome.org/), while the second config is for a single-node ASG running a base install of Ubuntu with some extras (check [packer/generic_base cvonfig](/packer/generic_base.json) for details) 

The AMIs are configured and built using [HashiCorp's Packer](https://www.packer.io/). These AMIs can then be updated in the config file.

## How to run

### Preparing the AMI

- Install [packer](https://www.packer.io/intro/getting-started/install.html)
- Generate [AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)
- Set the following variables in your shell's environment: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- Change into the `packer` sub directory: `cd packer`
- Build the Folding at Home Amazon Machine Image that will be used to create the virtual machines
      
      packer build -var 'fah_user=your_username' -var 'fah_passkey=your_passkey' \
                  -var 'fah_team=your_team_id' fah_ami.json

- If you have the `jq` program installed, the packer build will attempt to set the AMI ID in `config.yaml` automatically. If not, please edit the `config.yaml` and set the AMI ID as well as other parameters.

### Configuring the stack

- Install [CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#python)
- Setup a venv with 
        
        python3 -m venv .env
        
- Activate the venv

        source .env/bin/activate

- Install the dependencies

        pip install -r requirements.txt

- Copy the `config.sample.yaml` file to `config.yaml` and set the appropriate values. Additional documentation is available in the sample configuration file. The `config.yaml` supports multiple configuration sets, each denoted by the root key. To deploy a specific config, we use the `context` feature of CDK.

For example, if you want to create different config sets with different regions and VPCs, the config will look like below

```
everything:
  region: eu-west-1
  cidr: 10.1.0.0/22

folding:
  region: us-east-1
  cidr: 10.0.0.0/16
```

The root keys, `everything` and `folding` will have to be passed as `context` when working with CDK, The VPC and ASG stacks created will have the root key as a prefix.

- Show the cloudformation template

        cdk synth <stack name> -c stack_name=<config-name>
        cdk synth folding-vpc -c stack_name=folding

- Or just deploy 
 
        cdk deploy <stack names> -c stack_name=<config-name>
        cdk deploy folding-vpc folding-asg -c stack_name=folding
