# Nuitka build script for Disco Elysium Save Editor (PyQt6 GUI)

nuitka `
    --standalone `
    --onefile `
    --enable-plugin=pyqt6 `
    --windows-disable-console `
    --windows-icon-from-ico="assets\save.png" `
    --include-data-dir="assets=assets" `
    --product-name="Disco Elysium Save Editor" `
    --product-version="1.0.0" `
    --file-version="1.0.0.0" `
    --file-description="Save editor for Disco Elysium with PyQt6 GUI" `
    --company-name="KeepP" `
    --copyright="MIT License" `
    --output-filename="DiscoElysiumSaveEditor" `
    --output-dir="build" `
    --show-progress `
    --assume-yes-for-downloads `
    .\src\gui_editor.py

Write-Host ""
Write-Host "Build complete! Check build/ directory for DiscoElysiumSaveEditor.exe" -ForegroundColor Green
