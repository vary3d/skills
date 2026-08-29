"""Importable shim for find-openscad.py (hyphenated filename)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "find_openscad_impl", Path(__file__).resolve().parent / "find-openscad.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

find = _mod.find
candidates = _mod.candidates
is_exe = _mod.is_exe
