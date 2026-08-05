#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
installer="$script_dir/install_skill.py"

if [ ! -f "$installer" ]; then
  echo "Missing sibling installer: $installer" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$installer" "$@"
fi

echo "Python 3 is required." >&2
exit 1
