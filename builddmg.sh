#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/DeepDeck Installer" dist/dmg
# If the DMG already exists, delete it. 
test -f "dist/DeepDeck Installer.dmg" && rm "dist/DeepDeck Installer.dmg"
create-dmg \
  --volname "DeepDeck Installer" \
  --volicon "deepdeck.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "DeepDeck Installer" 175 120 \
  --hide-extension "DeepDeck Installer" \
  --app-drop-link 425 120 \
  "dist/DeepDeck Installer.dmg" \
  "dist/dmg/"