# securiCAD Vanguard SDK

> Automated threat modeling and attack simulations in your CI/CD pipeline

A Python SDK for [foreseeti's securiCAD Vanguard](https://foreseeti.com/securicad-vanguard-for-aws/).
Sign up for an account at [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B08424ZMPS).

## Getting started

### Sign up for a securiCAD Vanguard account

Go to [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B08424ZMPS) and sign up to securiCAD Vanguard and verify your account.

### Download and setup the SDK

Install `securicad-vanguard` with pip:

```shell
pip install securicad-vanguard
```

### Get the required AWS credentials

The securiCAD Vanguard SDK requires AWS credentials to be able to fetch data from AWS and run the simulations on your environment.
The easiest way is to create an IAM User with the required permissions and generate access keys for that IAM User:

* [Create an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) with this [IAM policy](https://vanguard.securicad.com/iam_policy.json)
* [Generate access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for the IAM user

Cross-account role access and local model generation will be available soon.

### Run your first simulation

The following snippet runs a simulation on an AWS environment where the high value asset is an EC2 instance with id `i-1a2b3c4d5e6f7` and prints the results.
Please note, never store your credentials in source code, this is just an example.

```python
import json

from securicad import vanguard
from securicad.vanguard import Profile

# Your vanguard credentials
email = "your vanguard email"
password = "your vanguard password"

# AWS credentials for IAM user
access_key = "aws access key id"
secret_key = "aws secret key"
region = "your aws region"  # e.g., us-east-1

# Create an authenticated vanguard client
client = vanguard.client(username=email, password=password)

# Generate a model from your AWS environment
model = client.get_model(access_key=access_key, secret_key=secret_key, region=region)

# Set high value assets in the model
client.set_high_value_assets(model, instances=["i-1a2b3c4d5e6f7"])

# Simulate and print the results
results = client.simulate(model, profile=Profile.CYBERCRIMINAL)
print(json.dumps(results, indent=2))
```

If you wish to run securiCAD Vanguard with a local file, replace the `model = client.get_model()` call in the above example with:

```python
with open('data.json', mode='r', encoding='utf-8') as json_file:
    aws_data = json.load(json_file)
model = client.get_model(data=aws_data)
```

The results will be returned as a `dict` with your high value asset identifiers as keys and sorted under object type. For example:

```json
{
  "EC2Instance": {
    "i-1a2b3c4d5e6f7": {
      "metaconcept": "EC2Instance",
      "attackstep": "HighPrivilegeAccess",
      "name": "web-server",
      "consequence": 10,
      "probability": 0.65,
      "ttc": 42
    }
  }
}
```

Check out `example.py` for a more detailed example.

## High value assets

The securiCAD Vanguard SDK features a set of predefined parameters for settings high value assets for certain AWS services as well as a more comprehensive option.

### Predefined parameters

Predefined parameters can be used to set high value assets in a model with the function `client.set_high_value_assets()`

- **EC2 instances**
Use the `instances` parameter to set a list of EC2 instance ids as high value assets.
For example: `instances=["i-1a2b3c4d5e6f", "i-9i8u7y6t5r4e"]`

- **S3 buckets**
Use the `buckets` parameter to set a list of S3 bucket names as high value assets.
For example: `buckets=["vanguard/bucket1", "vanguard/bucket2"]`

- **RDS instances**
Use the `dbinstances` parameter to set a list of RDS db instance identifers as high value assets.
For example: `dbinstances=["aurora-db-instance"]`

- **DynamoDB tables**
Use the `dynamodb_tables` parameter to set a list of dynamodb table names as high value assets.
For example: `dynamodb_tables=["vanguardTable"]`

### Advanced

Any object and attack step in the model can be set as a high value asset but it requires knowledge about the underlying model and concepts.
Use `client.set_high_value_assets()` with the `high_value_assets` parameter and set your high value assets by specifying the object type `metaconcept`, object identifier `id` and target `attackstep` as a list of dicts:

```python
high_value_assets = [
    {
        "metaconcept": "EC2Instance",
        "attackstep": "HighPrivilegeAccess",
        "consequence": 7,
    },
    {
        "metaconcept": "DynamoDBTable",
        "attackstep": "AuthenticatedRead",
        "id": {
            "type": "name",
            "value": "VanguardTable",
        },
    },
    {
        "metaconcept": "S3Bucket",
        "attackstep": "AuthenticatedWrite",
        "id": {
            "type": "tag",
            "key": "arn",
            "value": "arn:aws:s3:::my_corporate_bucket/",
        },
    },
]

# Set high value assets in securiCAD model
client.set_high_value_assets(model, high_value_assets=high_value_assets)
```

`id` is used to match objects in the model with the high value assets.
The supported `type` are currently `name` and `tag`.
Omitting the `id` parameters will set all assets of that type as a high value asset.
Omitting `consequence` will automatically set it to `10`.

## Vulnerability data and vulnerabilities

securiCAD Vanguard supports vulnerability data from third parties in combination with the AWS data.
Typical examples are vulnerability scanners, static code analysis and dependency managers.
Vulnerability data can be used to simulate the impact of known vulnerabilities in your AWS environment.

If you wish to run the simulation with third party vulnerability data, include the the `vuln_data` parameter for `client.get_model()`.

```python
model = client.get_model(
    access_key=access_key, secret_key=secret_key, region=region, vuln_data=data
)
```

The expected `vuln_data` format is explained below.

### Vulnerability data format

securiCAD Vanguard supports any type of vulnerability data by using a generic json format.
The json file should be a list of `findings` that describes each finding from e.g., a vulnerability scanner.
All fields are mandatory and validated, but some can be left empty.
See the example below for a practical example of a finding of `CVE-2018-11776` on a specific EC2 instance.
`"cve"`, `"cvss"` and `"id"` (instance-id) are always mandatory.
If the application is not listening on any port, you can set `"port"` to `0`.

```json
{
  "findings": [
    {
      "id": "i-1a2b3c4d5e6f7",
      "ip": "",
      "dns": "",
      "application": "Apache Struts 2.5.16",
      "port": 80,
      "name": "CVE-2018-11776",
      "description": "Apache Struts versions 2.3 to 2.3.34 and 2.5 to 2.5.16 suffer from possible Remote Code Execution when alwaysSelectFullNamespace is true",
      "cve": "CVE-2018-11776",
      "cwe": "",
      "cvss": [
        {
          "version": "3.0",
          "score": 8.1,
          "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        }
      ]
    }
  ]
}
```

### Vulnerabilities in the simulation

securiCAD Vanguard uses the [CVSS vector](https://www.first.org/cvss/v3.1/specification-document) of a [CVE](https://cve.mitre.org/about/faqs.html#what_is_cve) to asses the impact of a vulnerability in the context of your AWS environment.
For example, a CVE with `AV:L` is only exploitabe with local access and not via network access.
`AC:H` will require more effort from the attacker compared to `AC:L` and `PR:H` will require the attacker to have high privilege access before being able to exploit the vulnerability in the simulation.
The impact of the vulnerability is decided based on the `C/I/A` part of the vector.

`CVSS:2.0` vectors are automatically converted to `CVSS:3` by the tool and if multiple versions are available, the tool will always select the latest one.

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

## License

Copyright © 2020-2021 [Foreseeti AB](https://foreseeti.com)

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
