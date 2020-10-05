#!/bin/bash

set -eu -o pipefail

cd "$(dirname "$0")/../.."

hooks=(
  pre-commit
  prepare-commit-msg
  commit-msg
  post-commit
)

for hook in "${hooks[@]}"; do
  {
    echo "#!/bin/bash"
    echo
    echo "set -eu -o pipefail"
    echo
    echo "cd \"\$(dirname \"\$0\")/../..\""
    echo
    echo "hook=\"\$(basename \"\$0\")\""
    echo "hook_dir=\"tools/git-hooks/\$hook.d\""
    echo
    echo "if [ ! -d \"\$hook_dir\" ]; then"
    echo "  exit"
    echo "fi"
    echo
    echo "if ! compgen -G \"\$hook_dir/*.sh\" >/dev/null 2>&1; then"
    echo "  exit"
    echo "fi"
    echo
    echo "for script in \"\$hook_dir\"/*.sh; do"
    echo "  echo \"Running \$hook hook \$(basename \"\$script\")\""
    echo "  \"./\$script\" \"\$@\""
    echo "done"
  } > ".git/hooks/$hook"
  chmod a+x ".git/hooks/$hook"
done
