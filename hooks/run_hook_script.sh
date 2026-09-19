#!/bin/sh
set -eu

script_name=${1:?Usage: run_hook_script.sh <python_script_name> [args...]}
shift

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$script_dir/$script_name" "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$script_dir/$script_name" "$@"
fi

echo "Hook dispatcher needs python3 or python in PATH." >&2
exit 1
