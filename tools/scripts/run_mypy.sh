#!/bin/sh

set -eu

cd "$(dirname "$0")/../.."

repo_dir="$PWD"
venv_dir="$repo_dir/venv"

create_venv() {
  if [ ! -d "$venv_dir" ]; then
    ./tools/scripts/create_venv.sh
  fi
  # shellcheck disable=SC1090
  . "$venv_dir/bin/activate"
}

run_mypy() {
  mypy --namespace-packages -p securicad.vanguard
}

main() {
  create_venv
  run_mypy
}

main
