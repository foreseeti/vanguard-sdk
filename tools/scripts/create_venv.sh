#!/bin/sh

set -eu

cd "$(dirname "$0")/../.."

repo_dir="$PWD"
venv_dir="$repo_dir/venv"
reqs_file="$repo_dir/requirements.txt"
dev_reqs_file="$repo_dir/dev-requirements.txt"

create_venv() {
  echo "Creating virtual Python environment"
  rm -fR "$venv_dir"
  python3 -m venv "$venv_dir"
  # shellcheck disable=SC1090
  . "$venv_dir/bin/activate"
}

install_package() {
  echo "Installing $1"
  pip install --quiet --upgrade "$1"
}

sync_requirements() {
  echo "Synchronizing $reqs_file and $dev_reqs_file"
  pip-sync --quiet "$reqs_file" "$dev_reqs_file"
}

main() {
  create_venv
  install_package pip
  install_package setuptools
  install_package wheel
  install_package pip-tools
  sync_requirements
}

main
