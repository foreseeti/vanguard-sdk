#!/bin/bash

set -eu -o pipefail

cd "$(dirname "$0")/.."

if [ ! -d venv ]; then
  python3 -m venv venv
fi

. venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet --upgrade wheel
pip install --quiet --upgrade black

cd ../..

set +e
changed_py="$(
  git diff --cached --name-only --diff-filter=ACMR |
  grep "\.py$"
)"
set -e

if [ -z "$changed_py" ]; then
  exit
fi

echo "$changed_py" | tr "\n" "\0" | xargs -0 black -t py38 -l 100
echo "$changed_py" | tr "\n" "\0" | xargs -0 git add
