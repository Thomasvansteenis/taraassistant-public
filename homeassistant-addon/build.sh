#!/bin/bash
# Prepare the add-on directory for building by copying application files
# from the repo root into the add-on build context.
#
# Usage: ./homeassistant-addon/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ADDON_DIR="$SCRIPT_DIR/tara-assistant"

echo "Preparing Tara Assistant add-on build context..."

# Copy application code
rm -rf "$ADDON_DIR/app"
cp -r "$REPO_ROOT/app" "$ADDON_DIR/app"

# Copy requirements
cp "$REPO_ROOT/requirements.txt" "$ADDON_DIR/requirements.txt"

# Copy scripts
cp "$REPO_ROOT/scripts.yaml" "$ADDON_DIR/scripts.yaml"

echo "Build context ready at: $ADDON_DIR"
echo ""
echo "To build locally:"
echo "  docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11 -t tara-assistant $ADDON_DIR"
echo ""
echo "For HA add-on installation, copy $ADDON_DIR to /addons/tara-assistant/ on your HA machine."
