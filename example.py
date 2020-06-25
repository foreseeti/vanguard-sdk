import json
import sys

from securicad import vanguard
from securicad.vanguard.exceptions import (
    VanguardCredentialsError,
    AwsCredentialsError,
    HighValueAssetError,
)


# Vanguard credentials
email = "your vanguard email"
password = "your vanguard password"

# AWS credentials
access_key = "aws access key id"
secret_key = "aws secret key"
region = "your aws region"

# Create an authenticated vanguard client and catch invalid Vanguard credentials
try:
    client = vanguard.client(username=email, password=password)
except VanguardCredentialsError as e:
    sys.exit(e)

# Generate a model from your AWS environment and catch invalid AWS credentials
try:
    model = client.get_model(access_key=access_key, secret_key=secret_key, region=region)
except AwsCredentialsError as e:
    sys.exit(e)


# Set high value assets in the model
# Check that model has at least one high value asset
# Supported asset types are EC2 instances, S3 buckets and RDS databases

try:
    model.set_high_value_assets(
        instances=["instance-id-1", "instance-id-2"],
        buckets=["bucket_name"],
        dbinstances=["db-instance-identifier"],
    )
except HighValueAssetError as e:
    sys.exit(e)

# Start the simulation and wait for the results
# Supported Profiles are: STATESPONSORED, CYBERCRIMINAL and OPPORTUNIST
results = client.simulate(model, profile=vanguard.Profile.CYBERCRIMINAL)

print(json.dumps(results, indent=2))
