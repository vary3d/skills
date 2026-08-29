#!/usr/bin/env bash
# Compatibility shim: real implementation is cover.py (cross-platform).
exec python3 "$(dirname "$0")/cover.py" "$@"
