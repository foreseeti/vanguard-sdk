#!/bin/sh

set -eu

cd "$(dirname "$0")/../.."

repo_dir="$PWD"
venv_dir="$repo_dir/requirements-venv"
reqs_in="requirements.in"
reqs_out="requirements.txt"
dev_reqs_in="dev-requirements.in"
dev_reqs_out="dev-requirements.txt"

create_venv() {
  echo "Creating virtual Python environment"
  rm -fR "$venv_dir"
  python3 -m venv "$venv_dir"
  # shellcheck disable=SC1090
  . "$venv_dir/bin/activate"
}

delete_venv() {
  echo "Deleting virtual Python environment"
  deactivate
  rm -fR "$venv_dir"
}

install_package() {
  echo "Installing $1"
  pip install --quiet --upgrade "$1"
}

compile_requirements() {
  export CUSTOM_COMPILE_COMMAND="./tools/scripts/create_requirements.sh"

  echo "Compiling $reqs_out"
  rm -f "$reqs_out"
  pip-compile --quiet --upgrade --no-emit-index-url "$reqs_in"

  echo "Compiling $dev_reqs_out"
  rm -f "$dev_reqs_out"
  pip-compile --quiet --upgrade --no-emit-index-url "$dev_reqs_in"
}

main() {
  create_venv
  install_package pip
  install_package wheel
  install_package pip-tools
  compile_requirements
  delete_venv
}

main
