import json
from securicad import vanguard

# Vanguard credentials
email = "your vanguard email"
password = "your vanguard password"

# AWS credentials
access_key = "aws access key id"
secret_key = "aws secret key"
region = "your aws region"

# Create an authenticated vanguard client
client = vanguard.client(username=email, password=password)

# Generate a model from your AWS environment
model = client.get_model(access_key=access_key, secret_key=secret_key, region=region)

# Set high value assets in the model
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
