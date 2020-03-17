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
        applied_instance_ids = []
        bucket_ids = kwargs.get("buckets", [])
        applied_bucket_ids = []
        dbinstance_ids = kwargs.get("dbinstances", [])
        applied_dbinstance_ids = []
        for index, obj in enumerate(self.model["objects"]):
            if obj["metaconcept"] == "EC2Instance":
                if self.high_value_instance(obj, index, instance_ids):
                    applied_instance_ids.append(self.get_tag(obj, "aws-id"))
            elif obj["metaconcept"] == "DBInstance":
                if self.high_value_dbinstance(obj, index, dbinstance_ids):
                    applied_dbinstance_ids.append(obj["name"])
            elif obj["metaconcept"] == "S3Bucket":
                if self.high_value_bucket(obj, index, bucket_ids):
                    applied_bucket_ids.append(obj["name"])
        for instance_id in instance_ids:
            if instance_id not in applied_instance_ids:
                raise ValueError(f"EC2Instance {instance_id}, can't set consequence")
        for dbinstance_id in dbinstance_ids:
            if dbinstance_id not in applied_dbinstance_ids:
                raise ValueError(f"Database instance {dbinstance_id}, can't set consequence")
        for bucket_id in bucket_ids:
            if bucket_id not in applied_bucket_ids:
                raise ValueError(f"Bucket {bucket_id}, can't set consequence")


    def high_value_instance(self, obj, index, instance_ids):
        attackstep = "HighPrivilegeAccess"
        instance_id = self.get_tag(obj, "aws-id")
        if instance_id in instance_ids:
            ev = self.evidence(attackstep)
            self.model["objects"][index]["attacksteps"] = ev
            self.result_map[self.result_key(obj, attackstep)] = instance_id
            return True
        return False

    def high_value_dbinstance(self, obj, index, dbinstances):
        attackstep = "ReadDatabase"
        if obj["name"] in dbinstances:
            ev = self.evidence(attackstep)
            self.model["objects"][index]["attacksteps"] = ev
            self.result_map[self.result_key(obj, attackstep)] = obj["name"]
            return True
        return False

    def high_value_bucket(self, obj, index, buckets):
        attackstep = "ReadObject"
        if obj["name"] in buckets:
            ev = self.evidence(attackstep)
            self.model["objects"][index]["attacksteps"] = ev
            self.result_map[self.result_key(obj, attackstep)] = obj["name"]
            return True
        return False

    def evidence(self, attackstep, evidence=10):
        evidence_dict = {
            attackstep: {
                "evidence": evidence,
                "name": attackstep,
                "distribution": "securiCAD default",
                "distribution_params": {},
            }
        }
        return evidence_dict

    def result_key(self, obj, attackstep):
        return f"{obj['id']}.{attackstep}"

    def get_tag(self, obj, key):
        tags = obj.get("tags")
        for tag in tags:
            if tag["key"] == key:
                return tag["value"]
