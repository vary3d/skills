#!/usr/bin/env bash
# Compatibility shim: real implementation is multi-preview.py (cross-platform).
exec python3 "$(dirname "$0")/multi-preview.py" "$@"
