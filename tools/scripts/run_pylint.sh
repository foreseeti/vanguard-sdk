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

create_fake_namespace() {
  site_packages="$(python -c "import site; print(site.getsitepackages()[0])")"
  touch securicad/__init__.py
  cp -fpR "$site_packages/securicad/model" securicad/model
}

delete_fake_namespace() {
  site_packages="$(python -c "import site; print(site.getsitepackages()[0])")"
  rm -f securicad/__init__.py
  rm -fR securicad/model
}

run_pylint() {
  delete_fake_namespace
  create_fake_namespace
  set +e
  pylint securicad.vanguard
  status=$?
  set -e
  delete_fake_namespace
  return $status
}

main() {
  create_venv
  run_pylint
}

main
