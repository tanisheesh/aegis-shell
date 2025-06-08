#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the installer
pyinstaller \
    --name=AegisShell \
    --onefile \
    --windowed \
    --add-data="requirements.txt:." \
    --add-data="README.md:." \
    --add-data="LICENSE:." \
    --icon="assets/icon.icns" \
    installer.py

# Create release directory
mkdir -p release/mac

# Copy files
cp dist/AegisShell release/mac/
cp README.md release/mac/
cp LICENSE release/mac/

# Create zip file
cd release/mac
zip -r ../../AegisShell-Mac.zip *
cd ../..

echo "Mac package created: AegisShell-Mac.zip" 