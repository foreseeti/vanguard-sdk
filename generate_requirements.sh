#!/bin/bash

set -e

cd "$(dirname "$0")"

rm -rf requirements-venv
python3 -m venv requirements-venv
. requirements-venv/bin/activate
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade pip-tools
pip-compile --upgrade --no-emit-index-url --output-file requirements.txt requirements.in
deactivate
rm -rf requirements-venv
