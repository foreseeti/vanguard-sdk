# Copyright 2020-2021 Foreseeti AB <https://foreseeti.com>
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

import base64
import json
import math
import re
import sys
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import boto3
import botocore
import requests
from botocore.config import Config
from bs4 import BeautifulSoup
from pycognito.aws_srp import AWSSRP
from securicad.model import Model

from securicad.vanguard.exceptions import (
    AwsCredentialsError,
    AwsRegionError,
    RateLimitError,
    StatusCodeException,
    VanguardCredentialsError,
)

if TYPE_CHECKING:
    from securicad.vanguard import Profile


class Client:
    def __init__(
        self,
        username: str,
        password: str,
        url: str = "https://vanguard.securicad.com",
        region: str = "eu-central-1",
    ):
        self.__init_urls(url)
        self.__init_session()

        self.__login(username, password, region)

    def __init_urls(self, url: str) -> None:
        self._base_url = urljoin(url, "/")
        self._backend_url = urljoin(url, "/backend/")

    def __init_session(self) -> None:
        def get_user_agent():
            # pylint: disable=import-outside-toplevel
            import securicad.vanguard

            return f"Vanguard SDK {securicad.vanguard.__version__}"

        self._session = requests.Session()
        self._session.headers["User-Agent"] = get_user_agent()

    def _get_access_token(self) -> Optional[str]:
        if "Authorization" not in self._session.headers:
            return None
        return self._session.headers["Authorization"][len("JWT ") :]

    def _set_access_token(self, access_token: Optional[str]) -> None:
        if access_token is None:
            if "Authorization" in self._session.headers:
                del self._session.headers["Authorization"]
        else:
            self._session.headers["Authorization"] = f"JWT {access_token}"

    def __request(self, method: str, endpoint: str, data: Any, status_code: int) -> Any:
        url = urljoin(self._backend_url, endpoint)
        response = self._session.request(method, url, json=data)
        if response.status_code != status_code:
            raise StatusCodeException(status_code, method, url, response)
        return response.json()["response"]

    def _get(self, endpoint: str, data: Any = None, status_code: int = 200) -> Any:
        return self.__request("GET", endpoint, data, status_code)

    def _post(self, endpoint: str, data: Any = None, status_code: int = 200) -> Any:
        return self.__request("POST", endpoint, data, status_code)

    def _put(self, endpoint: str, data: Any = None, status_code: int = 200) -> Any:
        return self.__request("PUT", endpoint, data, status_code)

    def _delete(self, endpoint: str, data: Any = None, status_code: int = 200) -> Any:
        return self.__request("DELETE", endpoint, data, status_code)

    def __login(self, username: str, password: str, region: str) -> None:
        access_token = self.__authenticate(username, password, region)
        self._set_access_token(access_token)
        self._get("whoami")

    def __authenticate(self, username: str, password: str, region: str) -> str:
        def get_cognito_params() -> Tuple[str, str]:
            bundle = get_bundle()
            pattern = re.compile(
                fr"{{\s*UserPoolId:\s*['\"]({region}[^'\"]+)['\"],\s*ClientId:\s*['\"]([^'\"]+)['\"]\s*}}"
            )
            match = pattern.search(bundle)
            if match:
                userpool_id = str(match.group(1))
                client_id = str(match.group(2))
                return client_id, userpool_id
            raise EnvironmentError("Failed to get cognito parameters")

        def get_bundle() -> str:
            bundle_name = get_bundle_name()
            response = requests.get(urljoin(self._base_url, bundle_name))
            response.raise_for_status()
            return response.text

        def get_bundle_name() -> str:
            index_html = get_index_html()
            soup = BeautifulSoup(index_html, "html.parser")
            pattern = re.compile(r"/main\.[0-9a-f]+\.js")
            for tag in soup.find_all("script"):
                if "src" not in tag.attrs:
                    continue
                if pattern.fullmatch(tag["src"]) or tag["src"] == "/bundle.js":
                    return tag["src"]
            raise EnvironmentError("Failed to get bundle name")

        def get_index_html() -> str:
            response = requests.get(urljoin(self._base_url, "index.html"))
            response.raise_for_status()
            return response.text

        client = boto3.client(
            "cognito-idp",
            region_name=region,
            config=Config(signature_version=botocore.UNSIGNED),
        )
        client_id, pool_id = get_cognito_params()
        aws = AWSSRP(
            username=username,
            password=password,
            pool_id=pool_id,
            client_id=client_id,
            client=client,
        )
        try:
            access_token = aws.authenticate_user()["AuthenticationResult"][
                "AccessToken"
            ]
        except:
            raise VanguardCredentialsError("Invalid password or username")
        return access_token

    def get_model(
        self,
        *,
        data: Optional[Dict[str, Any]] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
        include_inspector: bool = False,
        vuln_data: Optional[Dict[str, Any]] = None,
    ) -> Model:
        try:
            if data is not None:
                model_tag = self.__build_from_config(data, vuln_data)
            elif (
                access_key is not None and secret_key is not None and region is not None
            ):
                model_tag = self.__build_from_role(
                    access_key, secret_key, region, include_inspector, vuln_data
                )
            else:
                raise ValueError(
                    "Either data or access_key, secret_key, and region must be specified"
                )
        except StatusCodeException as e:
            if e.status_code == 429:
                raise RateLimitError(
                    "You are currently ratelimited, please wait for other models to complete"
                )
            raise

        try:
            model = self.__wait_for_model(model_tag)
        except StatusCodeException as e:
            if e.status_code == 400:
                self.__raise_model_error(e)
            raise

        return Model(model)

    def __build_from_config(
        self, aws_data: Dict[str, Any], vuln_data: Optional[Dict[str, Any]]
    ) -> str:
        def get_file_content(dict_file: Dict[str, Any]) -> str:
            file_str = json.dumps(dict_file, allow_nan=False, indent=2)
            file_bytes = file_str.encode("utf-8")
            file_base64 = base64.b64encode(file_bytes).decode("utf-8")
            return file_base64

        def get_file(name: str, dict_file: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "filename": name,
                "content": get_file_content(dict_file),
            }

        data: Dict[str, Any] = {"files": [get_file("apimodel.json", aws_data)]}
        if vuln_data is not None:
            data["additionalFiles"] = [get_file("vulnerabilities.json", vuln_data)]
        response = self._put("build_from_config", data, 202)
        return response["mtag"]

    def __build_from_role(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        include_inspector: bool,
        vuln_data: Optional[Dict[str, Any]],
    ) -> str:
        def get_file_content(dict_file: Dict[str, Any]) -> str:
            file_str = json.dumps(dict_file, allow_nan=False, indent=2)
            file_bytes = file_str.encode("utf-8")
            file_base64 = base64.b64encode(file_bytes).decode("utf-8")
            return file_base64

        def get_file(name: str, dict_file: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "filename": name,
                "content": get_file_content(dict_file),
            }

        data: Dict[str, Any] = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "include_inspector": include_inspector,
        }
        if vuln_data is not None:
            data["additionalFiles"] = [get_file("vulnerabilities.json", vuln_data)]
        response = self._put("build_from_role", data, 202)
        return response["mtag"]

    def __wait_for_model(self, model_tag: str) -> Union[Dict[str, Any], str]:
        while True:
            try:
                return self._post("get_model", {"mtag": model_tag})
            except StatusCodeException as e:
                if e.status_code != 204:
                    raise
                time.sleep(5)

    def __raise_model_error(self, e: StatusCodeException) -> None:
        error_message = e.json["error"]

        # Credentials error 1
        expected_error_messages = [
            "Provided credentials were not accepted by AWS",
            "Your credentials does not give you the required access",
            "You don't have permission to perform a required action, please review the IAM policy",
        ]
        if error_message in expected_error_messages:
            raise AwsCredentialsError(error_message)

        # Credentials error 2
        expected_prefix = "You don't have permission to perform the required action: "
        expected_suffix = ", please review the IAM policy"
        if error_message.startswith(expected_prefix) and error_message.endswith(
            expected_suffix
        ):
            raise AwsCredentialsError(error_message)

        # Region error
        region_error = (
            "Error in retrieving or parsing info from AWS: No valid AWS region found"
        )
        if error_message == region_error:
            raise AwsRegionError(error_message)

        # pylint: disable=misplaced-bare-raise
        raise

    def set_high_value_assets(
        self,
        model: Model,
        instances: Optional[List[str]] = None,
        dbinstances: Optional[List[str]] = None,
        buckets: Optional[List[str]] = None,
        dynamodb_tables: Optional[List[str]] = None,
    ) -> None:
        high_value_assets = []

        if instances is not None:
            for identifier in instances:
                high_value_assets.append(
                    {
                        "metaconcept": "EC2Instance",
                        "attackstep": "HighPrivilegeAccess",
                        "id": {
                            "type": "tag",
                            "key": "aws-id",
                            "value": identifier,
                        },
                    }
                )

        if dbinstances is not None:
            for identifier in dbinstances:
                high_value_assets.append(
                    {
                        "metaconcept": "DBInstance",
                        "attackstep": "ReadDatabase",
                        "id": {
                            "type": "name",
                            "value": identifier,
                        },
                    }
                )

        if buckets is not None:
            for identifier in buckets:
                high_value_assets.append(
                    {
                        "metaconcept": "S3Bucket",
                        "attackstep": "ReadObject",
                        "id": {
                            "type": "name",
                            "value": identifier,
                        },
                    }
                )

        if dynamodb_tables is not None:
            for identifier in dynamodb_tables:
                high_value_assets.append(
                    {
                        "metaconcept": "DynamoDBTable",
                        "attackstep": "AuthenticatedRead",
                        "id": {
                            "type": "name",
                            "value": identifier,
                        },
                    }
                )

        model.set_high_value_assets(high_value_assets=high_value_assets)

    def simulate(
        self, model: Model, profile: "Profile", export_report: bool = False
    ) -> Dict[str, Any]:
        def has_high_value_asset(model: Model) -> bool:
            for obj in model.model["objects"].values():
                for step in obj["attacksteps"]:
                    if step["consequence"]:
                        return True
            return False

        if not has_high_value_asset(model):
            raise ValueError("Model must have at least one high value asset")

        try:
            simulation_tag = self.__simulate_model(model.model, profile.value)
        except StatusCodeException as e:
            if e.status_code == 429:
                raise RateLimitError(
                    "You are currently ratelimited, please wait for other simulations to complete"
                )
            raise

        results = self.__wait_for_results(simulation_tag)
        parsed_results = self.__parse_results(results)
        if export_report:
            parsed_results["Report"] = results
        return parsed_results

    def __simulate_model(self, model: Dict[str, Any], profile: str) -> str:
        model["name"] = "vanguard_model"
        data = {"model": model, "profile": profile, "demo": False}
        response = self._put("simulate", data)
        return response["tag"]

    def __wait_for_results(self, simulation_tag: str) -> Dict[str, Any]:
        while True:
            try:
                return self._post("results", {"tag": simulation_tag})
            except StatusCodeException as e:
                if e.status_code != 204:
                    raise
                time.sleep(5)

    def __parse_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        def get_key(data: Dict[str, Any]) -> str:
            object_id = int(data["object_id"])
            for obj in model["objects"].values():
                if obj["eid"] == object_id:
                    if "aws-id" in obj["tags"] and obj["tags"]["aws-id"]:
                        return str(obj["tags"]["aws-id"])
                    if obj["name"]:
                        return str(obj["name"])
                    if "Name" in obj["tags"] and obj["tags"]["Name"]:
                        return str(obj["tags"]["Name"])
                    return str(obj["eid"])
            return str(object_id)

        model = results["model_data"]
        parsed_results: Dict[str, Any] = {}
        for data in results["results"]["data"].values():
            metaconcept = data["metaconcept"]
            attackstep = data["attackstep"]
            object_name = data["object_name"]
            consequence = int(data["consequence"])
            probability = float(data["probability"])
            ttc50 = float(data["ttc50"])
            if ttc50 == sys.float_info.max:
                ttc50 = math.inf
            else:
                ttc50 = int(ttc50)

            result = {
                "metaconcept": metaconcept,
                "attackstep": attackstep,
                "name": object_name,
                "consequence": consequence,
                "probability": probability,
                "ttc": ttc50,
            }

            if metaconcept not in parsed_results:
                parsed_results[metaconcept] = {}
            parsed_results[metaconcept][get_key(data)] = result
        return parsed_results
