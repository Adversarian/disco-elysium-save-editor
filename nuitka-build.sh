#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

cd "$repo_root"

uv run --group build python -m nuitka \
    --mode=onefile \
    --product-name="Disco Elysium Save Editor" \
    --product-version="1.1.0" \
    --file-description="Disco Elysium Save Editor" \
    --output-filename="DESE" \
    --output-dir="build" \
    --show-progress \
    --assume-yes-for-downloads \
    src/save_editor.py

printf '\nBuild complete! Check build/ for DESE.\n'
