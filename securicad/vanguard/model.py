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

from collections import defaultdict


class Model:
    def __init__(self, model):
        self.model = model
        self.result_map = {}

    def set_high_value_assets(self, **kwargs):
        hv_list = kwargs.get("high_value_assets", [])

        # Normalize high value assets from short-hand version
        for identifier in kwargs.get("instances", []):
            hv_list.append(
                {
                    "metaconcept": "EC2Instance",
                    "attackstep": "HighPrivilegeAccess",
                    "id": {"type": "tag", "key": "aws-id", "value": identifier},
                }
            )
        for identifier in kwargs.get("dbinstances", []):
            hv_list.append(
                {
                    "metaconcept": "DBInstance",
                    "attackstep": "ReadDatabase",
                    "id": {"type": "name", "value": identifier},
                }
            )
        for identifier in kwargs.get("buckets", []):
            hv_list.append(
                {
                    "metaconcept": "S3Bucket",
                    "attackstep": "ReadObject",
                    "id": {"type": "name", "value": identifier},
                }
            )
        for identifier in kwargs.get("dynamodb_tables", []):
            hv_list.append(
                {
                    "metaconcept": "DynamoDBTable",
                    "attackstep": "AuthenticatedRead",
                    "id": {"type": "name", "value": identifier},
                }
            )

        # Collect the high value assets under their metaconcept
        hv_assets = defaultdict(list)
        [hv_assets[x["metaconcept"]].append(x) for x in hv_list]

        # Check if any of the objects are eligable as a high value asset
        for index, obj in enumerate(self.model["objects"]):
            if obj["metaconcept"] in hv_assets:
                for hv_asset in hv_assets[obj["metaconcept"]]:
                    if self.is_high_value_asset(obj, hv_asset):
                        self.set_high_value_asset(obj, hv_asset, index)

        # Raise error if no high value asset matches were found
        if not self.result_map:
            raise ValueError(
                f"Failed to set any high value assets, couldn't find {hv_list}"
            )

    def is_high_value_asset(self, obj, hv_asset):
        # Check if a model object matches any of the high value assets
        if hv_asset["id"]["type"] == "name" and obj["name"] == hv_asset["id"]["value"]:
            return True
        elif hv_asset["id"]["type"] == "tag":
            if self.get_tag(obj, hv_asset["id"]["key"]) == hv_asset["id"]["value"]:
                return True
        elif hv_asset["id"]["type"] == "arn":
            if self.get_tag(obj, "arn") == hv_asset["id"]["value"]:
                return True
        return False

    def set_high_value_asset(self, obj, hv_asset, index):
        attackstep = hv_asset["attackstep"]
        self.model["objects"][index]["attacksteps"] = self.get_evidence(attackstep)
        self.result_map[f"{obj['id']}.{attackstep}"] = hv_asset

    def get_evidence(self, attackstep, evidence=10):
        evidence_dict = {
            attackstep: {
                "evidence": evidence,
                "name": attackstep,
                "distribution": "securiCAD default",
                "distribution_params": {},
            }
        }
        return evidence_dict

    def get_tag(self, obj, key):
        tags = obj.get("tags")
        for tag in tags:
            if tag["key"] == key:
                return tag["value"]
