
# Folding on AWS

This is a CDK project which configures a 2-instance ASG. The ASG is pointed to an AMI which is pre-configured to run [Folding@Home](https://foldingathome.org/), which can be generated using `packer`.

## How to run

### Preparing the AMI

- Install [packer](https://www.packer.io/intro/getting-started/install.html)
- Generate [AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)
- Set the following variables in your shell's environment: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- Change into the `packer` sub directory: `cd packer`
- Build the Folding at Home Amazon Machine Image that will be used to create the virtual machines
      
      packer build -var 'fah_user=your_username' -var 'fah_passkey=your_passkey' \
                  -var 'fah_team=your_team_id' fah_ami.json

- From the output of the above command, copy the generated AMI's Id for use later

### Configuring the stack

- Install [CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#python)
- Setup a venv with 
        
        python3 -m venv .env
        
- Activate the venv

        source .env/bin/activate

- Install the dependencies

        pip install -r requirements.txt

- Copy the `config.sample.yaml` file to `config.yaml` and set the appropriate values
- Show the cloudformation template

        cdk synth <stack name>
        cdk synth folding-vpc

- Or just deploy 
 
        cdk deploy <stack name>
        cdk deploy folding-vpc
        cdk deploy folding-asg
