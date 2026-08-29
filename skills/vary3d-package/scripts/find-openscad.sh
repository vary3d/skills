#!/usr/bin/env bash
# Compatibility shim: real implementation is find-openscad.py (cross-platform).
exec python3 "$(dirname "$0")/find-openscad.py" "$@"
