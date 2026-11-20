#!/bin/sh
set -eu

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
python="$project_dir/.venv/bin/python"

if [ ! -x "$python" ]; then
    printf '%s\n' '请先按 README.md 创建 .venv 并安装依赖。' >&2
    exit 1
fi

if [ -d "$project_dir/.venv/native-lib" ]; then
    export LD_LIBRARY_PATH="$project_dir/.venv/native-lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

export PYTHONPATH="$project_dir${PYTHONPATH:+:$PYTHONPATH}"
exec "$python" -m pdfreader "$@"
