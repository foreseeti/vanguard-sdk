# Copyright 2020 Foreseeti AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import json
import time
import math
import base64

import requests

from vanguard.model import Model

try:
    from pycognito.aws_srp import AWSSRP
except ModuleNotFoundError as e:
    sys.exit(f"You need pycognito to run this script: {e}")

try:
    import boto3
    import botocore
    from botocore.config import Config
except ModuleNotFoundError as e:
    sys.exit(f"You need boto3 and botocore to run this script: {e}")


class Client:
    def __init__(self, username, password, url, region="eu-central-1"):
        self.base_url = url
        self.backend_url = f"{self.base_url}/backend"
        self.token = self.authenticate(username, password, region)
        self.headers = {"Authorization": self.token}

    def simulate(self, model, profile):
        if not model.result_map:
            raise ValueError("Model must have at least one high value asset")
        simulation_tag = self.simulate_model(model.model, profile.value)
        results = self.wait_for_results(simulation_tag)
        return self.parse_results(results, model)

    def get_model(self, **kwargs):
        if kwargs.get("data"):
            model_tag = self.build_from_config(kwargs.get("data"))
        else:
            model_tag = self.build_from_role(
                kwargs.get("access_key"), kwargs.get("secret_key"), kwargs.get("region")
            )
        model = self.wait_for_model(model_tag)
        return Model(model)

    def authenticate(self, username, password, region):
        client = boto3.client(
            "cognito-idp",
            region_name=region,
            config=Config(signature_version=botocore.UNSIGNED),
        )
        client_id, pool_id = self.cognito_params(region)
        aws = AWSSRP(
            username=username,
            password=password,
            pool_id=pool_id,
            client_id=client_id,
            client=client,
        )
        access_token = aws.authenticate_user()["AuthenticationResult"]["AccessToken"]
        jwt_token = f"JWT {access_token}"
        return jwt_token

    def build_from_role(self, access_key, secret_key, region):
        url = f"{self.backend_url}/build_from_role"
        data = {
            "region": region,
            "access_key": access_key,
            "secret_key": secret_key,
            "include_inspector": False,
        }
        res = requests.put(url, headers=self.headers, json=data)
        res.raise_for_status()
        return res.json()["response"]["mtag"]

    def build_from_config(self, json_data):
        if isinstance(json_data, dict):
            content = json.dumps(json_data).encode("utf-8")
        elif isinstance(json_data, bytes):
            content = json_data
        else:
            raise ValueError(
                f"a bytes-like object or dict is required, not {type(json_data)}"
            )
        url = f"{self.backend_url}/build_from_config"
        base64d = base64.b64encode(content).decode("utf-8")
        data = {"files": [{"content": base64d, "filename": "apimodel.json"}]}
        res = requests.put(url, headers=self.headers, json=data)
        res.raise_for_status()
        return res.json()["response"]["mtag"]

    def model_request(self, model_tag):
        url = f"{self.backend_url}/get_model"
        data = {"mtag": model_tag}
        res = requests.post(url, headers=self.headers, json=data)
        res.raise_for_status()
        return res.status_code, res.json()["response"]

    def simulate_model(self, model, profile):
        url = f"{self.backend_url}/simulate"
        model["name"] = "vanguard_model"
        data = {"model": model, "profile": profile, "demo": False}
        res = requests.put(url, headers=self.headers, json=data)
        res.raise_for_status()
        return res.json()["response"]["tag"]

    def get_results(self, simulation_tag):
        url = f"{self.backend_url}/results"
        data = {"tag": simulation_tag}
        res = requests.post(url, headers=self.headers, json=data)
        res.raise_for_status()
        return res.status_code, res.json()["response"]

    def wait_for_results(self, simulation_tag):
        results = self.wait_for_response("get_results", simulation_tag)
        return results["results"]

    def wait_for_model(self, model_tag):
        return self.wait_for_response("model_request", model_tag)

    def parse_results(self, results, model):
        buckets = {}
        instances = {}
        dbinstances = {}
        for key, data in results["data"].items():
            obj_id = model.result_map[key]
            result = self.format_result(data)
            if data["metaconcept"] == "EC2Instance":
                instances[obj_id] = result
            if data["metaconcept"] == "DBInstance":
                dbinstances[obj_id] = result
            if data["metaconcept"] == "S3Bucket":
                buckets[obj_id] = result
        return {"instances": instances, "buckets": buckets, "dbinstances": dbinstances}

    def format_result(self, data):
        ttc50 = float(data["ttc50"])
        if ttc50 == sys.float_info.max:
            ttc50 = math.inf
        else:
            ttc50 = int(ttc50)
        prob = int(float(data["probability"]) * 100)
        result = {
            "probability": float(data["probability"]),
            "ttc": ttc50,
            "object_name": data["object_name"],
        }
        return result

    def wait_for_response(self, function, *args):
        status = 204
        while status == 204:
            time.sleep(5)
            status, data = getattr(self, function)(*args)
            if status == 200:
                return data

    def cognito_params(self, region):
        url = f"{self.base_url}/bundle.js"
        pattern = fr"{{\s*UserPoolId:\s*['\"]({region}[^'\"]+)['\"],\s*ClientId:\s*['\"]([^'\"]+)['\"]\s*}}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.text
        match = re.search(pattern, data)
        if match:
            userpool_id = str(match.group(1))
            client_id = str(match.group(2))
            return client_id, userpool_id
        raise EnvironmentError("Failed to get cognito parameters")
