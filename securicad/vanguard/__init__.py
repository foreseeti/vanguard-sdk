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

from securicad.vanguard.client import Client
from enum import Enum

__author__ = "Foreseeti AB"
__version__ = "0.0.1"


class Profile(Enum):
    STATESPONSORED = "State-sponsored"
    CYBERCRIMINAL = "Cybercriminal"
    OPPORTUNIST = "Opportunist"


def client(username, password, url="https://vanguard.securicad.com"):
    return Client(username, password, url)
