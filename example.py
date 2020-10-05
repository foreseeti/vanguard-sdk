import json
import sys

from securicad import vanguard
from securicad.vanguard.exceptions import VanguardException


# Vanguard credentials
email = "your vanguard email"
password = "your vanguard password"

# AWS credentials
access_key = "aws access key id"
secret_key = "aws secret key"
region = "your aws region"

try:
    # Create an authenticated vanguard client and catch invalid Vanguard credentials
    client = vanguard.client(username=email, password=password)

    # Generate a model from your AWS environment and catch invalid AWS credentials
    model = client.get_model(access_key=access_key, secret_key=secret_key, region=region)

    # Set high value assets in the model
    # Check that model has at least one high value asset
    # Supported asset types are EC2 instances, S3 buckets and RDS databases
    model.set_high_value_assets(
        instances=["instance-id-1", "instance-id-2"],
        buckets=["bucket_name"],
        dbinstances=["db-instance-identifier"],
    )

    # Start the simulation and wait for the results
    # Supported Profiles are: STATESPONSORED, CYBERCRIMINAL and OPPORTUNIST
    results = client.simulate(model, profile=vanguard.Profile.CYBERCRIMINAL)

    print(json.dumps(results, indent=2))
except VanguardException as e:
    sys.exit(e)
