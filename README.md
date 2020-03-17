# securiCAD Vanguard SDK
> Automated threat modeling and attack simulations in your CI/CD pipeline

A python SDK for [foreseeti's securiCAD Vanguard](https://foreseeti.com/securicad-vanguard-for-aws/). Sign up for an account at [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B08424ZMPS).

## Getting started

### Sign up for a securiCAD Vanguard account
Go to [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B08424ZMPS) and sign up to securiCAD Vanguard and verify your account.

### Download and setup the SDK
Clone this repository and install the required third-party libraries.
```shell
git clone https://github.com/foreseeti/securicad-vanguard-sdk.git
cd securicad-vanguard-sdk
pip install -r requirements.txt
```

### Get the required AWS credentials
The securiCAD Vanguard SDK requires AWS credentials to be able to fetch data from AWS and run the simulations on your environment. The easiest way is to create an IAM User with the required permissions and generate access keys for that IAM User:
* [Create an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) with this [IAM policy](https://vanguard.securicad.com/iam_policy.json)
* [Generate access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for the IAM user

Cross-account role access and local model generation will be available soon.

### Run your first simulation
The following snippet runs a simulation on an AWS environment where the high value asset is an EC2 instance with id `i-1a2b3c4d5e6f7` and prints the results. Please note, never store your credentials in source code, this is just an example.
```python
import vanguard

# Your vanguard credentials
email = "your vanguard email"
password = "your vanguard password"

# AWS credentials for IAM user 
access_key = "aws access key id"
secret_key = "aws secret key"
region = "your aws region" # e.g., us-east-1

# Create an authenticated vanguard client
client = vanguard.client(username=email, password=password)

# Generate a model from your AWS environment
model = client.get_model(access_key=access_key, secret_key=secret_key, region=region)

# Set high value assets
model.set_high_value_assets(instances=["i-1a2b3c4d5e6f7"])

# Simulate and print the results
results = client.simulate(model, profile=vanguard.Profile.CYBERCRIMINAL)
print(results)

```

If you wish to run securiCAD Vanguard with a local file, replace the `client.get_model()` call in the above example with:

```python
import json

with open('data.json', 'r') as json_file:
    data = json.load(json_file)
    model = client.get_model(data=data)

```

The results will be returned as a `dict` with your high value asset identifiers as keys. For example:
```json
{
    "buckets": {},
    "dbinstances": {},
    "instances": {
        "i-1a2b3c4d5e6f7": {
            "object_name": "web-server",
            "probability": 0.5,
            "ttc": 59
        }
    }
}
```
Check out `example.py` for a more detailed example.

## Examples
Below are a few examples of how you can use `boto3` to automatically collect name or ids for your high value assets.

### Get EC2 instance ids
Get all EC2 instance ids where the instance is running and has the tag `owner` with value `erik`.

```python
import boto3

session = boto3.Session()
ec2 = session.resource('ec2')

# List all running EC2 instances with the owner-tag erik
instances = ec2.instances.filter(
    Filters=[
        {"Name": "tag:owner", "Values": ["erik"]},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
)
# Get the instance-id of each filtered instance
instance_ids = [instance.id for instance in instances]

```

### Get RDS instance identifiers
Get all RDS instances and their identifiers.

```python
import boto3

session = boto3.Session()
rds = session.client('rds')

# Get all RDS instance identifers with a paginator
dbinstances = []
paginator = rds.get_paginator('describe_db_instances').paginate()
for page in paginator:
    for db in page.get('DBInstances'):
        dbinstances.append(db['DBInstanceIdentifier'])

```

### Get S3 buckets
Get all S3 buckets where the bucket name contains the string `erik`.

```python
import boto3

session = boto3.Session()
s3 = session.resource('s3')

# Get all s3 buckets where `erik` is in the bucket name
buckets = []
for bucket in s3.buckets.all():
    if 'erik' in bucket.name:
        buckets.append(bucket.name)

```

## Links

Additional information can be found at:

- About [foreseeti](https://foreseeti.com/)
- securiCAD Vanguard on [AWS Marketplace](https://aws.amazon.com/marketplace/pp/foreseeti-securiCAD-Vanguard/B08424ZMPS)
- Related projects:
  - [https://mal-lang.org/](https://mal-lang.org/)

## Licensing

"The code in this project is licensed under Apache-2.0."
