#!/bin/sh

set -eu

cd "$(dirname "$0")/../../.."

repo_dir="$PWD"
venv_dir="$repo_dir/venv"

echo_changed_py() {
  set +e
  git diff --cached --name-only --diff-filter=ACMR | grep "\.py$"
  set -e
}

create_venv() {
  if [ ! -d "$venv_dir" ]; then
    ./tools/scripts/create_venv.sh
  fi
  # shellcheck disable=SC1090
  . "$venv_dir/bin/activate"
}

format_python() {
  echo "Formatting $(echo "$changed_py" | wc -l) python files"
  echo "$changed_py" | tr "\n" "\0" | xargs -0 isort
  echo "$changed_py" | tr "\n" "\0" | xargs -0 black
  echo "$changed_py" | tr "\n" "\0" | xargs -0 git add -f
}

main() {
  changed_py="$(echo_changed_py)"
  if [ -z "$changed_py" ]; then
    exit
  fi
  create_venv
  format_python
}

main
