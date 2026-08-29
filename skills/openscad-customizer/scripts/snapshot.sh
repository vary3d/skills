#!/usr/bin/env bash
# Compatibility shim: real implementation is snapshot.py (cross-platform).
exec python3 "$(dirname "$0")/snapshot.py" "$@"
