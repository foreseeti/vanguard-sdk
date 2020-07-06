#!/bin/bash

set -e

cd "$(dirname "$0")"

rm -rf tmp-venv
python3 -m venv tmp-venv
. tmp-venv/bin/activate
pip install --upgrade pip
pip install -r dependencies.txt
pip freeze | grep -v "pkg-resources" > requirements.txt
deactivate
rm -rf tmp-venv
