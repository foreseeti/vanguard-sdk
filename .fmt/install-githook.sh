#!/bin/sh

set -e

cd "$(dirname "$0")"
fmt_dir="$PWD"
cd ..
cwd="$PWD"
hooks_dir="$cwd/.git/hooks"
fmt_venv="$fmt_dir/venv"

if [ ! -d "$hooks_dir" ]; then
  >&2 echo "$hooks_dir: No such directory"
  exit 1
fi

if [ ! -d "$fmt_venv" ]; then
  python3 -m venv "$fmt_venv"
fi

. "$fmt_venv/bin/activate"
pip install --upgrade pip
pip install --upgrade black
deactivate

cp "$fmt_dir/pre-commit" "$hooks_dir/pre-commit"
