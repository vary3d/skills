#!/usr/bin/env bash
# Compatibility shim: real implementation is version-scad.py (cross-platform).
exec python3 "$(dirname "$0")/version-scad.py" "$@"
