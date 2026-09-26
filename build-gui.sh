#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

cd "$repo_root"

uv run --group build python -m PyInstaller \
    --windowed \
    --name="DiscoElysiumSaveEditor" \
    --icon="$repo_root/assets/save.png" \
    --osx-bundle-identifier="com.keepp.discoelysiumsaveeditor" \
    --distpath="build" \
    --workpath="build/pyinstaller" \
    --specpath="build/pyinstaller" \
    --noconfirm \
    --clean \
    src/gui_editor.py

printf '\nBuild complete! Check build/DiscoElysiumSaveEditor.app.\n'
