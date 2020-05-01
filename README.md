
# Folding on AWS

This is a CDK project which configures a 2-instance ASG. The ASG is pointed to an AMI which is pre-configured to run [Folding@Home](https://foldingathome.org/)

This is a blank project for Python development with CDK.


### How to run

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
