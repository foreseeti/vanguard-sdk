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


# Abstract vanguard exception, never raised
class VanguardException(Exception):
    pass


# Raised when authentication of username or password fails
class VanguardCredentialsError(VanguardException):
    pass


# Raised when authentication of AWS credentials fails
class AwsCredentialsError(VanguardException):
    pass


# Raised if the region is invalid
class AwsRegionError(VanguardException):
    pass


# Raised if no high value asset matches could be found
class HighValueAssetError(VanguardException):
    pass


# Raised if the user is ratelimited
class RateLimitError(VanguardException):
    pass
