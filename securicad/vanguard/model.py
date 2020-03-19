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


class Model:
    def __init__(self, model):
        self.model = model
        self.result_map = {}

    def set_high_value_assets(self, **kwargs):
        instance_ids = kwargs.get("instances", [])
        bucket_ids = kwargs.get("buckets", [])
        dbinstance_ids = kwargs.get("dbinstances", [])

        for index, obj in enumerate(self.model["objects"]):
            if obj["metaconcept"] == "EC2Instance":
                obj_id = self.get_tag(obj, "aws-id")
                attackstep = "HighPrivilegeAccess"
                self.set_high_value_asset(obj, obj_id, index, attackstep, instance_ids)

            elif obj["metaconcept"] == "DBInstance":
                obj_id = obj["name"]
                attackstep = "ReadDatabase"
                self.set_high_value_asset(obj, obj_id, index, attackstep, dbinstance_ids)

            elif obj["metaconcept"] == "S3Bucket":
                obj_id = obj["name"]
                attackstep = "ReadObject"
                self.set_high_value_asset(obj, obj_id, index, attackstep, bucket_ids)

        error_msg = "{} {} not found, can't set high value assets"
        if instance_ids:
            raise ValueError(error_msg.format("EC2 instances", instance_ids))
        if dbinstance_ids:
            raise ValueError(error_msg.format("RDS instances", dbinstance_ids))
        if bucket_ids:
            raise ValueError(error_msg.format("S3 buckets", bucket_ids))

    def set_high_value_asset(self, obj, identifier, index, attackstep, high_value_list):
        if identifier in high_value_list:
            self.model["objects"][index]["attacksteps"] = self.get_evidence(attackstep)
            self.result_map[f"{obj['id']}.{attackstep}"] = identifier
            high_value_list.remove(identifier)
            return True
        return False

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
