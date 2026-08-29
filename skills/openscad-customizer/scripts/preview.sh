#!/usr/bin/env bash
# Compatibility shim: real implementation is preview.py (cross-platform).
exec python3 "$(dirname "$0")/preview.py" "$@"
